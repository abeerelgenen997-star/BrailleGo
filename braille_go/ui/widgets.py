"""عناصر واجهة مشتركة قابلة لإعادة الاستخدام.

Every helper here is a thin factory that guarantees the two accessibility
must-haves the brief asks for: a clear **accessible name** on every
control and a **visible, keyboard-reachable** focus state.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .theme import braille_font


def screen_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("screenTitle")
    label.setWordWrap(True)
    label.setAccessibleName(text)
    label.setFocusPolicy(Qt.StrongFocus)  # ليقرأه قارئ الشاشة عند الوصول إليه
    return label


def heading(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("cardHeading")
    label.setWordWrap(True)
    label.setAccessibleName(text)
    return label


def body_label(text: str, *, muted: bool = False, wrap: bool = True) -> QLabel:
    label = QLabel(text)
    if muted:
        label.setObjectName("muted")
    label.setWordWrap(wrap)
    label.setAccessibleName(text)
    return label


class Card(QFrame):
    """بطاقة ذات عنوان ومحتوى عمودي."""

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.StyledPanel)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(14, 12, 14, 12)
        self._layout.setSpacing(8)
        if title:
            self._layout.addWidget(heading(title))

    def add(self, widget: QWidget) -> QWidget:
        self._layout.addWidget(widget)
        return widget

    def add_layout(self, layout) -> None:
        self._layout.addLayout(layout)

    def add_stretch(self, stretch: int = 1) -> None:
        self._layout.addStretch(stretch)

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._layout


def button(
    text: str,
    *,
    on_click: Callable[[], None] | None = None,
    name: str | None = None,
    tooltip: str = "",
    primary: bool = False,
    danger: bool = False,
    enabled: bool = True,
) -> QPushButton:
    """أنشئ زرًا باسم واضح لقارئ الشاشة وحالة تركيز ظاهرة."""
    widget = QPushButton(text)
    widget.setAccessibleName(name or text)
    if tooltip:
        widget.setToolTip(tooltip)
        widget.setAccessibleDescription(tooltip)
    if primary:
        widget.setProperty("primary", True)
    if danger:
        widget.setProperty("danger", True)
    widget.setEnabled(enabled)
    if on_click is not None:
        widget.clicked.connect(lambda _=False: on_click())
    return widget


class StatusBanner(QLabel):
    """شريط حالة يُعلَن لقارئ الشاشة عند تغيّره."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("statusBanner")
        self.setWordWrap(True)
        self.setAccessibleName("شريط الحالة")
        self.setVisible(False)

    def show_message(self, text: str, *, tone: str = "info") -> None:
        self.setText(text)
        self.setVisible(bool(text))
        self.setAccessibleDescription(text)
        if tone == "ok":
            self.setObjectName("feedbackOk")
        elif tone == "error":
            self.setObjectName("feedbackError")
        else:
            self.setObjectName("statusBanner")
        # أعِد تطبيق ورقة التنسيق لأن اسم العنصر تغيّر.
        self.style().unpolish(self)
        self.style().polish(self)


class LabeledProgress(QWidget):
    """شريط تقدّم مرفق بنص النسبة المئوية (لا لون فقط)."""

    def __init__(self, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self._caption = QLabel(label)
        self._caption.setAccessibleName(label)
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setTextVisible(True)
        self._bar.setFormat("%p%")
        layout.addWidget(self._caption)
        layout.addWidget(self._bar)

    def set_value(self, percent: float, caption: str | None = None) -> None:
        value = int(max(0.0, min(100.0, round(percent))))
        self._bar.setValue(value)
        text = caption if caption is not None else self._caption.text()
        self._caption.setText(text)
        self._bar.setAccessibleName(f"{text}: {value}%")
        self._bar.setAccessibleDescription(f"{text} بنسبة {value} بالمئة")


class BrailleUnicodeLabel(QLabel):
    """عرض ثانوي لنمط برايل كمحارف يونيكود (بجانب الرسم المخصّص)."""

    def __init__(self, parent: QWidget | None = None, *, point_size: float = 22.0) -> None:
        super().__init__(parent)
        self._point_size = point_size
        self.setFont(braille_font(point_size))
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def set_pattern(self, unicode_text: str, *, plain_fallback: str = "") -> None:
        text = unicode_text or ""
        self.setText(text or plain_fallback)
        self.setAccessibleName(
            f"نمط برايل {text}" if text else "لا يوجد نمط برايل"
        )


def scroll_area(content: QWidget) -> QScrollArea:
    """غلّف محتوى شاشة داخل مساحة قابلة للتمرير."""
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setWidget(content)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    area.setFrameShape(QFrame.NoFrame)
    return area


class ButtonColumn(QWidget):
    """عمود أزرار مرتّبة (للشاشة الرئيسية)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

    def add(self, widget: QWidget) -> QWidget:
        self._layout.addWidget(widget)
        return widget

    def add_stretch(self) -> None:
        self._layout.addStretch(1)


class StatsGrid(QWidget):
    """شبكة (عنوان: قيمة) للاستخدام في شاشة التقدّم."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(16)
        self._grid.setVerticalSpacing(6)
        self._row = 0

    def clear(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._row = 0

    def add_row(self, label: str, value: str) -> None:
        key = QLabel(label)
        key.setObjectName("muted")
        key.setAccessibleName(f"{label}: {value}")
        val = QLabel(value)
        val.setAccessibleName(f"{label}: {value}")
        val.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._grid.addWidget(key, self._row, 0)
        self._grid.addWidget(val, self._row, 1)
        self._row += 1


def informational(parent: QWidget | None, title: str, text: str) -> None:
    """رسالة معلومات قابلة للقراءة بقارئ الشاشة."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec()


def confirm(parent: QWidget | None, title: str, text: str) -> bool:
    """نافذة تأكيد نعم/لا."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    box.setDefaultButton(QMessageBox.No)
    return box.exec() == QMessageBox.Yes


def set_items_enabled(widgets: Iterable[QWidget], enabled: bool) -> None:
    for widget in widgets:
        widget.setEnabled(enabled)
