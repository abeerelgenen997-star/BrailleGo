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


def _answer_correctly(panel, exercise) -> None:
    """أجب على التمرين إجابةً صحيحةً بغضّ النظر عن نوعه."""
    if exercise.answer_mode in (AnswerMode.CHOOSE_TEXT, AnswerMode.CHOOSE_PATTERN):
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
    else:  # BUILD_CELL
        for cell in panel._cells:
            cell.set_cell(exercise.correct_dots, notify=False)
        panel._on_confirm()


def test_all_screens_construct(frame):
    for screen_id in [
        "welcome", "home", "lessons", "alphabet", "practice", "exams",
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
        _answer_correctly(panel, exercise)
        assert panel._answered
        answered += 1
        panel._next()

    assert answered >= 1
    stats = context.progress.statistics()
    assert stats["answers_total"] >= answered
    assert stats["answers_correct"] >= answered


def test_typing_questions_keep_answer_box_enabled(frame):
    """حقل الإجابة يجب أن يبقى قابلًا للكتابة في كل مرة يظهر."""
    checked = 0
    for level in LEVELS:
        for lesson in level.lessons:
            frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key)
            panel = frame._panels["lesson"]
            for _ in range(len(panel._exercises)):
                if panel._finished:
                    break
                exercise = panel._exercises[panel._index]
                if exercise.answer_mode is AnswerMode.TYPE_TEXT:
                    checked += 1
                    assert panel._answer_box is not None
                    assert panel._answer_box.IsEnabled(), "حقل الإجابة معطّل!"
                _answer_correctly(panel, exercise)
                panel._next()
    assert checked >= 1, "لم نجد أي سؤال كتابة للتحقق"


def test_session_summary_does_not_block(frame):
    """نهاية الجلسة تُعرض داخل الشاشة وتسمح بالعودة بلا عوائق."""
    lesson = first_lesson()
    level = level_of_lesson(lesson.key)
    frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key)
    panel = frame._panels["lesson"]
    for _ in range(len(panel._exercises)):
        _answer_correctly(panel, panel._exercises[panel._index])
        panel._next()
    assert panel._finished
    assert frame._current_id == "lesson"
    # زر الإنهاء يعود للشاشة الرئيسية.
    panel._next()
    assert frame._current_id == "home"


def test_language_switch_rebuilds_ui(frame, monkeypatch):
    """تبديل اللغة يعيد بناء الواجهة دون استخدام لوحة مُتلَفة كأب للحوار."""
    captured = {}

    def fake_info(parent, title, text):
        captured["parent"] = parent
        captured["alive"] = not parent.IsBeingDeleted()

    monkeypatch.setattr("braille_wx.widgets.informational", fake_info)

    for selection, lang in ((1, "en"), (0, "ar")):
        frame.navigate_to("settings")
        panel = frame._panels["settings"]
        panel._language.SetSelection(selection)
        panel._apply()
        from braille_wx import i18n

        assert i18n.get_lang() == lang
        assert captured["parent"] is frame
        assert captured["alive"] is True
    assert len(frame._panels) == 13


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


# ----------------------------------------------------------------------
# الإضافات الجديدة (توسيع الأنماط وفئات المستخدمين والترحيب ومفتاح Enter)
# ----------------------------------------------------------------------
def test_more_display_modes_with_labels():
    """قائمة الأنماط غنية وتغطّي فئات متعدّدة، وكل نمط له ترجمة."""
    from braille_wx import i18n, theme as theme_mod

    assert len(theme_mod.MODES) >= 14
    for key in ("dyslexia", "protanopia", "tritanopia", "sepia", "oled_black", "senior"):
        assert key in theme_mod.MODES
    for lang in ("ar", "en"):
        i18n.set_lang(lang)
        for mode in theme_mod.MODES.values():
            assert i18n.t(mode.label_key) != mode.label_key, mode.label_key
        for key, label in theme_mod.mode_choices():
            assert label
    i18n.set_lang("ar")


def test_user_profiles_apply_and_persist(frame, monkeypatch):
    """فئات المستخدم الأربع موجودة وتضبط الإعدادات وتحفظها."""
    from braille_wx import profiles

    monkeypatch.setattr("braille_wx.widgets.informational", lambda *a, **k: None)
    monkeypatch.setattr("braille_wx.a11y.announce", lambda *a, **k: None)
    assert set(profiles.PROFILES) == {"instructor", "sighted_learner", "blind", "low_vision"}

    frame.navigate_to("settings")
    panel = frame._panels["settings"]
    index = panel._profile_keys.index("instructor")
    panel._profile.SetSelection(index)
    panel._on_profile_change(None)  # كما لو نقر المستخدم الفئة
    panel._apply()
    assert frame.context.settings.get("user_profile") == "instructor"
    assert bool(frame.context.settings.get("instructor_mode")) is True

    panel = frame._panels["settings"]
    index = panel._profile_keys.index("blind")
    panel._profile.SetSelection(index)
    panel._on_profile_change(None)
    panel._apply()
    assert frame.context.settings.get("user_profile") == "blind"
    assert bool(frame.context.settings.get("speech_enabled")) is True


def test_instructor_button_hidden_for_non_instructors(frame, monkeypatch):
    monkeypatch.setattr("braille_wx.widgets.informational", lambda *a, **k: None)
    frame.context.settings.set("instructor_mode", False)
    frame.navigate_to("home")
    labels = _button_labels(frame._panels["home"])
    assert not any("مدرب" in label for label in labels)

    frame.context.settings.set("instructor_mode", True)
    frame.navigate_to("home")
    labels = _button_labels(frame._panels["home"])
    assert any("مدرب" in label for label in labels)


def _button_labels(panel):
    labels = []

    def walk(win):
        if isinstance(win, wx.Button):
            labels.append(win.GetLabel())
        for child in win.GetChildren():
            walk(child)

    walk(panel)
    return labels


def test_welcome_plays_music_and_speech(tmp_path):
    """شاشة الترحيب تشغّل موسيقى ترحيبية وتنطق كلمة الترحيب من داخل التطبيق."""
    import wx as _wx

    from braille_wx.context import build_context
    from braille_wx.main_frame import MainFrame

    called = {"tune": 0, "spoken": []}
    _wx.GetApp()
    context = build_context(data_dir=tmp_path)
    frame = MainFrame(context)
    try:
        frame.context.sounds.welcome_tune = lambda: called.__setitem__("tune", called["tune"] + 1)
        frame.context.speak = lambda text, language=None: called["spoken"].append(text)
        frame.navigate_to("welcome")
        panel = frame._panels["welcome"]
        called["tune"] = 0
        called["spoken"].clear()
        panel.activate()
        assert called["tune"] >= 1
        assert called["spoken"], "لم يُنطق ترحيب"
        assert bool(frame.context.settings.get("welcome_shown")) is True
    finally:
        frame.Destroy()
        context.shutdown()


def test_enter_confirms_then_advances(frame):
    """مفتاح الإدخال يؤكّد الإجابة ثم ينتقل للسؤال التالي."""
    lesson = first_lesson()
    level = level_of_lesson(lesson.key)
    frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key)
    panel = frame._panels["lesson"]
    exercise = panel._exercises[panel._index]
    _answer_correctly(panel, exercise)
    assert panel._answered
    start_index = panel._index
    handled = panel.on_enter()
    assert handled is True
    assert panel._index == start_index + 1


def test_char_hook_routes_enter_to_panel(frame):
    """آلية اعتراض Enter على مستوى الإطار توجّهه إلى الشاشة الحالية."""
    lesson = first_lesson()
    level = level_of_lesson(lesson.key)
    frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key)
    panel = frame._panels["lesson"]
    _answer_correctly(panel, panel._exercises[panel._index])
    start_index = panel._index

    class FakeEvent:
        def __init__(self, code):
            self._code = code
            self.skipped = False

        def GetKeyCode(self):
            return self._code

        def ControlDown(self):
            return False

        def AltDown(self):
            return False

        def Skip(self):
            self.skipped = True

    event = FakeEvent(wx.WXK_RETURN)
    frame._on_char_hook(event)
    assert event.skipped is False, "يجب أن يُستهلك مفتاح الإدخال"
    assert panel._index == start_index + 1


def test_alphabet_guide_speaks_symbols(frame, monkeypatch):
    """دليل الحروف والأرقام يعرض الحروف والأرقام وينطقها من داخل التطبيق."""
    from braille_go.core.symbols import SymbolCategory

    spoken = []
    monkeypatch.setattr(frame.context, "speak", lambda text, language=None: spoken.append((text, language)))
    monkeypatch.setattr("braille_wx.a11y.announce", lambda *a, **k: None)

    frame.navigate_to("alphabet")
    panel = frame._panels["alphabet"]
    assert panel is not None

    for category in (SymbolCategory.LETTER_AR, SymbolCategory.LETTER_EN, SymbolCategory.DIGIT):
        symbols = frame.context.repository.by_category(category)
        assert symbols, category
        target = symbols[0]
        panel._play(target, target.name_ar)

    assert any(text for text, _ in spoken), "لم يُنطق أي رمز"
    # يجب أن يُنطق الرقم بصيغة واضحة.
    assert any("رقم" in text or "number" in text for text, _ in spoken), spoken
