"""سياق التطبيق: يربط قاعدة البيانات والإعدادات والتقدّم والصوت والتدريبات.

``AppContext`` is the single object the UI talks to.  It owns the long-lived
services, exposes convenience queries, and emits Qt signals when the settings
or the learner's progress change so that every screen can refresh itself.
"""

from __future__ import annotations

import random
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from .core.curriculum import (
    LEVELS,
    LESSONS_BY_KEY,
    Level,
    Lesson,
    all_lessons,
    first_lesson,
    level_of_lesson,
)
from .core.exercises import Exercise, ExerciseGenerator, Feedback, grade
from .core.progress import (
    DEFAULT_MASTERY_THRESHOLD,
    ProgressSnapshot,
    available_levels,
    evaluate_level,
    frequently_wrong_symbols,
    overall_progress,
)
from .core.symbols import SymbolRepository, build_default_repository
from .data.db import Database, DatabaseError, default_data_dir
from .data.progress_store import ProgressStore
from .data.settings import Settings, SqliteSettingsBackend
from .services.speech import NullSpeechService, SpeechService, create_speech_service


class AppContext(QObject):
    """حالة التطبيق المشتركة."""

    settings_changed = Signal()
    progress_changed = Signal()

    def __init__(
        self,
        database: Database,
        settings: Settings,
        progress: ProgressStore,
        repository: SymbolRepository,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.database = database
        self.settings = settings
        self.progress = progress
        self.repository = repository
        self.generator = ExerciseGenerator(repository, random.Random())
        self.speech = create_speech_service(self)
        self._apply_speech_settings()

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------
    def _apply_speech_settings(self) -> None:
        self.speech.set_enabled(self.settings.speech_enabled)
        self.speech.set_rate(self.settings.get("speech_rate", 0.0))
        self.speech.set_volume(self.settings.get("volume", 1.0))
        self.speech.set_voice_name(self.settings.get("speech_voice", ""))
        self.speech.set_language(self.settings.get("speech_locale", ""))

    def apply_settings(self) -> None:
        """أعِد تطبيق الإعدادات على الخدمات ثم أبلغ الواجهة."""
        self._apply_speech_settings()
        self.settings_changed.emit()

    def reset_settings(self) -> None:
        self.settings.reset()
        self.apply_settings()

    @property
    def mastery_threshold(self) -> float:
        return float(self.settings.get("mastery_threshold", DEFAULT_MASTERY_THRESHOLD))

    # ------------------------------------------------------------------
    # Progress
    # ------------------------------------------------------------------
    def snapshot(self) -> ProgressSnapshot:
        level_key, lesson_key = self.progress.current_position()
        return ProgressSnapshot(
            results=self.progress.all_lesson_results(),
            symbol_stats=self.progress.all_symbol_stats(),
            current_level_key=level_key,
            current_lesson_key=lesson_key,
        )

    def evaluate(self, level: Level):
        return evaluate_level(level, self.progress.all_lesson_results(), self.mastery_threshold)

    def unlocked_level_keys(self) -> set[str]:
        return available_levels(LEVELS, self.progress.all_lesson_results(), self.mastery_threshold)

    def is_level_unlocked(self, level_key: str) -> bool:
        return level_key in self.unlocked_level_keys()

    def overall_progress_percent(self) -> float:
        return overall_progress(all_lessons(), self.progress.all_lesson_results(), self.mastery_threshold)

    def needs_review_symbols(self, limit: int = 12) -> list[str]:
        stats = self.progress.all_symbol_stats()
        stats_flagged = frequently_wrong_symbols(stats, limit=limit)
        keys = [stat.symbol_key for stat in stats_flagged]
        if keys:
            return keys
        return [k for k in self.progress.recent_wrong_symbols(limit) if k in self.repository]

    # ------------------------------------------------------------------
    # Lessons / exercises
    # ------------------------------------------------------------------
    def lesson(self, lesson_key: str) -> Lesson | None:
        return LESSONS_BY_KEY.get(lesson_key)

    def level_for_lesson(self, lesson_key: str) -> Level | None:
        return level_of_lesson(lesson_key)

    def last_lesson(self) -> Lesson:
        _, lesson_key = self.progress.current_position()
        lesson = LESSONS_BY_KEY.get(lesson_key)
        if lesson is None:
            return first_lesson()
        # لا تُرجِع درسًا مقفلًا.
        level = level_of_lesson(lesson.key)
        if level is not None and not self.is_level_unlocked(level.key):
            return first_lesson()
        return lesson

    def generate_exercises(self, lesson: Lesson, count: int | None = None) -> list[Exercise]:
        return self.generator.generate_lesson(lesson, count=count)

    def generate_review(self, count: int = 8) -> list[Exercise]:
        keys = self.needs_review_symbols(limit=12)
        if not keys:
            return []
        return self.generator.generate_review("review_session", keys, count=count)

    def grade(self, exercise: Exercise, response: object) -> Feedback:
        return grade(exercise, response, self.repository)

    def save_session(
        self,
        lesson: Lesson,
        level_key: str,
        results: list[tuple[Exercise, Feedback]],
    ) -> None:
        self.progress.save_session(lesson, level_key, results, self.mastery_threshold)
        self.progress_changed.emit()

    def set_current_position(self, level_key: str, lesson_key: str) -> None:
        self.progress.set_current(level_key, lesson_key)
        self.settings.set("last_level_key", level_key)
        self.settings.set("last_lesson_key", lesson_key)

    # ------------------------------------------------------------------
    # Speech
    # ------------------------------------------------------------------
    def speak(self, text: str, language: str | None = None) -> None:
        if not text:
            return
        self.speech.say(text, language)

    def speak_guidance(self, text: str, language: str | None = None) -> None:
        if self.settings.get("guidance_enabled", True) and self.settings.speech_enabled:
            self.speak(text, language)

    def speech_status(self) -> str:
        return self.speech.status_text()

    @property
    def speech_available(self) -> bool:
        return bool(getattr(self.speech, "available", False)) and not isinstance(
            self.speech, NullSpeechService
        )

    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        """إغلاق نظيف: إيقاف النطق ودمج سجل قاعدة البيانات."""
        try:
            self.speech.stop()
        except Exception:  # pragma: no cover
            pass
        try:
            self.settings.save()
        except Exception:  # pragma: no cover
            pass
        self.database.close()


def build_context(data_dir: str | Path | None = None) -> AppContext:
    """أنشئ سياق التطبيق كاملًا مع معالجة أخطاء قاعدة البيانات."""
    database = Database(Path(data_dir) / "braille_go.sqlite3" if data_dir else None)
    try:
        database.connect()
        database.initialize()
    except DatabaseError:
        # محاولة أخيرة: أعِد المحاولة بعد إزاحة القاعدة التالفة (يتكفّل بها connect).
        database.close()
        database = Database(Path(data_dir) / "braille_go.sqlite3" if data_dir else None)
        database.connect()
        database.initialize()

    settings = Settings(SqliteSettingsBackend(database))
    progress = ProgressStore(database)
    repository = build_default_repository()
    return AppContext(database, settings, progress, repository)


__all__ = ["AppContext", "build_context", "default_data_dir"]
