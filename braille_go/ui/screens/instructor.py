"""وضع المدرب - مراقبة الطلاب وتصدير التقارير."""

from __future__ import annotations

import csv
import os
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
)

from ...core import i18n
from ..widgets import Card, body_label, button
from .base import BaseScreen


class InstructorScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title=i18n.t("instructor"))
        lang = context.settings.get('ui_language', 'ar')
        self.setLayoutDirection(Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels([
            i18n.t("user_name"),
            i18n.t("overall_progress"),
            i18n.t("completed_lessons"),
            i18n.t("accuracy"),
            i18n.t("needs_review"),
        ])
        self.layout.addWidget(self._table)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self._btn_export = button(i18n.t("export_csv"), primary=True, on_click=self._export_csv)
        btns.addWidget(self._btn_export)
        self.layout.addLayout(btns)
        self.layout.addStretch(1)

    def activate(self, **kwargs) -> None:
        try:
            from ...data.users import UserManager
            um = UserManager(self.context.database)
            users = um.list_users()
        except Exception:
            users = []

        self._table.setRowCount(0)
        for user in users:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(user.name))
            # بيانات مبسطة
            stats = self.context.progress.statistics()
            self._table.setItem(row, 1, QTableWidgetItem(f"{int(stats['accuracy'])}%"))
            self._table.setItem(row, 2, QTableWidgetItem(str(stats['lessons_completed'])))
            self._table.setItem(row, 3, QTableWidgetItem(f"{int(stats['accuracy'])}%"))
            wrong = self.context.progress.recent_wrong_symbols(limit=5)
            self._table.setItem(row, 4, QTableWidgetItem(",".join(wrong[:3])))
        self._table.resizeColumnsToContents()

    def _export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            i18n.t("export_csv"),
            f"braille_go_class_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)",
        )
        if not path:
            return
        try:
            from ...data.users import UserManager
            um = UserManager(self.context.database)
            users = um.list_users()
            stats = self.context.progress.statistics()
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(['Student', 'Overall%', 'CompletedLessons', 'Accuracy%', 'WrongSymbols'])
                for user in users:
                    wrong = self.context.progress.recent_wrong_symbols(limit=5)
                    w.writerow([user.name, int(stats['accuracy']), stats['lessons_completed'], int(stats['accuracy']), ','.join(wrong)])
        except Exception:
            pass
