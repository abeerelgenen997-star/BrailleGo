"""أساس الشاشات مع بعض المساعدات."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout

from ...app_context import AppContext
from ..widgets import screen_title


class BaseScreen(QWidget):
    def __init__(self, context: AppContext, window, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._context = context
        self._window = window
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(16, 10, 16, 10)
        self._root.setSpacing(12)
        if title:
            self._title_label = screen_title(title)
            self._root.addWidget(self._title_label)
        else:
            self._title_label = screen_title("")
            self._title_label.setVisible(False)
            self._root.addWidget(self._title_label)

    @property
    def context(self) -> AppContext:
        return self._context

    @property
    def window(self):
        return self._window

    @property
    def layout(self) -> QVBoxLayout:
        return self._root

    def activate(self, **kwargs) -> None:
        pass

    def set_title(self, title: str) -> None:
        self._title_label.setText(title)
        self._title_label.setVisible(bool(title))
        self._title_label.setAccessibleName(title)


def base_screen() -> BaseScreen:  # pragma: no cover - helper
    raise NotImplementedError


def route(screen_id: str) -> None:  # pragma: no cover - helper
    pass
