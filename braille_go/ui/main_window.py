"""النافذة الرئيسية وتوجيه التنقل بين الشاشات.

The UI is a simple, stacked window (QStackedWidget).  All navigation happens via
explicit methods with Arabic labels, and focus is moved to the top of the new
screen whenever we switch views so that screen readers start reading at the
right place.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..app_context import AppContext
from .theme import apply_theme
from .widgets import button


class ScreenId(str, Enum):
    HOME = "home"
    LESSONS = "lessons"
    LESSON = "lesson"
    PRACTICE = "practice"
    EXAMS = "exams"
    REVIEW = "review"
    PROGRESS = "progress"
    SETTINGS = "settings"
    HELP = "help"


class HeaderBar(QWidget):
    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._context = context
        self.setObjectName("headerBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        self._title = QLabel("Braille Go")
        self._title.setAccessibleName("Braille Go")
        self._title.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._title)

        layout.addStretch(1)
        self._status = QLabel("التقدّم 0%")
        self._status.setAccessibleName("شريط التقدّم العام 0%")
        self._status.setObjectName("muted")
        layout.addWidget(self._status)

        self._btn_home = button("الرئيسية", on_click=self._go_home)
        self._btn_help = button("المساعدة", on_click=self._go_help)
        layout.addWidget(self._btn_home)
        layout.addWidget(self._btn_help)

    def _go_home(self) -> None:
        window = self.window()
        if isinstance(window, MainWindow):
            window.navigate_to(ScreenId.HOME)

    def _go_help(self) -> None:
        window = self.window()
        if isinstance(window, MainWindow):
            window.navigate_to(ScreenId.HELP)

    def update_progress(self) -> None:
        pct = self._context.overall_progress_percent()
        text = f"التقدّم العام {int(round(pct))}%"
        self._status.setText(text)
        self._status.setAccessibleName(text)


class MainWindow(QMainWindow):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context
        self.setWindowTitle("Braille Go - تعلّم برايل")
        self.setMinimumSize(960, 680)
        self.setLayoutDirection(Qt.RightToLeft)

        central = QFrame(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header = HeaderBar(context)
        root.addWidget(self._header)

        self._stack = QStackedWidget()
        root.addWidget(self._stack)

        # Load screens (lazy import to avoid circulars)
        from .screens import (
            ExamsScreen,
            HelpScreen,
            HomeScreen,
            LessonScreen,
            LessonsScreen,
            PracticeScreen,
            ProgressScreen,
            ReviewScreen,
            SettingsScreen,
        )

        self._screens = {
            ScreenId.HOME: HomeScreen(context, self),
            ScreenId.LESSONS: LessonsScreen(context, self),
            ScreenId.LESSON: LessonScreen(context, self),
            ScreenId.PRACTICE: PracticeScreen(context, self),
            ScreenId.EXAMS: ExamsScreen(context, self),
            ScreenId.REVIEW: ReviewScreen(context, self),
            ScreenId.PROGRESS: ProgressScreen(context, self),
            ScreenId.SETTINGS: SettingsScreen(context, self),
            ScreenId.HELP: HelpScreen(context, self),
        }

        for sid, screen in self._screens.items():
            self._stack.addWidget(screen)

        self._stack.setCurrentIndex(0)
        QTimer.singleShot(0, self._on_first_show)

    def _on_first_show(self) -> None:
        self._header.update_progress()
        self._focus_top()
        self.navigate_to(ScreenId.HOME)

    def navigate_to(self, screen_id: ScreenId, **kwargs) -> None:
        widget = self._screens.get(screen_id)
        if widget is None:
            return
        if hasattr(widget, "activate"):
            try:
                widget.activate(**kwargs)  # type: ignore[call-arg]
            except TypeError:
                widget.activate()  # type: ignore[call-arg]
        index = self._stack.indexOf(widget)
        self._stack.setCurrentIndex(index)
        self._header.update_progress()
        self._focus_top()

    def _focus_top(self) -> None:
        current = self._stack.currentWidget()
        if current is None:
            return
        target = current.findChild(QLabel, None) or current
        if hasattr(target, "setFocus"):
            try:
                target.setFocus(Qt.TabFocusReason)
            except Exception:
                pass

    @property
    def context(self) -> AppContext:
        return self._context

    def apply_theme(self) -> None:
        apply_theme(self.context.settings._backend)  # not needed; call via app
        app = self.window().windowHandle()
        # better: refresh via QApplication
        from PySide6.QtWidgets import QApplication

        apply_theme(QApplication.instance(), self.context.settings)
        self._header.update_progress()

    def go_back(self) -> None:
        self.navigate_to(ScreenId.HOME)
