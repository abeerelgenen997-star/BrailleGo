"""شاشة التدريب العام."""

from __future__ import annotations

from PySide6.QtCore import Qt

from ..widgets import Card, body_label, button
from .base import BaseScreen


class PracticeScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title="التدريب العام")
        self.setLayoutDirection(Qt.RightToLeft)

        card = Card("مراجعة مركّزة")
        card.add(body_label(
            "يولّد التدريب مراجعة على الرموز الأكثر خطأً لديك. "
            "إذا لم توجد أخطاء بعد، سيعرض تطبيقًا عشوائيًا على الحروف العربية الأساسية."
        ))
        card.add(button("ابدأ تدريب المراجعة", primary=True, on_click=self._review))
        self.layout.addWidget(card)

        card2 = Card("تدريب عشوائي")
        card2.add(body_label("ابدأ تمرينًا مختلطًا من أول درس متاح."))
        card2.add(button("ابدأ تدريب عشوائي", on_click=self._mixed))
        self.layout.addWidget(card2)
        self.layout.addStretch(1)

    def _review(self) -> None:
        from ...core.curriculum import first_lesson, level_of_lesson
        lesson = first_lesson()
        level = level_of_lesson(lesson.key)
        self.window.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key if level else "", mode="review")

    def _mixed(self) -> None:
        from ...core.curriculum import first_lesson, level_of_lesson
        lesson = first_lesson()
        level = level_of_lesson(lesson.key)
        self.window.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key if level else "", mode="mixed")
