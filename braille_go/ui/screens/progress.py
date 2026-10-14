"""شاشة متابعة التقدّم."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from ...core.curriculum import all_lessons, LEVELS
from ..widgets import Card, LabeledProgress, StatsGrid, body_label, button
from .base import BaseScreen


class ProgressScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title="متابعة التقدّم")
        self.setLayoutDirection(Qt.RightToLeft)

        self._overall = LabeledProgress("التقدّم العام")
        self.layout.addWidget(self._overall)

        self._stats = StatsGrid()
        self.layout.addWidget(self._stats)

        self._per_level = QVBoxLayout()
        self.layout.addLayout(self._per_level)

        btn_reset = button("إعادة ضبط كل التقدّم", danger=True, on_click=self._reset, tooltip="يُحذف كل ما تم حفظه من دروس ونتائج.")
        self.layout.addWidget(btn_reset)
        self.layout.addStretch(1)

    def activate(self, **kwargs) -> None:
        self._stats.clear()
        stats = self.context.progress.statistics()
        self._overall.set_value(float(stats["accuracy"]), f"التقدّم العام ({int(round(stats['accuracy']))}%)")
        self._stats.add_row("إجابات صحيحة", f"{stats['answers_correct']}/{stats['answers_total']}")
        self._stats.add_row("الدروس التي جُرّبت", str(stats["lessons_attempted"]))
        self._stats.add_row("الدروس المكتملة", str(stats["lessons_completed"]))
        self._stats.add_row("نسبة الإتقان المطلوبة", f"{int(round(self.context.mastery_threshold))}%")

        # clear level widgets
        while self._per_level.count():
            item = self._per_level.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for level in LEVELS:
            ev = self.context.evaluate(level)
            card = Card(f"المستوى {level.number}: {ev.mastery:.0f}%")
            body = body_label(f"مكتمل {ev.lessons_completed}/{ev.lessons_total}. {ev.reason_ar}")
            card.add(body)
            self._per_level.addWidget(card)

    def _reset(self) -> None:
        from ..widgets import confirm

        if confirm(self, "تأكيد إعادة الضبط", "هل تريد حذف كل بيانات التقدّم والإعدادات والنتائج؟ هذا الإجراء لا يمكن التراجع عنه."):
            self.context.progress.reset_all()
            try:
                self.context.settings.reset()
            except Exception:
                pass
            self.activate()
