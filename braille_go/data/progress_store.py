"""حفظ واستعادة تقدّم المتعلّم في قاعدة البيانات المحلية.

The store writes a whole practice session inside a single transaction, so the
learner's progress is never left half-written if the application is closed
unexpectedly.  It exposes plain data objects from
:mod:`braille_go.core.progress`, which the UI and the rules engine then use.
"""

from __future__ import annotations

from typing import Sequence

from ..core.curriculum import Lesson
from ..core.exercises import Exercise, Feedback
from ..core.progress import (
    DEFAULT_MASTERY_THRESHOLD,
    LessonResult,
    SymbolStat,
)
from .db import Database, utc_now


class ProgressStore:
    """واجهة قراءة/كتابة بيانات التقدّم."""

    def __init__(self, database: Database) -> None:
        self._db = database

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------
    def save_session(
        self,
        lesson: Lesson,
        level_key: str,
        results: Sequence[tuple[Exercise, Feedback]],
        threshold: float = DEFAULT_MASTERY_THRESHOLD,
    ) -> LessonResult:
        """سجّل جلسة تدريب كاملة (أسئلة + نتائج) ثم أعِد ملخّص الدرس."""
        if not results:
            return self.lesson_result(lesson.key) or LessonResult(
                lesson_key=lesson.key, level_key=level_key
            )

        correct_count = sum(1 for _, feedback in results if feedback.correct)
        total = len(results)
        score = round(correct_count / total * 100.0, 2) if total else 0.0
        completed = score >= threshold
        now = utc_now()

        with self._db.transaction() as conn:
            for exercise, feedback in results:
                conn.execute(
                    "INSERT INTO exercise_results("
                    "exercise_key, lesson_key, level_key, kind, language, "
                    "symbol_keys, is_correct, given, expected, created_at"
                    ") VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        exercise.key,
                        lesson.key,
                        level_key,
                        exercise.kind.value,
                        exercise.language,
                        ",".join(exercise.symbol_keys),
                        1 if feedback.correct else 0,
                        str(feedback.given)[:500],
                        str(feedback.expected)[:500],
                        now,
                    ),
                )
                for symbol_key in exercise.symbol_keys:
                    conn.execute(
                        "INSERT INTO symbol_stats(symbol_key, attempts, correct, updated_at) "
                        "VALUES(?, 1, ?, ?) "
                        "ON CONFLICT(symbol_key) DO UPDATE SET "
                        "  attempts = attempts + 1, "
                        "  correct = correct + excluded.correct, "
                        "  updated_at = excluded.updated_at",
                        (symbol_key, 1 if feedback.correct else 0, now),
                    )

            conn.execute(
                """
                INSERT INTO lesson_progress(
                    lesson_key, level_key, attempts, best_score, last_score,
                    correct_total, answered_total, completed, completed_at, updated_at
                ) VALUES(?,?,1,?,?,?,?,?,?,?)
                ON CONFLICT(lesson_key) DO UPDATE SET
                    level_key     = excluded.level_key,
                    attempts      = lesson_progress.attempts + 1,
                    last_score    = excluded.last_score,
                    best_score    = MAX(lesson_progress.best_score, excluded.best_score),
                    correct_total = lesson_progress.correct_total + excluded.correct_total,
                    answered_total = lesson_progress.answered_total + excluded.answered_total,
                    completed     = MAX(lesson_progress.completed, excluded.completed),
                    completed_at  = CASE
                        WHEN lesson_progress.completed = 1 THEN lesson_progress.completed_at
                        ELSE excluded.completed_at END,
                    updated_at    = excluded.updated_at
                """,
                (
                    lesson.key,
                    level_key,
                    score,
                    score,
                    correct_count,
                    total,
                    1 if completed else 0,
                    now if completed else None,
                    now,
                ),
            )
            conn.execute(
                "INSERT INTO app_state(key, value, updated_at) VALUES('last_lesson_key', ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
                (lesson.key, now),
            )
            conn.execute(
                "INSERT INTO app_state(key, value, updated_at) VALUES('last_level_key', ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
                (level_key, now),
            )

        return self.lesson_result(lesson.key) or LessonResult(
            lesson_key=lesson.key, level_key=level_key,
        )

    def record_answer(
        self,
        exercise: Exercise,
        feedback: Feedback,
        level_key: str,
        lesson_key: str,
    ) -> None:
        """سجّل إجابة سؤال واحد فورًا.

        الحفظ التدريجي داخل معاملة واحدة يضمن ألا يفقد المتعلّم تقدّمه إذا
        أُغلق التطبيق بصورة غير متوقعة في منتصف الجلسة.
        """
        now = utc_now()
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT INTO exercise_results("
                "exercise_key, lesson_key, level_key, kind, language, "
                "symbol_keys, is_correct, given, expected, created_at"
                ") VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    exercise.key,
                    lesson_key,
                    level_key,
                    exercise.kind.value,
                    exercise.language,
                    ",".join(exercise.symbol_keys),
                    1 if feedback.correct else 0,
                    str(feedback.given)[:500],
                    str(feedback.expected)[:500],
                    now,
                ),
            )
            for symbol_key in exercise.symbol_keys:
                conn.execute(
                    "INSERT INTO symbol_stats(symbol_key, attempts, correct, updated_at) "
                    "VALUES(?, 1, ?, ?) "
                    "ON CONFLICT(symbol_key) DO UPDATE SET "
                    "  attempts = attempts + 1, "
                    "  correct = correct + excluded.correct, "
                    "  updated_at = excluded.updated_at",
                    (symbol_key, 1 if feedback.correct else 0, now),
                )

    def finalize_session(
        self,
        lesson: Lesson,
        level_key: str,
        correct: int,
        total: int,
        threshold: float = DEFAULT_MASTERY_THRESHOLD,
    ) -> LessonResult:
        """أغلق جلسة درس: حدّث ملخّص الدرس ونقطة الاستكمال.

        تُستدعى مرّة واحدة في نهاية الجلسة، بعد أن تكون كل إجابة قد حُفظت
        على حِدة عبر :meth:`record_answer`.
        """
        total = max(0, int(total))
        score = round(correct / total * 100.0, 2) if total else 0.0
        completed = total > 0 and score >= threshold
        now = utc_now()
        with self._db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO lesson_progress(
                    lesson_key, level_key, attempts, best_score, last_score,
                    correct_total, answered_total, completed, completed_at, updated_at
                ) VALUES(?,?,1,?,?,?,?,?,?,?)
                ON CONFLICT(lesson_key) DO UPDATE SET
                    level_key      = excluded.level_key,
                    attempts       = lesson_progress.attempts + 1,
                    last_score     = excluded.last_score,
                    best_score     = MAX(lesson_progress.best_score, excluded.best_score),
                    correct_total  = lesson_progress.correct_total + excluded.correct_total,
                    answered_total = lesson_progress.answered_total + excluded.answered_total,
                    completed      = MAX(lesson_progress.completed, excluded.completed),
                    completed_at   = CASE
                        WHEN lesson_progress.completed = 1 THEN lesson_progress.completed_at
                        ELSE excluded.completed_at END,
                    updated_at     = excluded.updated_at
                """,
                (
                    lesson.key,
                    level_key,
                    score,
                    score,
                    correct,
                    total,
                    1 if completed else 0,
                    now if completed else None,
                    now,
                ),
            )
            for key, value in (
                ("last_lesson_key", lesson.key),
                ("last_level_key", level_key),
                ("current_lesson_key", lesson.key),
                ("current_level_key", level_key),
            ):
                conn.execute(
                    "INSERT INTO app_state(key, value, updated_at) VALUES(?, ?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value, "
                    "updated_at = excluded.updated_at",
                    (key, value, now),
                )
        return self.lesson_result(lesson.key) or LessonResult(
            lesson_key=lesson.key, level_key=level_key
        )

    def set_current(self, level_key: str, lesson_key: str) -> None:
        """احفظ نقطة الاستكمال الحالية."""
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT INTO app_state(key, value, updated_at) VALUES('current_level_key', ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
                (level_key, utc_now()),
            )
            conn.execute(
                "INSERT INTO app_state(key, value, updated_at) VALUES('current_lesson_key', ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
                (lesson_key, utc_now()),
            )

    def reset_all(self) -> None:
        """امسح كل بيانات التقدّم (مع الاحتفاظ بالإعدادات)."""
        with self._db.transaction() as conn:
            conn.execute("DELETE FROM exercise_results")
            conn.execute("DELETE FROM lesson_progress")
            conn.execute("DELETE FROM symbol_stats")
            conn.execute("DELETE FROM app_state")

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------
    def lesson_result(self, lesson_key: str) -> LessonResult | None:
        row = self._db.query_one(
            "SELECT * FROM lesson_progress WHERE lesson_key = ?", (lesson_key,)
        )
        return _row_to_lesson_result(row) if row else None

    def all_lesson_results(self) -> dict[str, LessonResult]:
        rows = self._db.query("SELECT * FROM lesson_progress")
        return {row["lesson_key"]: _row_to_lesson_result(row) for row in rows}

    def all_symbol_stats(self) -> dict[str, SymbolStat]:
        rows = self._db.query("SELECT symbol_key, attempts, correct FROM symbol_stats")
        return {
            row["symbol_key"]: SymbolStat(
                symbol_key=row["symbol_key"],
                attempts=row["attempts"] or 0,
                correct=row["correct"] or 0,
            )
            for row in rows
        }

    def symbol_stat(self, symbol_key: str) -> SymbolStat:
        row = self._db.query_one(
            "SELECT symbol_key, attempts, correct FROM symbol_stats WHERE symbol_key = ?",
            (symbol_key,),
        )
        if not row:
            return SymbolStat(symbol_key=symbol_key)
        return SymbolStat(symbol_key=row["symbol_key"], attempts=row["attempts"], correct=row["correct"])

    def current_position(self) -> tuple[str, str]:
        """أعد ``(level_key, lesson_key)`` لآخر نقطة وصل إليها المتعلّم."""
        level = self._db.get_state("current_level_key", "") or ""
        lesson = self._db.get_state("current_lesson_key", "") or ""
        if not lesson:
            lesson = self._db.get_state("last_lesson_key", "") or ""
        return level, lesson

    def recent_wrong_symbols(self, limit: int = 12) -> list[str]:
        """مفاتيح الرموز الأكثر تكرارًا في الخطأ."""
        rows = self._db.query(
            """
            SELECT symbol_keys, COUNT(*) AS mistakes
            FROM exercise_results
            WHERE is_correct = 0 AND symbol_keys <> ''
            GROUP BY symbol_keys
            ORDER BY mistakes DESC
            LIMIT ?
            """,
            (limit,),
        )
        ordered: list[str] = []
        for row in rows:
            for key in str(row["symbol_keys"]).split(","):
                key = key.strip()
                if key and key not in ordered:
                    ordered.append(key)
        return ordered

    def wrong_answers(self, limit: int = 50) -> list[dict[str, object]]:
        """قائمة الأخطاء السابقة لعرضها في شاشة المراجعة."""
        rows = self._db.query(
            """
            SELECT exercise_key, lesson_key, kind, symbol_keys, given, expected, created_at
            FROM exercise_results
            WHERE is_correct = 0
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in rows]

    def statistics(self) -> dict[str, float | int]:
        """إحصاءات عامة للعرض في شاشة التقدّم."""
        totals = self._db.query_one(
            "SELECT COUNT(*) AS total, SUM(is_correct) AS correct FROM exercise_results"
        )
        total = int(totals["total"] or 0) if totals else 0
        correct = int(totals["correct"] or 0) if totals else 0
        lessons = self._db.query_one("SELECT COUNT(*) AS n FROM lesson_progress")
        completed = self._db.query_one(
            "SELECT COUNT(*) AS n FROM lesson_progress WHERE completed = 1"
        )
        return {
            "answers_total": total,
            "answers_correct": correct,
            "accuracy": (correct / total * 100.0) if total else 0.0,
            "lessons_attempted": int(lessons["n"] or 0) if lessons else 0,
            "lessons_completed": int(completed["n"] or 0) if completed else 0,
        }

    def export_error_pairs(self) -> list[dict[str, str]]:
        """أزواج (المتوقع، ما أجاب به المتعلّم) الأكثر تكرارًا لدرس المراجعة."""
        rows = self._db.query(
            """
            SELECT expected, given, COUNT(*) AS n
            FROM exercise_results
            WHERE is_correct = 0 AND expected <> ''
            GROUP BY expected, given
            ORDER BY n DESC
            LIMIT 30
            """
        )
        return [{"expected": r["expected"], "given": r["given"], "count": str(r["n"])} for r in rows]


def _row_to_lesson_result(row) -> LessonResult:
    return LessonResult(
        lesson_key=row["lesson_key"],
        level_key=row["level_key"],
        attempts=row["attempts"] or 0,
        best_score=float(row["best_score"] or 0.0),
        last_score=float(row["last_score"] or 0.0),
        correct_total=int(row["correct_total"] or 0),
        answered_total=int(row["answered_total"] or 0),
        completed=bool(row["completed"]),
        completed_at=row["completed_at"],
    )
