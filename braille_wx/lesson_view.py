"""شاشة تنفيذ الدرس/الاختبار لنسخة wxPython.

تركّز هذه الشاشة على ملاحظة المراجع الأولى: **صندوق كتابة (Edit Box) لقراءة
السؤال** يكون قابلًا للتركيز بالكامل مع قارئات الشاشة. عند ظهور كل سؤال
يُوضع التركيز تلقائيًا على هذا الصندوق، ويمكن العودة إليه في أي وقت بالاختصار
**Ctrl+E**. كما يوجد حقل إدخال إجابة حقيقي (Edit Box) لأسئلة الكتابة.
"""

from __future__ import annotations

import wx

from braille_go.core.curriculum import LEVELS_BY_KEY, LESSONS_BY_KEY, level_of_lesson
from braille_go.core.exercises import AnswerMode

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
        self._answered = False
        self._finished = False

        # عناصر تُبنى عند التنشيط.
        self._title: wx.StaticText | None = None
        self._banner: wx.StaticText | None = None
        self._intro: wx.StaticText | None = None
        self._question_box: wx.TextCtrl | None = None
        self._stimulus_view: BrailleCellsView | None = None
        self._braille_label: wx.StaticText | None = None
        self._options_sizer: wx.Sizer | None = None
        self._options_panel: wx.Panel | None = None
        self._answer_box: wx.TextCtrl | None = None
        self._cells: list[BrailleCellInput] = []
        self._cells_panel: wx.Panel | None = None
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

        self._title = W.heading(self, "درس", theme)
        self.content.Add(self._title, 0, wx.ALL, 8)

        self._banner = wx.StaticText(self, label="")
        self._banner.SetName("شريط الحالة")
        self.content.Add(self._banner, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self._intro = W.wrapped_text(self, "")
        self.content.Add(self._intro, 0, wx.EXPAND | wx.ALL, 10)

        # صندوق السؤال (Edit Box قابل للقراءة الكاملة) -----------------
        qbox, qsizer = W.card(self, self.content, "نص السؤال (قابل للقراءة بقارئ الشاشة)")
        self._question_box = W.read_only_box(qbox, multiline=True, height=90, name="نص السؤال")
        qsizer.Add(self._question_box, 1, wx.EXPAND | wx.ALL, 4)
        hint = W.body(qbox, "للرجوع إلى هذا الحقل في أي وقت اضغط Ctrl+E.")
        qsizer.Add(hint, 0, wx.ALL, 4)

        # المحفّز (نمط برايل للقراءة) ----------------------------------
        sbox, ssizer = W.card(self, self.content, "المطلوب قراءته")
        self._stimulus_view = BrailleCellsView(sbox, scale=self.theme.cell_scale(), theme=theme)
        ssizer.Add(self._stimulus_view, 0, wx.ALL | wx.ALIGN_CENTER, 6)
        self._braille_label = wx.StaticText(sbox, label="")
        self._braille_label.SetName("نمط برايل كنص")
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
        abox, asizer = W.card(self, self.content, "حقل إدخال الإجابة")
        self._answer_box = W.editable_box(abox, name="حقل إدخال الإجابة", on_enter=self._on_confirm)
        asizer.Add(self._answer_box, 0, wx.EXPAND | wx.ALL, 4)
        self._answer_box.Hide()

        # خلايا البناء -------------------------------------------------
        self._cells_panel = wx.Panel(self)
        cells_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cells_panel.SetSizer(cells_sizer)
        self.content.Add(self._cells_panel, 0, wx.EXPAND | wx.ALL, 8)

        # شريط الأزرار -------------------------------------------------
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_clear = W.action_button(self, "مسح النقاط", on_click=self._clear, tooltip="Ctrl+Delete")
        self._btn_confirm = W.action_button(self, "تأكيد الإجابة", on_click=self._on_confirm, primary=True, tooltip="Ctrl+Enter")
        self._btn_next = W.action_button(self, "السؤال التالي", on_click=self._next, tooltip="Ctrl+N")
        self._btn_next.Hide()
        buttons.Add(self._btn_clear, 0, wx.RIGHT, 8)
        buttons.Add(self._btn_confirm, 0, wx.RIGHT, 8)
        buttons.Add((0, 0), 1, wx.EXPAND)
        buttons.Add(self._btn_next, 0)
        self.content.Add(buttons, 0, wx.EXPAND | wx.ALL, 8)

        # التغذية الراجعة ----------------------------------------------
        fbox, fsizer = W.card(self, self.content, "نتيجة الإجابة")
        self._feedback_box = W.read_only_box(fbox, multiline=True, height=110, name="نتيجة الإجابة")
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
        self._btn_next.SetLabel("السؤال التالي")
        self._btn_next.Hide()
        self._btn_confirm.Enable(True)
        self._btn_clear.Enable(True)
        if self._answer_box is not None:
            self._answer_box.SetValue("")
            self._answer_box.Enable(True)

        if not self._lesson:
            self._intro.SetLabel("درس غير معروف.")
            return
        self._title.SetLabel(self._lesson.title_ar)
        self._title.SetName(self._lesson.title_ar)
        self._intro.SetLabel(self._lesson.description_ar or self._lesson.intro_ar or "")

        if self._mode == "review":
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
            message = "لا يمكن توليد تدريبات لهذا الدرس في الوقت الحالي. جرّب درسًا آخر."
            self._end_text.SetLabel(message)
            self._question_box.SetValue(message)
            self._question_box.SetFocus()
            self._btn_confirm.Enable(False)
            self._btn_clear.Enable(False)
            return
        self._show_current()
        self.finish_layout()

    # ------------------------------------------------------------------
    # العرض
    # ------------------------------------------------------------------
    def _show_current(self) -> None:
        if self._index >= len(self._exercises):
            self._finish()
            return
        ex = self._exercises[self._index]
        self._answered = False

        # صندوق السؤال: النص الكامل الذي يقرأه قارئ الشاشة.
        question_text = ex.prompt_ar
        if ex.show_target_text and ex.stimulus_text:
            question_text += "\nالمطلوب: " + ex.stimulus_text
        if self._question_box is not None:
            self._question_box.SetValue(question_text)
            self._question_box.SetName("نص السؤال: " + ex.prompt_ar)

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
            for i, opt in enumerate(ex.options):
                label = ex.option_labels[i] if ex.option_labels and i < len(ex.option_labels) else opt
                button = W.action_button(
                    self._options_panel, label,
                    on_click=lambda idx=i: self._choose_option(idx),
                    name=f"خيار {i + 1}: {label}",
                )
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

        self._show_feedback("")
        self._btn_next.Hide()
        self._btn_confirm.Enable(True)
        self._btn_clear.Enable(True)
        self._banner.SetLabel("")

        self.context.speak_guidance(ex.speak_prompt(), ex.language)

        # التركيز على صندوق السؤال أو حقل الإجابة.
        wx.CallAfter(self._focus_initial)

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
            caption = W.body(self._cells_panel, f"الخلية {i + 1}")
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
                self._banner.SetLabel("اكتب إجابة في الحقل ثم اضغط تأكيد (Ctrl+Enter).")
                announce(self, "اكتب إجابة أولًا.")
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
        self.context.speak(feedback.spoken, ex.language)

        text = feedback.title_ar
        if feedback.message_ar:
            text += "\n" + feedback.message_ar
        if feedback.explanation_ar:
            text += "\n" + feedback.explanation_ar
        if not feedback.correct and feedback.expected:
            text += f"\nالإجابة الصحيحة: {feedback.expected}"
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
            self._feedback_box.SetName("نتيجة الإجابة: " + text.split("\n")[0])
            self._feedback_box.Show()
        else:
            self._feedback_box.SetValue("")
            self._feedback_box.Hide()
        self.Layout()

    def _clear(self) -> None:
        for cell in self._cells:
            cell.clear()
        announce(self, "تم مسح النقاط. الخلية فارغة.")

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
        try:
            self.context.progress.finalize_session(
                lesson, lvl_key, correct, total, self.context.mastery_threshold
            )
        except Exception:
            pass
        self.context.progress_changed.emit()
        pct = round(correct / total * 100.0, 1) if total else 0.0
        summary = (
            f"انتهت الجلسة.\n"
            f"الإجابات الصحيحة: {correct} من {total} ({pct}%).\n"
            f"نسبة الإتقان المطلوبة: {int(round(self.context.mastery_threshold))}%.\n"
            f"{'أحسنت! أتممت الدرس.' if total and pct >= self.context.mastery_threshold else 'واصل التدريب لتحقيق نسبة الإتقان.'}\n"
            "تم حفظ التقدّم محليًا."
        )
        self._finished = True
        self._end_text.SetLabel(summary)
        if self._question_box is not None:
            self._question_box.SetValue(summary)
            self._question_box.SetName("ملخّص الجلسة: " + summary.split("\n")[0])
        self._show_feedback(summary)
        self._btn_confirm.Enable(False)
        self._btn_clear.Enable(False)
        for cell in self._cells:
            cell.Disable()
        if self._answer_box is not None:
            self._answer_box.Disable()
        self._btn_next.SetLabel("إنهاء والعودة إلى الرئيسية")
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

    def confirm_action(self) -> bool:
        if self._answered:
            self._next()
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
        except Exception:
            pass
        self.Refresh()
