"""شاشة الترحيب مع نطق تلقائي."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget

from ...core import i18n
from .base import BaseScreen


class WelcomeScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title="")
        lang = context.settings.get('ui_language', 'ar')
        self.setLayoutDirection(Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight)
        layout = QVBoxLayout(self)
        layout.addStretch(1)

        self._title = QLabel(i18n.t("welcome"))
        self._title.setObjectName("screenTitle")
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setStyleSheet("font-size: 48px; font-weight: bold;")
        layout.addWidget(self._title)

        self._subtitle = QLabel(i18n.t("welcome_subtitle"))
        self._subtitle.setAlignment(Qt.AlignCenter)
        self._subtitle.setStyleSheet("font-size: 20px; margin-top: 15px; color: #4a4a4a;")
        layout.addWidget(self._subtitle)

        layout.addStretch(1)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._go_home)

    def activate(self, **kwargs) -> None:
        try:
            self.context.speak(i18n.t("welcome_speak"), self.context.settings.get("speech_locale") or None)
        except Exception:
            pass
        try:
            self.context.settings.set('welcome_shown', True)
        except Exception:
            pass
        self._timer.start(2500)

    def _go_home(self) -> None:
        from ..main_window import ScreenId
        self.window.navigate_to(ScreenId.HOME)
