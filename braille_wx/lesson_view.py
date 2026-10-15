"""شاشة تنفيذ الدرس/الاختبار لنسخة wxPython.

تركّز هذه الشاشة على ملاحظة المراجع الأولى: **صندوق كتابة (Edit Box) لقراءة
السؤال** يكون قابلًا للتركيز بالكامل مع قارئات الشاشة. عند ظهور كل سؤال
يُوضع التركيز تلقائيًا على هذا الصندوق، ويمكن العودة إليه في أي وقت بالاختصار
**Ctrl+E**. كما يوجد حقل إدخال إجابة حقيقي (Edit Box) لأسئلة الكتابة.
"""

from __future__ import annotations

import wx

from braille_go.core.curriculum import LEVELS, LEVELS_BY_KEY, LESSONS_BY_KEY, Lesson, level_of_lesson
from braille_go.core.exercises import AnswerMode

from . import i18n
from .a11y import announce
from .base_panel import BasePanel, clear_sizer
from .braille_cell import BrailleCellInput, BrailleCellsView
from . import widgets as W


class LessonPanel(BasePanel):
    """شاشة تشغيل درس أو اختبار أو مراجعة."""

    def __init__(self, parent: wx.Window, context, frame) -> None:
        super().__init__(parent, context, frame)
        self._lesson = None
        self._level = None
        self._exercises: list = []
        self._index = 0
        self._results: list = []
        self._mode = ""
        self._match_lang = "ar"
        self._placement_note = ""
        self._answered = False
        self._finished = False

        # عناصر تُبنى عند التنشيط.
        self._title: wx.StaticText | None = None
        self._banner: wx.StaticText | None = None
        self._objectives: wx.StaticText | None = None
        self._intro: wx.StaticText | None = None
        self._symbols_label: wx.StaticText | None = None
        self._target_label: wx.StaticText | None = None
        self._cell_help: wx.StaticText | None = None
        self._question_box: wx.TextCtrl | None = None
        self._stimulus_view: BrailleCellsView | None = None
        self._braille_label: wx.StaticText | None = None
        self._options_sizer: wx.Sizer | None = None
        self._options_panel: wx.Panel | None = None
        self._answer_box: wx.TextCtrl | None = None
        self._cells: list[BrailleCellInput] = []
        self._cells_panel: wx.Panel | None = None
        self._option_buttons: list[wx.Button] = []
        self._btn_clear: wx.Button | None = None
        self._btn_confirm: wx.Button | None = None
        self._btn_next: wx.Button | None = None
        self._feedback_box: wx.TextCtrl | None = None
        self._end_text: wx.StaticText | None = None
        self._build_ui()

    # ------------------------------------------------------------------
    # البناء
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        clear_sizer(self.content)
        theme = self.theme

        self._title = W.heading(self, i18n.t("lesson_label"), theme)
        self.content.Add(self._title, 0, wx.ALL, 8)

        self._banner = wx.StaticText(self, label="")
        self._banner.SetName(i18n.t("status_bar"))
        self.content.Add(self._banner, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # أهداف الدرس: عنوان واضح ثم وصف الدرس ومقدّمته ----------------
        self._objectives = W.subheading(self, i18n.t("lesson_objectives"), theme)
        self.content.Add(self._objectives, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self._intro = W.wrapped_text(self, "")
        self.content.Add(self._intro, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # الحرف/الرمز المطلوب تعلّمه في هذا الدرس ----------------------
        self._symbols_label = W.wrapped_text(self, "")
        self.content.Add(self._symbols_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # المطلوب تعلّمه في السؤال الحالي (كبير وواضح للمبتدئ المبصر) ---
        self._target_label = wx.StaticText(self, label="")
        self._target_label.SetName(i18n.t("target_label").format(target=""))
        self._target_label._keep_font = True
        try:
            target_font = theme.make_font(20.0)
            target_font.SetWeight(wx.FONTWEIGHT_BOLD)
            self._target_label.SetFont(target_font)
        except Exception:
            pass
        self._target_label.Hide()
        self.content.Add(self._target_label, 0, wx.EXPAND | wx.ALL, 10)

        # صندوق السؤال (Edit Box قابل للقراءة الكاملة) -----------------
        qbox, qsizer = W.card(self, self.content, i18n.t("question_card"))
        self._question_box = W.read_only_box(qbox, multiline=True, height=90, name=i18n.t("question_card"))
        qsizer.Add(self._question_box, 1, wx.EXPAND | wx.ALL, 4)
        hint = W.body(qbox, i18n.t("question_hint"))
        qsizer.Add(hint, 0, wx.ALL, 4)

        # المحفّز (نمط برايل للقراءة) ----------------------------------
        sbox, ssizer = W.card(self, self.content, i18n.t("stimulus_card"))
        self._stimulus_view = BrailleCellsView(sbox, scale=self.theme.cell_scale(), theme=theme)
        ssizer.Add(self._stimulus_view, 0, wx.ALL | wx.ALIGN_CENTER, 6)
        self._braille_label = wx.StaticText(sbox, label="")
        self._braille_label.SetName(i18n.t("braille_plain"))
        self._braille_label._keep_font = True
        try:
            self._braille_label.SetFont(theme.make_braille_font(30.0))
        except Exception:
            pass
        ssizer.Add(self._braille_label, 0, wx.ALL | wx.ALIGN_CENTER, 6)

        # الخيارات -----------------------------------------------------
        self._options_panel = wx.Panel(self)
        self._options_sizer = wx.BoxSizer(wx.VERTICAL)
        self._options_panel.SetSizer(self._options_sizer)
        self.content.Add(self._options_panel, 0, wx.EXPAND | wx.ALL, 8)

        # حقل إدخال الإجابة (Edit Box) --------------------------------
        abox, asizer = W.card(self, self.content, i18n.t("answer_card"))
        self._answer_box = W.editable_box(abox, name=i18n.t("answer_card"), on_enter=self._on_confirm)
        asizer.Add(self._answer_box, 0, wx.EXPAND | wx.ALL, 4)
        self._answer_box.Hide()

        # خلايا البناء (تظهر متوسّطة أفقيًا في منتصف الشاشة) ------------
        self._cells_panel = wx.Panel(self)
        cells_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cells_panel.SetSizer(cells_sizer)
        cells_outer = wx.BoxSizer(wx.HORIZONTAL)
        cells_outer.AddStretchSpacer(1)
        cells_outer.Add(self._cells_panel, 0, wx.ALL, 8)
        cells_outer.AddStretchSpacer(1)
        self.content.Add(cells_outer, 0, wx.EXPAND)

        # تعليمات مرئية واضحة لطريقة تحديد النقاط (تظهر في تدريبات البناء) --
        self._cell_help = W.wrapped_text(
            self,
            i18n.t("cell_help_title")
            + "\n"
            + i18n.t("cell_input_hint")
            + "\n"
            + i18n.t("cell_help_legend"),
            width=760,
        )
        self._cell_help.SetName(i18n.t("cell_help_title"))
        self._cell_help.Hide()
        self.content.Add(self._cell_help, 0, wx.EXPAND | wx.ALL, 8)

        # شريط الأزرار -------------------------------------------------
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_clear = W.action_button(self, i18n.t("btn_clear"), on_click=self._clear, tooltip="Ctrl+Delete")
        self._btn_confirm = W.action_button(self, i18n.t("btn_confirm"), on_click=self._on_confirm, primary=True, tooltip="Enter")
        self._btn_next = W.action_button(self, i18n.t("btn_next"), on_click=self._next, tooltip="Ctrl+N")
        self._btn_next.Hide()
        buttons.Add(self._btn_clear, 0, wx.RIGHT, 8)
        buttons.Add(self._btn_confirm, 0, wx.RIGHT, 8)
        buttons.Add((0, 0), 1, wx.EXPAND)
        buttons.Add(self._btn_next, 0)
        self.content.Add(buttons, 0, wx.EXPAND | wx.ALL, 8)

        # التغذية الراجعة ----------------------------------------------
        fbox, fsizer = W.card(self, self.content, i18n.t("feedback_card"))
        self._feedback_box = W.read_only_box(fbox, multiline=True, height=110, name=i18n.t("feedback_card"))
        fsizer.Add(self._feedback_box, 1, wx.EXPAND | wx.ALL, 4)
        self._feedback_box.Hide()

        self._end_text = W.wrapped_text(self, "")
        self.content.Add(self._end_text, 0, wx.EXPAND | wx.ALL, 10)

        self.finish_layout()

    # ------------------------------------------------------------------
    # التنشيط
    # ------------------------------------------------------------------
    def activate(self, **kwargs) -> None:
        lesson_key = kwargs.get("lesson_key", "")
        level_key = kwargs.get("level_key", "")
        self._mode = kwargs.get("mode", "")
        self._match_lang = kwargs.get("match_lang", "ar")
        self._placement_note = ""
        self._lesson = LESSONS_BY_KEY.get(lesson_key)
        self._level = LEVELS_BY_KEY.get(level_key) or level_of_lesson(lesson_key)
        self._exercises = []
        self._index = 0
        self._results = []
        self._answered = False
        self._finished = False
        self._show_feedback("")
        self._end_text.SetLabel("")
        self._banner.SetLabel("")
        self._btn_next.SetLabel(i18n.t("btn_next"))
        self._btn_next.Hide()
        self._btn_confirm.Enable(True)
        self._btn_clear.Enable(True)
        if self._answer_box is not None:
            self._answer_box.SetValue("")
            self._answer_box.Enable(True)

        # وضع التطابق ووضع تحديد المستوى قد لا يعتمدان على درسٍ محدّد.
        if self._mode == "matching":
            self._lesson = Lesson(
                key="matching",
                title_ar=i18n.t("match_title"),
                description_ar=i18n.t("match_intro"),
                language=self._match_lang,
            )

        if not self._lesson:
            self._intro.SetLabel(i18n.t("unknown_lesson"))
            return
        self._title.SetLabel(i18n.lesson_title(self._lesson))
        self._title.SetName(i18n.lesson_title(self._lesson))
        self._intro.SetLabel(
            i18n.lesson_intro(self._lesson) or i18n.lesson_description(self._lesson) or ""
        )
        if self._symbols_label is not None:
            self._symbols_label.SetLabel(self._lesson_symbols_text())

        if self._mode == "matching":
            self._exercises = self.context.generator.generate_matching(count=8, language=self._match_lang)
        elif self._mode == "placement":
            self._exercises = self._build_placement()
        elif self._mode == "review":
            keys = self.context.needs_review_symbols(limit=10)
            if not keys:
                # لا توجد أخطاء مسجّلة بعد: نراجع رموز أول درس متاح.
                keys = list(self._lesson.symbol_keys)
            self._exercises = self.context.generator.generate_review("review_lesson", keys, count=8)
        elif self._mode == "mixed":
            self._exercises = self.context.generate_exercises(self._lesson, count=6)
        else:
            self._exercises = self.context.generate_exercises(self._lesson, count=self._lesson.exercise_count)

        if not self._exercises:
            message = i18n.t("no_exercises")
            self._end_text.SetLabel(message)
            self._question_box.SetValue(message)
            self._question_box.SetFocus()
            self._btn_confirm.Enable(False)
            self._btn_clear.Enable(False)
            return
        self._show_current()
        self.finish_layout()

    def _build_placement(self) -> list:
        """ولّد أسئلة موزّعة على المستويات لتقدير مستوى المتعلّم."""
        exercises: list = []
        seen: set[str] = set()
        for level in LEVELS:
            for lesson in level.lessons[:2]:
                try:
                    generated = self.context.generate_exercises(lesson, count=2)
                except Exception:
                    generated = []
                for exercise in generated:
                    if exercise.key in seen:
                        continue
                    seen.add(exercise.key)
                    exercises.append(exercise)
            if len(exercises) >= 10:
                break
        return exercises[:10]

    def _report_placement(self) -> None:
        """اقترح مستوى البداية وفق نتائج اختبار تحديد المستوى واضبطه."""
        totals: dict[str, int] = {}
        rights: dict[str, int] = {}
        for exercise, feedback in self._results:
            level = level_of_lesson(exercise.lesson_key)
            if level is None:
                continue
            totals[level.key] = totals.get(level.key, 0) + 1
            if feedback.correct:
                rights[level.key] = rights.get(level.key, 0) + 1
        recommended = None
        for level in LEVELS:
            if not totals.get(level.key):
                continue
            if rights.get(level.key, 0) / totals[level.key] >= 0.6:
                recommended = level
            else:
                break
        if recommended is None and LEVELS:
            recommended = LEVELS[0]
        if recommended is not None and recommended.lessons:
            lesson = recommended.lessons[0]
            try:
                self.context.set_current_position(recommended.key, lesson.key)
            except Exception:
                pass
            self._placement_note = (
                i18n.t("placement_recommend").format(level=f"{recommended.number}. {i18n.level_title(recommended)}")
                + " " + i18n.t("placement_sets")
            )
        else:
            self._placement_note = i18n.t("placement_none")

    # ------------------------------------------------------------------
    # العرض
    # ------------------------------------------------------------------
    def _lesson_symbols_text(self) -> str:
        """نص يوضّح الحرف/الرمز (أو الرموز) التي يعلّمها هذا الدرس."""
        lesson = self._lesson
        if lesson is None:
            return ""
        arabic = i18n.get_lang() == "ar"
        names: list[str] = []
        for key in list(lesson.symbol_keys)[:8]:
            symbol = None
            try:
                symbol = self.context.repository.get(key)
            except Exception:
                symbol = None
            if symbol is None:
                continue
            name = symbol.name_ar if arabic else (symbol.name_en or symbol.name_ar)
            if name:
                names.append(name)
        if not names:
            return i18n.t("lesson_symbols_none")
        return i18n.t("lesson_symbols_label").format(
            symbols=i18n.t("ex_separator").join(names)
        )

    def _show_current(self) -> None:
        if self._index >= len(self._exercises):
            self._finish()
            return
        ex = self._exercises[self._index]
        self._answered = False

        # صندوق السؤال: النص الكامل الذي يقرأه قارئ الشاشة.
        question_text = ex.prompt_ar
        if ex.show_target_text and ex.stimulus_text:
            question_text += "\n" + i18n.t("required_prefix") + ex.stimulus_text
        if self._question_box is not None:
            self._question_box.SetValue(question_text)
            self._question_box.SetName(i18n.t("question_name_prefix") + ex.prompt_ar)

        # المحفّز.
        if ex.stimulus_braille:
            self._stimulus_view.set_cells(ex.stimulus_braille)
            self._braille_label.SetLabel(ex.stimulus_braille)
            self._braille_label.Show()
        else:
            self._stimulus_view.set_cells(())
            self._braille_label.SetLabel("")
            self._braille_label.Hide()

        self._clear_options()
        self._clear_cells()
        if self._answer_box is not None:
            self._answer_box.SetValue("")
            self._answer_box.Hide()

        if ex.answer_mode in (AnswerMode.CHOOSE_TEXT, AnswerMode.CHOOSE_PATTERN):
            self._option_buttons = []
            for i, opt in enumerate(ex.options):
                label = ex.option_labels[i] if ex.option_labels and i < len(ex.option_labels) else opt
                button = W.action_button(
                    self._options_panel, label,
                    on_click=lambda idx=i: self._choose_option(idx),
                    name=i18n.t("option_prefix").format(n=i + 1, label=label),
                )
                self._option_buttons.append(button)
                self._options_sizer.Add(button, 0, wx.EXPAND | wx.ALL, 3)
            self._options_panel.Show()
            self._options_panel.Layout()
        else:
            self._options_panel.Hide()

        if ex.answer_mode is AnswerMode.TYPE_TEXT and self._answer_box is not None:
            self._answer_box.Enable(True)
            self._answer_box.Show()
            self._btn_clear.Hide()
        elif ex.answer_mode in (AnswerMode.BUILD_CELL, AnswerMode.BUILD_CELLS):
            self._btn_clear.Show()
            self._build_cells(ex)
        else:
            self._btn_clear.Hide()

        # الهدف: أظهِر الحرف/الرمز المطلوب تعلّمه بوضوح إن توفّر نصّه.
        target = ex.stimulus_text if (ex.show_target_text and ex.stimulus_text) else ""
        if self._target_label is not None:
            if target:
                text = i18n.t("target_label").format(target=target)
                self._target_label.SetLabel(text)
                self._target_label.SetName(text)
                self._target_label.Show()
            else:
                self._target_label.Hide()

        # تعليمات مرئية لطريقة تحديد النقاط في تدريبات البناء.
        if self._cell_help is not None:
            if ex.answer_mode in (AnswerMode.BUILD_CELL, AnswerMode.BUILD_CELLS):
                self._cell_help.Show()
            else:
                self._cell_help.Hide()

        self.content.Layout()
        self._show_feedback("")
        self._btn_next.Hide()
        self._btn_confirm.Enable(True)
        self._btn_clear.Enable(True)
        self._banner.SetLabel("")

        # نغمة لافتة للانتباه تُعلن بدء سؤال جديد (مفيدة للطفل الكفيف).
        try:
            if bool(self.context.settings.get("encouragement_enabled", True)) and self._mode != "exam":
                self.context.sounds.attention()
        except Exception:
            pass
        self.context.speak_guidance(ex.speak_prompt(), ex.language)
        self._announce_target(ex)

        # التركيز على صندوق السؤال أو حقل الإجابة.
        wx.CallAfter(self._focus_initial)

    #: أسماء الأرقام العربية للنطق الواضح.
    _DIGIT_WORDS_AR = {
        "0": "صفر", "1": "واحد", "2": "اثنان", "3": "ثلاثة", "4": "أربعة",
        "5": "خمسة", "6": "ستة", "7": "سبعة", "8": "ثمانية", "9": "تسعة",
    }
    _DIGIT_WORDS_EN = {
        "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
        "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
    }

    def _announce_target(self, ex) -> None:
        """انطق الحرف/الرمز المطلوب تعلّمه بصوت واضح من داخل التطبيق.

        تُفعَّل هذه الميزة عبر إعداد ``announce_symbols``، وتُساعد المتعلّم
        الكفيف على معرفة الحرف/الرقم الحالي مباشرة دون قراءة الشاشة. ننطق
        الحرف بصيغة واضحة («الحرف أ» / «Letter A») باستخدام صوت التطبيق.
        """
        try:
            if not bool(self.context.settings.get("announce_symbols", True)):
                return
        except Exception:
            return
        # في وضع الاختبار لا نُعلن الرمز حتى لا نفشي الإجابة.
        if self._mode == "exam":
            return
        target = self._single_target(ex)
        if not target:
            return
        self.context.speak(self._target_phrase(target, ex), ex.language)

    def _single_target(self, ex) -> str:
        """أعِد الحرف/الرقم المستهدف (حرف واحد) من التمرين إن أمكن."""
        candidates: list[str] = [ex.correct_answer, ex.stimulus_text]
        for key in getattr(ex, "symbol_keys", ()) or ():
            symbol = None
            try:
                symbol = self.context.repository.get(key)
            except Exception:
                symbol = None
            if symbol is not None:
                candidates.append(symbol.char)
        for value in candidates:
            text = (value or "").strip()
            if len(text) == 1:
                return text
        return ""

    def _target_phrase(self, target: str, ex) -> str:
        """صيغة نطق واضحة للحرف/الرقم المطلوب تعلّمه."""
        language = (ex.language or "ar").lower()
        if language == "en":
            if target.isdigit():
                return f"Number {self._DIGIT_WORDS_EN.get(target, target)}"
            return f"Letter {target}"
        if target.isdigit():
            return f"رقم {self._DIGIT_WORDS_AR.get(target, target)}"
        return f"حرف {target}"

    def _speak_feedback(self, feedback, ex) -> None:
        """انطق نتيجة الإجابة مع عبارة تشجيع من داخل التطبيق."""
        try:
            encourage = bool(self.context.settings.get("encouragement_enabled", True))
        except Exception:
            encourage = True
        spoken = feedback.spoken
        if encourage:
            if feedback.correct:
                spoken = i18n.t("praise_correct") + spoken
            else:
                spoken = i18n.t("praise_wrong") + spoken
        self.context.speak(spoken, ex.language)

    def _focus_initial(self) -> None:
        ex = self._exercises[self._index] if self._index < len(self._exercises) else None
        if ex is not None and ex.answer_mode is AnswerMode.TYPE_TEXT and self._answer_box is not None:
            self._answer_box.SetFocus()
        elif self._cells:
            self._cells[0].SetFocus()
        elif self._question_box is not None:
            self._question_box.SetFocus()

    def _build_cells(self, ex) -> None:
        count = max(1, int(ex.letter_count or 1))
        sizer = self._cells_panel.GetSizer()
        for i in range(count):
            column = wx.BoxSizer(wx.VERTICAL)
            caption = W.body(self._cells_panel, i18n.t("cell_caption").format(n=i + 1))
            cell = BrailleCellInput(self._cells_panel, scale=self.theme.cell_scale(), theme=self.theme)
            cell.on_confirm = self._on_confirm
            self._cells.append(cell)
            column.Add(caption, 0, wx.ALIGN_CENTER | wx.ALL, 2)
            column.Add(cell, 0, wx.ALL, 2)
            sizer.Add(column, 0, wx.ALL, 6)
        self._cells_panel.Show()
        self._cells_panel.Layout()

    def _clear_cells(self) -> None:
        for cell in self._cells:
            cell.Destroy()
        self._cells = []
        if self._cells_panel is not None:
            sizer = self._cells_panel.GetSizer()
            if sizer is not None:
                clear_sizer(sizer)
            self._cells_panel.Hide()

    def _clear_options(self) -> None:
        if self._options_sizer is not None:
            clear_sizer(self._options_sizer)
        self._option_buttons = []

    # ------------------------------------------------------------------
    # الإجابة
    # ------------------------------------------------------------------
    def _choose_option(self, index: int) -> None:
        if self._answered or self._index >= len(self._exercises):
            return
        ex = self._exercises[self._index]
        self.context.sounds.click()
        if ex.answer_mode is AnswerMode.CHOOSE_PATTERN:
            response: object = index
        else:
            response = ex.options[index] if 0 <= index < len(ex.options) else ""
        feedback = self.context.grade(ex, response)
        self._record_and_show(ex, feedback)

    def _on_confirm(self) -> None:
        if self._answered or self._index >= len(self._exercises):
            return
        ex = self._exercises[self._index]
        mode = ex.answer_mode
        if mode is AnswerMode.TYPE_TEXT:
            response = self._answer_box.GetValue() if self._answer_box is not None else ""
            if not response.strip():
                self._banner.SetLabel(i18n.t("write_answer_hint"))
                announce(self, i18n.t("write_answer_announce"))
                return
        elif mode is AnswerMode.BUILD_CELLS:
            response = [cell.dots() for cell in self._cells]
        else:
            if not self._cells:
                return
            response = self._cells[0].dots()
        feedback = self.context.grade(ex, response)
        self._record_and_show(ex, feedback)

    def _record_and_show(self, ex, feedback) -> None:
        lvl_key = self._level.key if self._level else ""
        try:
            self.context.progress.record_answer(ex, feedback, lvl_key, ex.lesson_key)
        except Exception:
            pass
        self._results.append((ex, feedback))
        self._answered = True

        if feedback.correct:
            self.context.sounds.correct()
        else:
            self.context.sounds.incorrect()
        self._speak_feedback(feedback, ex)

        text = feedback.title_ar
        if feedback.message_ar:
            text += "\n" + feedback.message_ar
        if feedback.explanation_ar:
            text += "\n" + feedback.explanation_ar
        if not feedback.correct and feedback.expected:
            text += "\n" + i18n.t("correct_answer_prefix") + str(feedback.expected)
        self._show_feedback(text)
        self._banner.SetLabel(f"{feedback.title_ar}: {feedback.message_ar}")

        self._btn_confirm.Enable(False)
        self._btn_clear.Enable(False)
        for cell in self._cells:
            cell.Disable()
        if self._answer_box is not None:
            self._answer_box.Disable()
        self._btn_next.Show()
        self.Layout()
        # اجعل قارئ الشاشة يقرأ النتيجة.
        if self._feedback_box is not None:
            self._feedback_box.SetFocus()

    def _show_feedback(self, text: str) -> None:
        if self._feedback_box is None:
            return
        if text:
            self._feedback_box.SetValue(text)
            self._feedback_box.SetName(i18n.t("feedback_name_prefix") + text.split("\n")[0])
            self._feedback_box.Show()
        else:
            self._feedback_box.SetValue("")
            self._feedback_box.Hide()
        self.Layout()

    def _clear(self) -> None:
        for cell in self._cells:
            cell.clear()
        announce(self, i18n.t("cleared_announce"))

    def _next(self) -> None:
        if self._finished:
            self.frame.navigate_to("home")
            return
        self._index += 1
        self._show_current()
        self.finish_layout()

    # ------------------------------------------------------------------
    # النهاية
    # ------------------------------------------------------------------
    def _finish(self) -> None:
        correct = sum(1 for _, feedback in self._results if feedback.correct)
        total = len(self._results)
        lesson = self._lesson
        lvl_key = self._level.key if self._level else ""
        if self._mode != "matching":
            try:
                self.context.progress.finalize_session(
                    lesson, lvl_key, correct, total, self.context.mastery_threshold
                )
            except Exception:
                pass
        self.context.progress_changed.emit()
        pct = round(correct / total * 100.0, 1) if total else 0.0
        passed = bool(total) and pct >= self.context.mastery_threshold
        note = ""
        if self._mode == "placement":
            self._report_placement()
            note = "\n" + self._placement_note
        summary = (
            i18n.t("session_ended") + "\n"
            + i18n.t("session_correct").format(correct=correct, total=total, pct=pct) + "\n"
            + i18n.t("session_mastery").format(pct=int(round(self.context.mastery_threshold))) + "\n"
            + (i18n.t("session_great") if passed else i18n.t("session_keep")) + "\n"
            + i18n.t("session_saved")
            + note
        )
        self._finished = True
        self._end_text.SetLabel(summary)
        if self._question_box is not None:
            self._question_box.SetValue(summary)
            self._question_box.SetName(i18n.t("summary_title") + summary.split("\n")[0])
        self._show_feedback(summary)
        # احتفال عند إتمام الجلسة (يُعزّز إحساس الإنجاز، خاصة للطفل الكفيف).
        if passed:
            try:
                if bool(self.context.settings.get("encouragement_enabled", True)):
                    self.context.sounds.celebrate()
            except Exception:
                pass
        self._btn_confirm.Enable(False)
        self._btn_clear.Enable(False)
        for cell in self._cells:
            cell.Disable()
        if self._answer_box is not None:
            self._answer_box.Disable()
        self._btn_next.SetLabel(i18n.t("btn_finish_home"))
        self._btn_next.Show()
        self.Layout()
        self.context.speak_guidance(summary, self._lesson.language if self._lesson else "ar")
        if self._feedback_box is not None:
            self._feedback_box.SetFocus()

    # ------------------------------------------------------------------
    # واجهة الاختصارات
    # ------------------------------------------------------------------
    def focus_edit_box(self) -> bool:
        # إن كان هناك حقل إجابة ظاهرًا فالأولى التركيز عليه، وإلا صندوق السؤال.
        if self._answer_box is not None and self._answer_box.IsShown():
            self._answer_box.SetFocus()
            return True
        if self._question_box is not None:
            self._question_box.SetFocus()
            return True
        return False

    def _activate_focused_option(self) -> bool:
        """إن كان التركيز على زرّ خيار، اختره وأعد ``True``."""
        focused = wx.Window.FindFocus()
        if focused is not None and focused in self._option_buttons:
            try:
                index = self._option_buttons.index(focused)
            except ValueError:
                return False
            self._choose_option(index)
            return True
        return False

    def confirm_action(self) -> bool:
        if self._answered:
            self._next()
            return True
        if self._activate_focused_option():
            return True
        self._on_confirm()
        return True

    def on_enter(self) -> bool:
        """مفتاح الإدخال (Enter): تأكيد الإجابة أو الانتقال للسؤال التالي.

        هذا هو السلوك المطلوب صراحةً من المراجعة: التأكيد بمفتاح الإدخال وحده
        (دون الحاجة إلى Ctrl+Enter).
        """
        if self._finished:
            self.frame.navigate_to("home")
            return True
        if self._answered:
            self._next()
            return True
        # إن كان التركيز على أحد أزرار الخيارات، فليختر الإجابة المعروضة
        # (مفتاح الإدخال يختار الخيار تمامًا كما يفعل مفتاح المسافة).
        if self._activate_focused_option():
            return True
        self._on_confirm()
        return True

    def next_action(self) -> bool:
        if self._answered:
            self._next()
            return True
        return False

    def on_shortcut(self, key: str) -> bool:
        if key == "repeat":
            self.context.speech.repeat()
            return True
        if key == "clear":
            if self._cells and not self._answered:
                self._clear()
                return True
            return False
        if key.startswith("dot") and key[3:].isdigit():
            if self._answered or not self._cells:
                return False
            dot = int(key[3:])
            target = None
            for cell in self._cells:
                if cell.HasFocus():
                    target = cell
                    break
            if target is None:
                target = self._cells[0]
            target.SetFocus()
            target.toggle_dot(dot)
            return True
        return False

    def on_theme_changed(self) -> None:
        theme = self.theme
        try:
            if self._stimulus_view is not None:
                self._stimulus_view.set_theme(theme)
                self._stimulus_view.set_scale(theme.cell_scale())
            for cell in self._cells:
                cell.set_theme(theme)
                cell.set_scale(theme.cell_scale())
            if self._braille_label is not None:
                self._braille_label.SetFont(theme.make_braille_font(30.0))
            if self._target_label is not None:
                target_font = theme.make_font(20.0)
                target_font.SetWeight(wx.FONTWEIGHT_BOLD)
                self._target_label.SetFont(target_font)
        except Exception:
            pass
        self.Refresh()
