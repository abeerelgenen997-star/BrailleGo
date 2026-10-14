"""الشاشة الرئيسية."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout

from ...core.curriculum import first_lesson, level_of_lesson
from ..main_window import ScreenId
from ..widgets import Card, ButtonColumn, body_label, button
from .base import BaseScreen


class HomeScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title="Braille Go")
        self.setLayoutDirection(Qt.RightToLeft)

        top = body_label(
            "تعلّم برايل العربي والإنجليزي بطريقة تفاعلية، مع نظام مستويات وتقدّم وحفظ محلي."
        )
        self.layout.addWidget(top)

        grid = QHBoxLayout()
        grid.setSpacing(12)

        learn_card = Card("التعلّم")
        btn_start = button(
            "بدء التعلم",
            primary=True,
            on_click=self._start_learning,
            tooltip="ابدأ من أول درس في المنهج.",
        )
        btn_continue = button("استكمال آخر درس", on_click=self._continue_last)
        btn_lessons = button("الدروس والمستويات", on_click=self._lessons)
        col = ButtonColumn()
        col.add(btn_start)
        col.add(btn_continue)
        col.add(btn_lessons)
        col.add_stretch()
        learn_card.add(col)
        grid.addWidget(learn_card)

        practice_card = Card("التدريب")
        col2 = ButtonColumn()
        col2.add(button("التدريب العام", on_click=lambda: self.window.navigate_to(ScreenId.PRACTICE)))
        col2.add(button("الاختبارات", on_click=lambda: self.window.navigate_to(ScreenId.EXAMS)))
        col2.add(button("مراجعة الأخطاء", on_click=lambda: self.window.navigate_to(ScreenId.REVIEW)))
        col2.add_stretch()
        practice_card.add(col2)
        grid.addWidget(practice_card)

        track_card = Card("متابعة")
        col3 = ButtonColumn()
        col3.add(button("متابعة التقدّم", on_click=lambda: self.window.navigate_to(ScreenId.PROGRESS)))
        col3.add(button("الإعدادات", on_click=lambda: self.window.navigate_to(ScreenId.SETTINGS)))
        col3.add(button("المساعدة ودليل الاستخدام", on_click=lambda: self.window.navigate_to(ScreenId.HELP)))
        col3.add_stretch()
        track_card.add(col3)
        grid.addWidget(track_card)

        self.layout.addLayout(grid)
        self.layout.addStretch(1)

    def _start_learning(self) -> None:
        lesson = first_lesson()
        level = level_of_lesson(lesson.key)
        self.window.navigate_to(ScreenId.LESSON, lesson_key=lesson.key, level_key=level.key if level else "")

    def _continue_last(self) -> None:
        lesson = self.context.last_lesson()
        level = level_of_lesson(lesson.key)
        self.window.navigate_to(ScreenId.LESSON, lesson_key=lesson.key, level_key=level.key if level else "")

    def _lessons(self) -> None:
        self.window.navigate_to(ScreenId.LESSONS)
