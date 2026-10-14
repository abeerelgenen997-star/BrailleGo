"""شاشة تنفيذ الدرس مع خلايا برايل وتغذية راجعة."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ...core.curriculum import LEVELS_BY_KEY, LESSONS_BY_KEY, level_of_lesson
from ...core.exercises import AnswerMode
from ...services.accessibility import announce, announce_alert, describe_braille_cell
from ..braille_cell_widget import BrailleCellInput, BrailleCellsView
from ..main_window import ScreenId
from ..widgets import (
    BrailleUnicodeLabel,
    Card,
    StatusBanner,
    body_label,
    button,
    informational,
)
from .base import BaseScreen


class LessonScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title="درس")
        self.setLayoutDirection(Qt.RightToLeft)

        self._banner = StatusBanner()
        self.layout.addWidget(self._banner)

        self._intro = body_label("")
        self.layout.addWidget(self._intro)

        self._stimulus_box = Card("المحفّز")
        self._stimulus_text = QLabel("")
        self._stimulus_text.setWordWrap(True)
        self._stimulus_text.setAccessibleName("النص المعروض")
        self._stimulus_view = BrailleCellsView(scale=1.2)
        self._braille_label = BrailleUnicodeLabel(point_size=26.0)
        self._stimulus_box.add(self._stimulus_text)
        self._stimulus_box.add(self._stimulus_view)
        self._stimulus_box.add(self._braille_label)
        self.layout.addWidget(self._stimulus_box)

        self._prompt = body_label("", wrap=True)
        self.layout.addWidget(self._prompt)

        self._cell_box = Card("خلية برايل التفاعلية")
        self._cell = BrailleCellInput(scale=1.4)
        self._cell.confirmed.connect(self._on_confirm)
        self._cell_box.add(self._cell)
        self.layout.addWidget(self._cell_box)

        # options (for CHOOSE_TEXT / CHOOSE_PATTERN)
        self._options_box = Card("الخيارات")
        self._options = QVBoxLayout()
        self._options_box.add_layout(self._options)
        self._options_box.setVisible(False)
        self.layout.addWidget(self._options_box)

        self._action_bar = QHBoxLayout()
        self._btn_clear = button("مسح النقاط", on_click=self._clear)
        self._btn_confirm = button("تأكيد الإجابة", primary=True, on_click=self._on_confirm)
        self._btn_next = button("السؤال التالي", on_click=self._next)
        self._action_bar.addWidget(self._btn_clear)
        self._action_bar.addWidget(self._btn_confirm)
        self._action_bar.addStretch(1)
        self._action_bar.addWidget(self._btn_next)
        self.layout.addLayout(self._action_bar)

        self._feedback_box = Card("تغذية راجعة")
        self._feedback_title = QLabel("")
        self._feedback_msg = body_label("")
        self._explain = body_label("", wrap=True)
        self._feedback_box.add(self._feedback_title)
        self._feedback_box.add(self._feedback_msg)
        self._feedback_box.add(self._explain)
        self._feedback_box.setVisible(False)
        self.layout.addWidget(self._feedback_box)

        self._end_box = Card("انتهت الجلسة")
        self._end_text = body_label("")
        self._end_box.add(self._end_text)
        self._end_box.setVisible(False)
        self.layout.addWidget(self._end_box)

        self.layout.addStretch(1)

        # state
        self._lesson = None
        self._level = None
        self._exercises = []
        self._index = 0
        self._results: list[tuple] = []
        self._mode = ""

    def activate(self, **kwargs) -> None:
        lesson_key = kwargs.get("lesson_key", "")
        level_key = kwargs.get("level_key", "")
        self._mode = kwargs.get("mode", "")
        self._lesson = LESSONS_BY_KEY.get(lesson_key)
        self._level = LEVELS_BY_KEY.get(level_key) or level_of_lesson(lesson_key)
        self._exercises = []
        self._index = 0
        self._results = []
        self._hide_feedback()
        self._end_box.setVisible(False)
        self._cell.clear()
        self._cell.setFocus(Qt.TabFocusReason)

        if not self._lesson:
            self._intro.setText("درس غير معروف.")
            return

        self.set_title(self._lesson.title_ar)
        self._intro.setText(self._lesson.description_ar or self._lesson.intro_ar or "")

        # generate
        if self._mode == "review":
            keys = self.context.needs_review_symbols(limit=10)
            self._exercises = self.context.generator.generate_review("review_lesson", keys, count=8)
        elif self._mode == "exam":
            self._exercises = self.context.generate_exercises(self._lesson, count=self._lesson.exercise_count)
        elif self._mode == "mixed":
            self._exercises = self.context.generate_exercises(self._lesson, count=6)
        else:
            self._exercises = self.context.generate_exercises(self._lesson, count=self._lesson.exercise_count)
        if not self._exercises:
            informational(self, "لا توجد تدريبات", "لا يمكن توليد تدريبات لهذا الدرس في الوقت الحالي.")
            return
        self._show_current()

    def _show_current(self) -> None:
        if self._index >= len(self._exercises):
            self._finish()
            return
        ex = self._exercises[self._index]
        self._prompt.setText(ex.prompt_ar)
        self._stimulus_text.setText(ex.stimulus_text)
        # show braille
        from ...core.braille import unicode_to_cells

        if ex.stimulus_braille:
            cells = unicode_to_cells(ex.stimulus_braille)
            self._stimulus_view.set_cells(cells)
            self._braille_label.set_pattern(ex.stimulus_braille)
        else:
            self._stimulus_view.set_cells(())
            self._braille_label.setText("")
        self._cell.clear()
        # options
        self._clear_options()
        if ex.answer_mode in (AnswerMode.CHOOSE_TEXT, AnswerMode.CHOOSE_PATTERN):
            self._options_box.setVisible(True)
            for i, opt in enumerate(ex.options):
                lbl = opt
                if ex.option_labels:
                    lbl = ex.option_labels[i]
                b = button(lbl, on_click=lambda idx=i: self._choose_option(idx))
                b.setObjectName("choice")
                self._options.addWidget(b)
        else:
            self._options_box.setVisible(False)
        self._hide_feedback()
        self._btn_next.setVisible(False)
        self._banner.setVisible(False)
        self.context.speak_guidance(ex.speak_prompt(), ex.language)
        QTimer.singleShot(0, lambda: self._cell.setFocus(Qt.TabFocusReason))

    def _clear_options(self) -> None:
        while self._options.count():
            item = self._options.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _choose_option(self, idx: int) -> None:
        if self._index >= len(self._exercises):
            return
        ex = self._exercises[self._index]
        fb = self.context.grade(ex, idx)
        self._record_and_show(ex, fb)

    def _on_confirm(self) -> None:
        if self._index >= len(self._exercises):
            return
        ex = self._exercises[self._index]
        resp = self._cell.cell()
        fb = self.context.grade(ex, resp.dots)
        self._record_and_show(ex, fb)

    def _record_and_show(self, ex, fb) -> None:
        lvl_key = self._level.key if self._level else (ex.lesson_key.split("_")[0] if "_" in ex.lesson_key else ex.lesson_key)
        try:
            self.context.progress.record_answer(ex, fb, lvl_key, ex.lesson_key)
        except Exception:
            pass
        self._results.append((ex, fb))
        self._show_feedback(fb, ex)
        self._btn_confirm.setEnabled(False)
        self._btn_clear.setEnabled(False)
        self._cell.setEnabled(False)
        self._btn_next.setVisible(True)
        if fb.correct:
            announce_alert(self._cell, "إجابة صحيحة")
        else:
            announce_alert(self._cell, "إجابة غير صحيحة")
        self.context.speak(fb.spoken, ex.language)

    def _show_feedback(self, fb, ex) -> None:
        self._feedback_box.setVisible(True)
        self._feedback_title.setText(fb.title_ar)
        self._feedback_msg.setText(fb.message_ar)
        self._explain.setText(fb.explanation_ar or "")
        tone = "ok" if fb.correct else "error"
        self._banner.show_message(f"{fb.title_ar}: {fb.message_ar}", tone=tone)

    def _hide_feedback(self) -> None:
        self._feedback_box.setVisible(False)
        self._btn_confirm.setEnabled(True)
        self._btn_clear.setEnabled(True)
        self._cell.setEnabled(True)

    def _clear(self) -> None:
        self._cell.clear()
        announce(self._cell, "تم مسح النقاط. الخلية فارغة.")

    def _next(self) -> None:
        self._index += 1
        self._cell.clear()
        self._show_current()

    def _finish(self) -> None:
        correct = sum(1 for _, fb in self._results if fb.correct)
        total = len(self._results)
        lesson = self._lesson
        lvl_key = self._level.key if self._level else ""
        try:
            self.context.progress.finalize_session(lesson, lvl_key, correct, total, self.context.mastery_threshold)
        except Exception:
            pass
        self.context.progress_changed.emit()
        pct = round(correct / total * 100.0, 1) if total else 0.0
        self._end_box.setVisible(True)
        self._end_text.setText(
            f"انتهت الجلسة.\nالإجابات الصحيحة: {correct} من {total} ({pct}%).\nتم حفظ التقدّم محليًا."
        )
        informational(self, "انتهت الجلسة", self._end_text.text())
        QTimer.singleShot(800, lambda: self.window.navigate_to(ScreenId.HOME))
