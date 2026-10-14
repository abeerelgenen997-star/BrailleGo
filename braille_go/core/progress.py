"""قواعد التقدّم وإتقان المستويات (منطق خالص بدون قاعدة بيانات).

Everything here is a pure function of the recorded results, which keeps the
"rules of the game" easy to reason about and easy to unit test:

* a lesson is **completed** when its best score reaches the mastery threshold;
* a level is **mastered** when *every* lesson of the level is completed and the
  overall accuracy of the level reaches the threshold;
* moving to the next level requires mastery of the current one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

from .curriculum import Lesson, Level

#: النسبة الافتراضية المطلوبة للانتقال بين المستويات.
DEFAULT_MASTERY_THRESHOLD = 85.0

#: أقل عدد محاولات قبل اعتبار رمز ما «يحتاج مراجعة».
REVIEW_MIN_ATTEMPTS = 3

#: دقّة أقل من هذه القيمة تُعتبر خطأً متكررًا.
REVIEW_ACCURACY_THRESHOLD = 70.0


def clamp_percentage(value: float) -> float:
    """حصر النسبة بين 0 و100."""
    return max(0.0, min(100.0, float(value)))


def compute_accuracy(correct: int, total: int) -> float:
    """حساب النسبة المئوية للإجابات الصحيحة."""
    if total <= 0:
        return 0.0
    return clamp_percentage(correct / total * 100.0)


@dataclass
class LessonResult:
    """ملخّص نتائج درس واحد."""

    lesson_key: str
    level_key: str
    attempts: int = 0
    best_score: float = 0.0
    last_score: float = 0.0
    correct_total: int = 0
    answered_total: int = 0
    completed: bool = False
    completed_at: str | None = None

    @property
    def accuracy(self) -> float:
        return compute_accuracy(self.correct_total, self.answered_total)


@dataclass
class SymbolStat:
    """إحصاء محاولات رمز واحد."""

    symbol_key: str
    attempts: int = 0
    correct: int = 0

    @property
    def accuracy(self) -> float:
        return compute_accuracy(self.correct, self.attempts)

    @property
    def needs_review(self) -> bool:
        return self.attempts >= REVIEW_MIN_ATTEMPTS and self.accuracy < REVIEW_ACCURACY_THRESHOLD


@dataclass
class LevelEvaluation:
    """نتيجة تقييم مستوى واحد."""

    level_key: str
    level_number: int
    mastery: float = 0.0
    passed: bool = False
    lessons_total: int = 0
    lessons_attempted: int = 0
    lessons_completed: int = 0
    missing_lessons: tuple[str, ...] = ()
    reason_ar: str = ""
    exam_score: float | None = None
    threshold: float = DEFAULT_MASTERY_THRESHOLD

    @property
    def progress_percent(self) -> float:
        """نسبة إنجاز المستوى وفق عدد الدروس المكتملة."""
        if self.lessons_total <= 0:
            return 100.0 if self.passed else 0.0
        return clamp_percentage(self.lessons_completed / self.lessons_total * 100.0)


@dataclass
class ProgressSnapshot:
    """صورة كاملة لتقدّم المتعلّم."""

    results: Mapping[str, LessonResult] = field(default_factory=dict)
    symbol_stats: Mapping[str, SymbolStat] = field(default_factory=dict)
    current_level_key: str = ""
    current_lesson_key: str = ""

    def lesson_result(self, lesson_key: str) -> LessonResult:
        return self.results.get(lesson_key) or LessonResult(lesson_key=lesson_key, level_key="")

    def symbol_stat(self, symbol_key: str) -> SymbolStat:
        return self.symbol_stats.get(symbol_key) or SymbolStat(symbol_key=symbol_key)


# ----------------------------------------------------------------------
def evaluate_level(
    level: Level,
    results: Mapping[str, LessonResult],
    threshold: float = DEFAULT_MASTERY_THRESHOLD,
) -> LevelEvaluation:
    """قيّم مستوى كاملًا وفق النتائج المسجّلة.

    يعيد :class:`LevelEvaluation` يوضّح هل اجتاز المتعلّم المستوى، ونسبة
    الإتقان، والدروس الناقصة، وسبب عدم الاجتياز بصيغة عربية واضحة.
    """
    evaluation = LevelEvaluation(
        level_key=level.key,
        level_number=level.number,
        threshold=threshold,
        lessons_total=len(level.lessons),
    )
    if not level.lessons:
        evaluation.passed = True
        evaluation.mastery = 100.0
        evaluation.reason_ar = "لا توجد دروس في هذا المستوى."
        return evaluation

    scores: list[float] = []
    missing: list[str] = []
    attempted = 0
    completed = 0

    for lesson in level.lessons:
        result = results.get(lesson.key)
        if result is None or result.attempts <= 0:
            missing.append(lesson.key)
            scores.append(0.0)
            continue
        attempted += 1
        scores.append(result.best_score)
        if result.completed or result.best_score >= threshold:
            completed += 1
        else:
            missing.append(lesson.key)

    evaluation.lessons_attempted = attempted
    evaluation.lessons_completed = completed
    evaluation.missing_lessons = tuple(missing)
    evaluation.mastery = clamp_percentage(sum(scores) / len(scores))

    exam_lessons = [lesson for lesson in level.lessons if lesson.is_exam]
    if exam_lessons:
        exam_scores = [results[l.key].best_score for l in exam_lessons if l.key in results]
        evaluation.exam_score = clamp_percentage(sum(exam_scores) / len(exam_scores)) if exam_scores else 0.0

    problems: list[str] = []
    if missing:
        titles = ", ".join(_lesson_title(level, key) for key in missing)
        problems.append(f"يجب إكمال الدروس التالية: {titles}")
    if evaluation.mastery < threshold:
        problems.append(
            f"نسبة الإتقان الحالية {evaluation.mastery:.0f}% والمطلوب {threshold:.0f}%"
        )
    if exam_lessons and (evaluation.exam_score or 0.0) < threshold:
        problems.append(
            f"درجة الاختبار {evaluation.exam_score or 0.0:.0f}% والمطلوب {threshold:.0f}%"
        )

    evaluation.passed = not problems
    evaluation.reason_ar = (
        "أتممت هذا المستوى بنجاح." if evaluation.passed else "؛ ".join(problems) + "."
    )
    return evaluation


def _lesson_title(level: Level, lesson_key: str) -> str:
    lesson = level.lesson(lesson_key)
    return lesson.title_ar if lesson else lesson_key


def can_advance(
    level: Level,
    results: Mapping[str, LessonResult],
    threshold: float = DEFAULT_MASTERY_THRESHOLD,
) -> tuple[bool, str]:
    """هل يمكن الانتقال من المستوى المحدّد إلى ما بعده؟"""
    evaluation = evaluate_level(level, results, threshold)
    return evaluation.passed, evaluation.reason_ar


def next_level_after(current_number: int, levels: Iterable[Level]) -> Level | None:
    """المستوى التالي في الترتيب."""
    ordered = sorted(levels, key=lambda lv: lv.number)
    for level in ordered:
        if level.number > current_number:
            return level
    return None


def available_levels(levels: Iterable[Level], results: Mapping[str, LessonResult],
                     threshold: float = DEFAULT_MASTERY_THRESHOLD) -> set[str]:
    """المستويات المتاحة للفتح (المستوى الأول + ما أُتقن ما قبله).

    الإتقان يفتح التالي؛ وهذا يضمن عدم تجاوز المستويات دون استحقاق.
    """
    ordered = sorted(levels, key=lambda lv: lv.number)
    unlocked: set[str] = set()
    for index, level in enumerate(ordered):
        if index == 0:
            unlocked.add(level.key)
            continue
        previous = ordered[index - 1]
        if previous.key in unlocked and evaluate_level(previous, results, threshold).passed:
            unlocked.add(level.key)
            continue
        # لا يُفتح أي مستوى لاحق حتى يُتقن السابق.
        break
    return unlocked


def frequently_wrong_symbols(
    symbol_stats: Mapping[str, SymbolStat],
    limit: int = 12,
    min_attempts: int = REVIEW_MIN_ATTEMPTS,
    accuracy_threshold: float = REVIEW_ACCURACY_THRESHOLD,
) -> list[SymbolStat]:
    """أكثر الرموز تكرارًا في الخطأ، مرتّبة من الأكثر حاجة للمراجعة."""
    candidates = [
        stat
        for stat in symbol_stats.values()
        if stat.attempts >= min_attempts and stat.accuracy < accuracy_threshold
    ]
    candidates.sort(key=lambda s: (s.accuracy, -s.attempts))
    return candidates[:limit]


def overall_progress(
    lessons: Iterable[Lesson],
    results: Mapping[str, LessonResult],
    threshold: float = DEFAULT_MASTERY_THRESHOLD,
) -> float:
    """نسبة الإنجاز العامة عبر كل الدروس."""
    lesson_list = list(lessons)
    if not lesson_list:
        return 0.0
    completed = sum(
        1
        for lesson in lesson_list
        if (r := results.get(lesson.key)) is not None and (r.completed or r.best_score >= threshold)
    )
    return clamp_percentage(completed / len(lesson_list) * 100.0)
