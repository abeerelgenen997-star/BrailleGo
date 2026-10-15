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
        "welcome", "home", "lessons", "alphabet", "practice", "placement",
        "match", "exams", "review", "progress", "settings", "instructor",
        "help", "shortcuts",
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

    for selection, lang in ((1, "en"), (2, "fr"), (3, "es"), (0, "ar")):
        frame.navigate_to("settings")
        panel = frame._panels["settings"]
        panel._language.SetSelection(selection)
        panel._apply()
        from braille_wx import i18n

        assert i18n.get_lang() == lang
        assert captured["parent"] is frame
        assert captured["alive"] is True
    assert len(frame._panels) == 15


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
    for lang in ("ar", "en", "fr", "es"):
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


# ----------------------------------------------------------------------
# الميزات الجديدة: تطابق الحرف، تحديد المستوى، تعدد اللغات، دليل برايل
# ----------------------------------------------------------------------
def _static_labels(panel):
    labels = []

    def walk(win):
        if isinstance(win, (wx.StaticText, wx.StaticBox)):
            labels.append(win.GetLabel())
        for child in win.GetChildren():
            walk(child)

    walk(panel)
    return labels


def test_matching_exercise_generates_matching_kind(frame):
    """مولّد تطابق الحرف يُنتج تدريبات من نوع التطابق بنمط اختيار."""
    from braille_go.core.exercise_types import ExerciseKind

    exercises = frame.context.generator.generate_matching(count=6, language="ar")
    assert exercises
    assert all(e.kind is ExerciseKind.MATCH_LETTER for e in exercises)
    assert all(e.answer_mode is AnswerMode.CHOOSE_PATTERN for e in exercises)
    assert all(e.stimulus_text for e in exercises)


def test_matching_screen_runs_and_grades(frame):
    """شاشة التطابق تعمل لصالح المتعلّم المبصر وتُصحّح الإجابات."""
    frame.navigate_to("match")
    assert frame._current_id == "match"

    frame.navigate_to("lesson", lesson_key="", level_key="", mode="matching", match_lang="ar")
    panel = frame._panels["lesson"]
    assert panel._exercises, "يجب توليد تمارين التطابق"
    for _ in range(len(panel._exercises)):
        _answer_correctly(panel, panel._exercises[panel._index])
        panel._next()
    assert panel._finished


def test_placement_sets_starting_level(frame):
    """اختبار تحديد المستوى يقترح مستوى ويضبطه كنقطة بداية."""
    frame.navigate_to("placement")
    assert frame._current_id == "placement"
    frame._panels["placement"]._start()
    assert frame._current_id == "lesson"
    panel = frame._panels["lesson"]
    assert panel._mode == "placement"
    assert panel._exercises, "يجب توليد أسئلة تحديد المستوى"
    for _ in range(len(panel._exercises)):
        _answer_correctly(panel, panel._exercises[panel._index])
        panel._next()
    assert panel._finished
    assert panel._placement_note, "يجب عرض توصية بالمستوى"


def test_four_interface_languages_available():
    """أربع لغات واجهة مدعومة ولها ترجمات فعلية."""
    from braille_wx import i18n

    assert i18n.languages() == ("ar", "en", "fr", "es")
    for code, name in i18n.language_choices():
        assert code and name
    sample = ("save_settings", "menu_lessons", "menu_practice", "menu_exams",
              "btn_confirm", "braille_history", "match_title", "placement_start")
    for lang in i18n.languages():
        i18n.set_lang(lang)
        for key in sample:
            assert i18n.t(key) != key, (lang, key)
    i18n.set_lang("ar")


def test_help_guide_covers_braille_history(frame):
    """الدليل التعريفي يشرح برايل وأهميتها وتاريخ تطوّرها."""
    from braille_wx import i18n

    frame.navigate_to("help")
    labels = _static_labels(frame._panels["help"])
    for key in ("braille_what", "braille_importance", "braille_history"):
        assert i18n.t(key) in labels, key


def test_menus_include_lessons_practice_exams_placement(frame):
    """شريط القوائم يحتوي قوائم الدروس والتدريبات والاختبارات وتحديد المستوى."""
    from braille_wx import i18n

    bar = frame.GetMenuBar()
    assert bar is not None
    titles = [bar.GetMenuLabelText(i) for i in range(bar.GetMenuCount())]
    for key in ("menu_lessons", "menu_practice", "menu_exams", "menu_placement"):
        if key == "menu_placement":
            # تحديد المستوى يظهر كعنصر داخل قائمة الاختبارات.
            continue
        assert i18n.t(key) in titles, (key, titles)


# ----------------------------------------------------------------------
# إصلاحات المراجعة الشاملة: الاتجاه، العناوين المترجمة، Enter على الخيارات
# ----------------------------------------------------------------------
def test_every_level_and_lesson_has_english_title():
    """كل مستوى ودرس له عنوان إنجليزي حتى لا تظهر عناوين عربية في واجهة غير عربية."""
    from braille_go.core import curriculum as cur

    for level in cur.LEVELS:
        assert cur.level_title(level, "en") != level.title_ar or not level.title_ar
        assert cur.level_title(level, "en").strip()
        for lesson in level.lessons:
            assert cur.lesson_title(lesson, "en").strip()
            assert cur.lesson_title(lesson, "en") != lesson.title_ar


def test_exercise_prompts_are_localized():
    """نصوص الأسئلة تتبع لغة الواجهة الحالية بدل أن تبقى عربية دائمًا."""
    from braille_go.core import curriculum as cur
    from braille_go.core import i18n as core_i18n
    from braille_go.core.exercises import ExerciseGenerator, build_default_repository

    generator = ExerciseGenerator(build_default_repository())
    lesson = cur.first_lesson()
    try:
        core_i18n.set_lang("en")
        english = generator.generate_lesson(lesson, count=4)
        assert english
        assert all(e.prompt_ar and e.prompt_ar.isascii() for e in english), [
            e.prompt_ar for e in english
        ]
    finally:
        core_i18n.set_lang("ar")


def test_feedback_is_localized(frame):
    """التغذية الراجعة (صحيحة/خاطئة) تتبع لغة الواجهة."""
    from braille_wx import i18n
    from braille_go.core import i18n as core_i18n

    try:
        core_i18n.set_lang("en")
        i18n.set_lang("en")
        lesson = first_lesson()
        level = level_of_lesson(lesson.key)
        frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key)
        panel = frame._panels["lesson"]
        exercise = panel._exercises[panel._index]
        feedback = frame.context.grade(exercise, exercise.correct_answer)
        assert feedback.title_ar == i18n.t("ex_fb_correct_title")
    finally:
        core_i18n.set_lang("ar")
        i18n.set_lang("ar")


def test_rtl_layout_direction_for_arabic(frame):
    """الاتجاه يُضبط يمينًا→يسارًا للعربية ويسارًا→يمينًا لغيرها."""
    from braille_wx import i18n

    try:
        i18n.set_lang("ar")
        frame.rebuild_ui()
        assert frame.GetLayoutDirection() == wx.Layout_RightToLeft
        i18n.set_lang("en")
        frame.rebuild_ui()
        assert frame.GetLayoutDirection() == wx.Layout_LeftToRight
    finally:
        i18n.set_lang("ar")
        frame.rebuild_ui()


def test_enter_selects_focused_option(frame, monkeypatch):
    """مفتاح الإدخال يختار الخيار المُركَّز عليه بدل تجاهله."""
    frame.navigate_to("lesson", lesson_key="", level_key="", mode="matching", match_lang="ar")
    panel = frame._panels["lesson"]
    assert panel._exercises
    assert panel._option_buttons, "يجب بناء أزرار الخيارات"
    assert panel._exercises[panel._index].answer_mode in (
        AnswerMode.CHOOSE_TEXT,
        AnswerMode.CHOOSE_PATTERN,
    )

    target_button = panel._option_buttons[0]
    monkeypatch.setattr(
        wx.Window, "FindFocus", staticmethod(lambda: target_button)
    )
    panel._answered = False
    assert panel.on_enter() is True
    assert panel._answered, "يجب أن يختار الإدخال الخيار المُركَّز عليه"


def test_braille_cell_accessibility_is_localized():
    """وصف خلية برايل لقارئ الشاشة يتبع لغة الواجهة."""
    from braille_wx import a11y
    from braille_wx import i18n
    from braille_go.core.braille import BrailleCell

    cell = BrailleCell.from_dots((1, 2))
    try:
        i18n.set_lang("en")
        english = a11y.describe_braille_cell(cell)
        assert "Dot" in english or "Braille cell" in english
        assert "braille" in english.lower()
        i18n.set_lang("ar")
        arabic = a11y.describe_braille_cell(cell)
        assert arabic != english
        assert "برايل" in arabic
    finally:
        i18n.set_lang("ar")


# ----------------------------------------------------------------------
# v1.4.0: الترحيب المكتوب/المسموع، التنقّل (رجوع/رئيسية/خروج و Esc)،
# أهداف الدرس ورمز الهدف، وبطاقة «التطبيق» في الإعدادات.
# ----------------------------------------------------------------------
class _FakeKeyEvent:
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


def test_navbar_has_back_home_exit(frame):
    """شريط التنقّل يعرض أزرار رجوع/الرئيسية/خروج كما في برامج ويندوز."""
    from braille_wx import i18n

    assert frame._btn_back.GetLabel() == i18n.t("nav_back")
    assert frame._btn_home.GetLabel() == i18n.t("nav_home")
    assert frame._btn_exit.GetLabel() == i18n.t("btn_exit")


def test_navigation_history_and_back(frame):
    """زر الرجوع يعود إلى الشاشة السابقة بالترتيب."""
    frame.navigate_to("home")
    frame.navigate_to("lessons")
    frame.navigate_to("help")
    assert frame._current_id == "help"
    assert frame.go_back() is True
    assert frame._current_id == "lessons"
    assert frame.go_back() is True
    assert frame._current_id == "home"


def test_escape_key_goes_back(frame):
    """مفتاح Esc يعمل كزر رجوع قياسي."""
    frame.navigate_to("home")
    frame.navigate_to("lessons")
    event = _FakeKeyEvent(wx.WXK_ESCAPE)
    frame._on_char_hook(event)
    assert event.skipped is False, "يجب أن يُستهلك مفتاح Esc"
    assert frame._current_id == "home"


def test_welcome_has_written_message_and_replay(frame, monkeypatch):
    """الترحيب مكتوب + مسموع (موسيقى) + منطوق، مع زر لإعادة الاستماع."""
    from braille_wx import i18n

    called = {"tune": 0, "spoken": []}
    monkeypatch.setattr(
        frame.context.sounds, "welcome_tune",
        lambda: called.__setitem__("tune", called["tune"] + 1),
    )
    monkeypatch.setattr(
        frame.context, "speak",
        lambda text, language=None: called["spoken"].append(text),
    )
    frame.navigate_to("home")
    frame.navigate_to("welcome")
    panel = frame._panels["welcome"]
    assert panel._message.GetLabel() == i18n.t("welcome_speak")
    assert panel._listen_button is not None

    called["tune"] = 0
    called["spoken"].clear()
    panel._play_welcome()
    assert called["tune"] >= 1
    assert called["spoken"] == [i18n.t("welcome_speak")]


def test_lesson_shows_objectives_and_symbols(frame):
    """كل درس يعرض عنوان أهدافه والحرف/الرمز المطلوب تعلّمه."""
    from braille_wx import i18n
    from braille_go.core.curriculum import all_lessons

    intro = first_lesson()
    frame.navigate_to("lesson", lesson_key=intro.key, level_key=level_of_lesson(intro.key).key)
    panel = frame._panels["lesson"]
    assert panel._objectives.GetLabel() == i18n.t("lesson_objectives")
    assert panel._symbols_label.GetLabel() == i18n.t("lesson_symbols_none")

    letter_lesson = next((l for l in all_lessons() if l.symbol_keys and not l.is_exam), None)
    if letter_lesson is not None:
        frame.navigate_to(
            "lesson", lesson_key=letter_lesson.key,
            level_key=level_of_lesson(letter_lesson.key).key,
        )
        panel = frame._panels["lesson"]
        label = panel._symbols_label.GetLabel()
        assert label and label != i18n.t("lesson_symbols_none")
        assert "{" not in label, "يجب أن تُطبَّق قيم التنسيق في النص"


def test_build_exercise_shows_dot_help_and_target(frame):
    """تدريب البناء يعرض تعليمات تحديد النقاط والحرف المطلوب تعلّمه."""
    from braille_go.core.curriculum import all_lessons

    intro = first_lesson()
    frame.navigate_to("lesson", lesson_key=intro.key, level_key=level_of_lesson(intro.key).key)
    panel = frame._panels["lesson"]
    exercise = panel._exercises[panel._index]
    assert exercise.answer_mode in (AnswerMode.BUILD_CELL, AnswerMode.BUILD_CELLS)
    assert panel._cell_help.IsShown()
    assert panel._cell_help.GetLabel()

    letter_lesson = next((l for l in all_lessons() if l.symbol_keys and not l.is_exam), None)
    if letter_lesson is not None:
        frame.navigate_to(
            "lesson", lesson_key=letter_lesson.key,
            level_key=level_of_lesson(letter_lesson.key).key,
        )
        panel = frame._panels["lesson"]
        index = next(
            (i for i, e in enumerate(panel._exercises) if e.show_target_text and e.stimulus_text),
            None,
        )
        if index is not None:
            panel._index = index
            panel._show_current()
            assert panel._target_label.IsShown()
            assert panel._exercises[index].stimulus_text in panel._target_label.GetLabel()


def test_settings_has_application_section(frame):
    """الإعدادات تحتوي بطاقة «التطبيق» بأزرار المشاركة/التحديث/البيانات/الإزالة."""
    from braille_wx import i18n

    frame.navigate_to("settings")
    panel = frame._panels["settings"]
    labels = _button_labels(panel)
    for key in ("settings_share", "settings_check_updates", "settings_open_data", "settings_uninstall"):
        assert i18n.t(key) in labels, (key, labels)


def test_settings_app_actions_are_safe(frame, monkeypatch):
    """أزرار التطبيق تعمل دون فتح نوافذ حقيقية أو تشغيل برامج."""
    from braille_wx import app_management as am
    from braille_wx import widgets as W

    opened: list[str] = []
    messages: list[tuple[str, str]] = []
    monkeypatch.setattr(am, "open_url", lambda url: opened.append(url) or True)
    monkeypatch.setattr(am, "open_data_folder", lambda: True)
    monkeypatch.setattr(am, "find_uninstaller", lambda: None)
    monkeypatch.setattr(W, "informational", lambda parent, title, text: messages.append((title, text)))
    monkeypatch.setattr(W, "confirm", lambda parent, title, text: True)

    frame.navigate_to("settings")
    panel = frame._panels["settings"]
    panel._share_app()
    panel._check_updates()
    panel._open_data_folder()
    panel._uninstall()
    assert opened, "يجب فتح رابط المشاركة/التحديث"
    assert len(messages) >= 4


def test_app_management_helpers():
    """روابط المشروع ودوال إدارة التطبيق متاحة وآمنة."""
    from braille_wx import app_management as am

    assert am.REPO_URL.startswith("https://github.com/")
    assert am.LATEST_RELEASE_URL.endswith("/releases/latest")
    assert am.REPO_URL in am.LATEST_RELEASE_URL
    found = am.find_uninstaller()
    assert found is None or isinstance(found, str)
    assert am.data_folder() is not None


def test_review_v140_i18n_keys_translated():
    """مفاتيح v1.4.0 الجديدة مترجمة في اللغات الأربع."""
    from braille_wx import i18n

    keys = (
        "nav_back", "nav_home", "btn_exit", "welcome_listen", "lesson_objectives",
        "lesson_symbols_label", "lesson_symbols_none", "target_label",
        "cell_help_title", "cell_help_legend", "settings_intro", "settings_app_section",
        "settings_app_desc", "settings_share", "share_done", "settings_check_updates",
        "updates_opened", "settings_open_data", "settings_uninstall", "uninstall_title",
        "uninstall_confirm", "uninstall_not_found", "app_version_label",
        "speech_voice_label", "speech_voice_auto", "speech_test", "speech_test_phrase",
    )
    try:
        for lang in i18n.languages():
            i18n.set_lang(lang)
            for key in keys:
                assert i18n.t(key) != key, (lang, key)
    finally:
        i18n.set_lang("ar")


def test_speech_enabled_and_voice_picker_by_default(frame):
    """النطق مُفعَّل افتراضيًا، والإعدادات فيها مُنتقي صوت وزر تجربة."""
    from braille_wx import i18n

    assert bool(frame.context.settings.get("speech_enabled")) is True
    frame.navigate_to("settings")
    panel = frame._panels["settings"]
    assert panel._voice is not None
    assert panel._voice.GetCount() >= 1
    assert panel._voice.GetString(0) == i18n.t("speech_voice_auto")


def test_target_letter_phrase_is_clear(frame, monkeypatch):
    """نطق الحرف المطلوب تعلّمه بصيغة واضحة («حرف أ» / «Letter A»)."""
    from braille_go.core.exercises import Exercise, ExerciseKind, AnswerMode

    frame.navigate_to("home")
    panel = frame._panels["lesson"]

    arabic = Exercise(
        key="t", kind=ExerciseKind.IDENTIFY_CHAR, lesson_key="t", prompt_ar="",
        answer_mode=AnswerMode.CHOOSE_TEXT, correct_answer="أ", language="ar",
    )
    english = Exercise(
        key="t", kind=ExerciseKind.IDENTIFY_CHAR, lesson_key="t", prompt_ar="",
        answer_mode=AnswerMode.CHOOSE_TEXT, correct_answer="A", language="en",
    )
    assert panel._single_target(arabic) == "أ"
    assert panel._target_phrase("أ", arabic) == "حرف أ"
    assert panel._target_phrase("A", english) == "Letter A"

    spoken: list[str] = []
    monkeypatch.setattr(frame.context, "speak", lambda text, language=None: spoken.append(text))
    panel._mode = ""
    panel._announce_target(arabic)
    assert spoken == ["حرف أ"]
    panel._mode = "exam"
    spoken.clear()
    panel._announce_target(arabic)
    assert spoken == [], "لا نكشف الحرف في وضع الاختبار"


def test_braille_cell_accepts_focus_and_toggles(monkeypatch):
    """الخلية تقبل التركيز بـ Tab، والمسافة تبدّل النقطة، والأسهم تتنقّل."""
    import wx as _wx

    from braille_wx.braille_cell import BrailleCellInput

    _wx.GetApp()
    parent = _wx.Frame(None)
    try:
        cell = BrailleCellInput(parent, scale=1.0, theme=None)
        assert cell.AcceptsFocus() is True
        assert cell.AcceptsFocusFromKeyboard() is True
        cell.toggle_dot(1)
        assert cell.dots() == (1,)
        cell.toggle_dot(1)
        assert cell.dots() == ()

        class _Key:
            def __init__(self, code):
                self._code = code

            def GetKeyCode(self):
                return self._code

            def ShiftDown(self):
                return False

            def Skip(self):
                pass

        cell._on_key_down(_Key(_wx.WXK_RIGHT))
        assert cell._cursor == 4  # من النقطة 1 إلى النقطة 4 في العمود الأيمن.
        cell._on_key_down(_Key(_wx.WXK_DOWN))
        assert cell._cursor == 5
    finally:
        parent.Destroy()
