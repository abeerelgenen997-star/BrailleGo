"""اختبارات دخانية لواجهة wxPython (تُتخطّى إن لم يتوفّر wx)."""

from __future__ import annotations

import pytest

wx = pytest.importorskip("wx")

from braille_go.core.curriculum import LEVELS, first_lesson, level_of_lesson  # noqa: E402
from braille_go.core.exercises import AnswerMode  # noqa: E402


@pytest.fixture(scope="module")
def app():
    application = wx.App(False)
    yield application
    # لا نستدعي MainLoop؛ نكتفي بإتلاف النوافذ.


@pytest.fixture()
def frame(app, tmp_path):
    from braille_wx.context import build_context
    from braille_wx.main_frame import MainFrame

    context = build_context(data_dir=tmp_path)
    window = MainFrame(context)
    yield window
    window.Destroy()
    context.shutdown()


def test_all_screens_construct(frame):
    for screen_id in [
        "welcome", "home", "lessons", "practice", "exams",
        "review", "progress", "settings", "instructor", "help", "shortcuts",
    ]:
        frame.navigate_to(screen_id)
        assert frame._current_id == screen_id


def test_lesson_screen_builds_exercises(frame):
    lesson = first_lesson()
    level = level_of_lesson(lesson.key)
    frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key)
    panel = frame._panels["lesson"]
    assert panel._exercises, "يجب أن يولّد الدرس تدريبات"
    assert panel._question_box is not None
    assert panel._question_box.GetValue()


def test_question_edit_box_focus_shortcut(frame):
    lesson = first_lesson()
    level = level_of_lesson(lesson.key)
    frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key)
    panel = frame._panels["lesson"]
    assert panel.focus_edit_box() is True


def test_answer_correctly_records_progress(frame):
    context = frame.context
    # درس يحتوي على رموز حقيقية لأسئلة التعرّف.
    lesson = next(l for l in LEVELS[1].lessons if l.symbol_keys)
    level = level_of_lesson(lesson.key)
    frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key)
    panel = frame._panels["lesson"]

    answered = 0
    for _ in range(len(panel._exercises)):
        exercise = panel._exercises[panel._index]
        if exercise.answer_mode in (AnswerMode.CHOOSE_TEXT, AnswerMode.CHOOSE_PATTERN):
            # اختر الخيار الصحيح.
            if exercise.answer_mode is AnswerMode.CHOOSE_PATTERN:
                index = list(exercise.option_labels).index(exercise.correct_answer)
            else:
                index = list(exercise.options).index(exercise.correct_answer)
            panel._choose_option(index)
        elif exercise.answer_mode is AnswerMode.TYPE_TEXT:
            panel._answer_box.SetValue(exercise.correct_answer)
            panel._on_confirm()
        elif exercise.answer_mode is AnswerMode.BUILD_CELLS:
            for i, cell in enumerate(panel._cells):
                want = exercise.correct_cells[i] if i < len(exercise.correct_cells) else ()
                cell.set_cell(want, notify=False)
            panel._on_confirm()
        else:
            for cell in panel._cells:
                cell.set_cell(exercise.correct_dots, notify=False)
            panel._on_confirm()
        assert panel._answered
        answered += 1
        panel._next()

    assert answered >= 1
    stats = context.progress.statistics()
    assert stats["answers_total"] >= answered
    assert stats["answers_correct"] >= answered


def test_display_modes_apply(frame):
    from braille_wx import theme as theme_mod

    for key in theme_mod.MODES:
        frame._set_mode(key)
        assert frame.theme.colors["background"]


def test_settings_persist(frame, monkeypatch):
    monkeypatch.setattr("braille_wx.widgets.informational", lambda *a, **k: None)
    frame.navigate_to("settings")
    panel = frame._panels["settings"]
    panel._font.SetValue(1.3)
    panel._mastery.SetValue(90.0)
    panel._apply()
    assert float(frame.context.settings.get("font_scale")) == pytest.approx(1.3)
    assert float(frame.context.settings.get("mastery_threshold")) == pytest.approx(90.0)


def test_instructor_adds_user(frame, monkeypatch):
    monkeypatch.setattr("braille_wx.widgets.informational", lambda *a, **k: None)
    from braille_go.data.users import UserManager

    frame.navigate_to("instructor")
    panel = frame._panels["instructor"]
    panel._name.SetValue("طالب اختبار")
    panel._add_user()
    names = [user.name for user in UserManager(frame.context.database).list_users()]
    assert "طالب اختبار" in names
