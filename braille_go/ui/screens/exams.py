"""شاشة الاختبارات."""

from __future__ import annotations

from PySide6.QtCore import Qt

from ..widgets import Card, body_label, button
from .base import BaseScreen


class ExamsScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title="الاختبارات")
        self.setLayoutDirection(Qt.RightToLeft)

        card = Card("اختبارات المستويات")
        card.add(body_label("اختر مستوى لتقدّم لاختباره (يجب إكمال الدروس حسب شروط الإتقان)."))
        from ...core.curriculum import LEVELS
        for level in LEVELS:
            ev = self.context.evaluate(level)
            unlocked = self.context.is_level_unlocked(level.key)
            b = button(
                f"المستوى {level.number}: {level.title_ar} — إتقان {int(round(ev.mastery))}%",
                on_click=lambda lk=None, lv=level.key: self.window.navigate_to("lesson", lesson_key=self._exam_lesson(lv), level_key=lv, mode="exam"),
                enabled=unlocked,
            )
            card.add(b)
        self.layout.addWidget(card)
        self.layout.addStretch(1)

    def _exam_lesson(self, level_key: str):
        from ...core.curriculum import LEVELS_BY_KEY
        lvl = LEVELS_BY_KEY.get(level_key)
        if not lvl:
            return ""
        for l in lvl.lessons:
            if l.is_exam:
                return l.key
        return lvl.lessons[-1].key if lvl.lessons else ""
