"""اختبارات قواعد التقدّم والإتقان."""

from braille_go.core import progress, curriculum
from braille_go.data import db, progress_store


def test_evaluate_level():
    lvl = curriculum.LEVELS[0]
    results = {}
    for i, l in enumerate(lvl.lessons):
        results[l.key] = progress.LessonResult(
            lesson_key=l.key,
            level_key=lvl.key,
            attempts=1,
            best_score=90.0,
            last_score=90.0,
            correct_total=9,
            answered_total=10,
            completed=True,
        )
    ev = progress.evaluate_level(lvl, results, threshold=85.0)
    assert ev.passed
    assert ev.mastery >= 85.0


def test_can_advance_false():
    lvl = curriculum.LEVELS[0]
    results = {}
    progress.evaluate_level(lvl, results, threshold=85.0)
    can, reason = progress.can_advance(lvl, results, threshold=85.0)
    assert not can


def test_available_levels():
    results = {}
    available = progress.available_levels(curriculum.LEVELS, results, threshold=85.0)
    # only first unlocked initially
    assert "level_intro" in available


def test_overall_progress():
    lessons = curriculum.all_lessons()[:3]
    results = {}
    for l in lessons:
        results[l.key] = progress.LessonResult(lesson_key=l.key, level_key="x", best_score=95, completed=True)
    assert progress.overall_progress(lessons, results) == 100.0


def test_symbol_stats_needs_review():
    s = progress.SymbolStat(symbol_key="ar_ba", attempts=5, correct=2)
    assert s.accuracy < 70
    assert s.needs_review


def test_progress_store_save_session(tmp_path):
    d = db.Database(tmp_path / "t.sqlite3")
    d.connect()
    d.initialize()
    store = progress_store.ProgressStore(d)
    l = curriculum.first_lesson()
    # make fake exercises
    from braille_go.core import exercises
    repo = exercises.build_default_repository()
    gen = exercises.ExerciseGenerator(repo)
    exs = gen.generate_lesson(l, count=2)
    res = []
    for ex in exs:
        fb = exercises.grade(ex, ex.correct_dots, repo)
        res.append((ex, fb))
    store.save_session(l, "level_intro", res, threshold=85.0)
    snap = store.lesson_result(l.key)
    assert snap is not None
    d.close()
