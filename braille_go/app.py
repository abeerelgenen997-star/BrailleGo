"""مدخل التطبيق الرئيسي (QApplication)."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .app_context import build_context
from .ui.main_window import MainWindow
from .ui.theme import apply_theme


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Braille Go")
    app.setApplicationDisplayName("Braille Go")
    app.setOrganizationName("BrailleGo")
    app.setOrganizationDomain("braillego.local")

    context = build_context()
    apply_theme(app, context.settings)
    window = MainWindow(context)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
