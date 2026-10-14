"""شاشة الدروس والمستويات."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from ...core.curriculum import LEVELS
from ..main_window import ScreenId
from ..widgets import Card, body_label, button
from .base import BaseScreen


class LessonsScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title="الدروس والمستويات")
        self.setLayoutDirection(Qt.RightToLeft)
        self.layout.addStretch(0)

    def activate(self, **kwargs) -> None:
        # clear
        while self.layout.count() > 1:
            item = self.layout.takeAt(1)
            w = item.widget()
            if w:
                w.deleteLater()
        for level in LEVELS:
            unlocked = self.context.is_level_unlocked(level.key)
            evalr = self.context.evaluate(level)
            card = Card(f"{level.number}. {level.title_ar}")
            desc = body_label(f"{level.description_ar}\nمكتمل: {evalr.lessons_completed}/{evalr.lessons_total}  |  إتقان: {int(round(evalr.mastery))}%")
            card.add(desc)
            col = QVBoxLayout()
            for lesson in level.lessons:
                lres = self.context.progress.lesson_result(lesson.key)
                status = "✓ مكتمل" if lres.completed else ("مُجرّب" if lres.attempts > 0 else "جديد")
                b = button(
                    f"{lesson.title_ar} — {status}",
                    on_click=lambda lk=lesson.key, lv=level.key: self.window.navigate_to(
                        ScreenId.LESSON, lesson_key=lk, level_key=lv
                    ),
                    enabled=unlocked,
                    tooltip=lesson.description_ar,
                )
                col.addWidget(b)
            card.add_layout(col)
            self.layout.addWidget(card)
        self.layout.addStretch(1)
