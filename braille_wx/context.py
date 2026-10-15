"""سياق التطبيق لنسخة wxPython.

يفصل هذا الملف كل منطق الحالة عن الواجهة، ويعيد استخدام
``braille_go.core`` و``braille_go.data`` كما هي. يوفّر آلية إشارات بسيطة
(``Signal``) تُبقي الواجهة على علم بالتغييرات.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Callable

from braille_go.core.curriculum import (
    LEVELS,
    LESSONS_BY_KEY,
    Level,
    Lesson,
    all_lessons,
    first_lesson,
    level_of_lesson,
)
from braille_go.core.exercises import Exercise, ExerciseGenerator, Feedback, grade
from braille_go.core.progress import (
    DEFAULT_MASTERY_THRESHOLD,
    ProgressSnapshot,
    available_levels,
    evaluate_level,
    frequently_wrong_symbols,
    overall_progress,
)
from braille_go.core.symbols import SymbolRepository, build_default_repository
from braille_go.data.db import Database, DatabaseError
from braille_go.data.progress_store import ProgressStore
from braille_go.data.settings import Settings, SqliteSettingsBackend

from .sounds import SoundPlayer
from .speech import NullSpeechService, create_speech_service


class Signal:
    """إشارة بسيطة: قائمة دوال تُنادى عند الإطلاق."""

    def __init__(self) -> None:
        self._subscribers: list[Callable[..., None]] = []

    def connect(self, callback: Callable[..., None]) -> None:
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def disconnect(self, callback: Callable[..., None]) -> None:
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def emit(self, *args, **kwargs) -> None:
        for callback in list(self._subscribers):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass


class WxAppContext:
    """حالة التطبيق المشتركة بين كل الشاشات."""

    def __init__(
        self,
        database: Database,
        settings: Settings,
        progress: ProgressStore,
        repository: SymbolRepository,
    ) -> None:
        self.database = database
        self.settings = settings
        self.progress = progress
        self.repository = repository
        self.generator = ExerciseGenerator(repository, random.Random())
        self.speech = create_speech_service()
        self.sounds = SoundPlayer(enabled=bool(settings.get("sound_enabled", True)))

        #: تُطلق عند تغيّر الإعدادات.
        self.settings_changed = Signal()
        #: تُطلق عند تغيّر التقدّم.
        self.progress_changed = Signal()

        self._apply_settings_to_services()

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------
    def _apply_settings_to_services(self) -> None:
        self.speech.set_enabled(self.settings.speech_enabled)
        self.speech.set_rate(self.settings.get("speech_rate", 0.0))
        self.speech.set_volume(self.settings.get("volume", 1.0))
        self.speech.set_voice_name(self.settings.get("speech_voice", ""))
        self.speech.set_language(self.settings.get("speech_locale", ""))
        self.sounds.enabled = bool(self.settings.get("sound_enabled", True))

    def apply_settings(self) -> None:
        """أعِد تطبيق الإعدادات على الخدمات ثم أبلغ الواجهة."""
        self._apply_settings_to_services()
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
        recent = [k for k in self.progress.recent_wrong_symbols(limit) if k in self.repository]
        if recent:
            return recent
        # لا توجد أخطاء مسجّلة بعد: نراجع رموز أول درس يحتوي على رموز فعلية.
        for lesson in all_lessons():
            if lesson.symbol_keys:
                return list(lesson.symbol_keys)[:limit]
        return []

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
        except Exception:
            pass
        try:
            self.settings.save()
        except Exception:
            pass
        self.database.close()


def build_context(data_dir: str | Path | None = None) -> WxAppContext:
    """أنشئ سياق التطبيق كاملًا مع معالجة أخطاء قاعدة البيانات."""
    database = Database(Path(data_dir) / "braille_go.sqlite3" if data_dir else None)
    try:
        database.connect()
        database.initialize()
    except DatabaseError:
        database.close()
        database = Database(Path(data_dir) / "braille_go.sqlite3" if data_dir else None)
        database.connect()
        database.initialize()

    settings = Settings(SqliteSettingsBackend(database))
    progress = ProgressStore(database)
    repository = build_default_repository()
    _ensure_extra_tables(database)
    return WxAppContext(database, settings, progress, repository)


def _ensure_extra_tables(database: Database) -> None:
    """أنشئ جدول المستخدمين إن لم يكن موجودًا (يستخدمه وضع المدرب)."""
    try:
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                role       TEXT NOT NULL DEFAULT 'student',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
    except Exception:
        pass


__all__ = ["WxAppContext", "build_context", "Signal"]
