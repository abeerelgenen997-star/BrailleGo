"""اختبارات التدريب والتصحيح."""

from braille_go.core import exercises, curriculum
from braille_go.core.exercises import AnswerMode, ExerciseKind


def test_grade_choose_text_correct():
    repo = exercises.build_default_repository()
    gen = exercises.ExerciseGenerator(repo)
    lesson = curriculum.first_lesson()
    ex = gen._identify_char(lesson, 0, repo.many(lesson.symbol_keys) or repo.many(["ar_alif"]))
    if ex is None:
        ex = gen._identify_char(lesson, 0, repo.many(["ar_alif"]))
    fb = exercises.grade(ex, ex.correct_answer, repo)
    assert fb.correct


def test_grade_build_cell():
    repo = exercises.build_default_repository()
    cell = repo.require("ar_alif").cell
    ex = exercises.Exercise(
        key="t1",
        kind=ExerciseKind.BUILD_PATTERN,
        lesson_key="l1",
        prompt_ar="",
        answer_mode=AnswerMode.BUILD_CELL,
        correct_dots=cell.dots,
        correct_answer=cell.to_dot_string(""),
    )
    fb = exercises.grade(ex, cell.dots, repo)
    assert fb.correct


def test_grade_build_cells_count():
    repo = exercises.build_default_repository()
    a = repo.require("ar_alif").cell.dots
    b = repo.require("ar_ba").cell.dots
    ex = exercises.Exercise(
        key="t2",
        kind=ExerciseKind.BUILD_WORD,
        lesson_key="l1",
        prompt_ar="",
        answer_mode=AnswerMode.BUILD_CELLS,
        correct_cells=(a, b),
    )
    fb = exercises.grade(ex, (a,), repo)
    assert not fb.correct
