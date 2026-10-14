"""شاشة مراجعة الأخطاء السابقة."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from ..widgets import Card, body_label, button
from .base import BaseScreen


class ReviewScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title="مراجعة الأخطاء السابقة")
        self.setLayoutDirection(Qt.RightToLeft)
        self._list = QVBoxLayout()
        self.layout.addLayout(self._list)

    def activate(self, **kwargs) -> None:
        while self._list.count():
            item = self._list.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        wrong = self.context.progress.wrong_answers(limit=30)
        if not wrong:
            card = Card("لا توجد أخطاء محفوظة بعد")
            card.add(body_label("بعد الإجابة على التدريبات ستظهر هنا قائمة الأخطاء لسهولة المراجعة."))
            self._list.addWidget(card)
            return
        for row in wrong:
            card = Card(row["lesson_key"])
            text = (
                f"التاريخ: {row['created_at']}\n"
                f"نوع التدريب: {row['kind']}\n"
                f"الرموز: {row['symbol_keys']}\n"
                f"ما أجبت به: {row['given']}\n"
                f"الإجابة الصحيحة: {row['expected']}"
            )
            card.add(body_label(text))
            self._list.addWidget(card)
        self._list.addStretch(1)
