"""خلية برايل التفاعلية (رسم مخصّص + دعم كامل للوحة المفاتيح).

The interactive cell is the heart of the application, so it is implemented with
custom painting rather than a grid of ordinary buttons.  That gives us full
control over:

* an unambiguous **selected / not selected** state for every dot (filled shape
  with a tick *and* a printed dot number, so colour is never the only cue);
* a keyboard cursor moved with the arrow keys and toggled with the number keys
  or the space bar;
* a precise textual description published to the accessibility layer, which is
  what NVDA and Windows Narrator read out.

Braille itself is read left-to-right regardless of the language, so the cell is
always laid out left-to-right (the Arabic interface only mirrors the *screen*,
not the dots).
"""

from __future__ import annotations

from typing import Sequence

from PySide6.QtCore import QPoint, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QSizePolicy, QWidget

from ..core.braille import (
    BrailleCell,
    DOT_NAMES_AR,
    STANDARD_DOT_COUNT,
)
from ..services.accessibility import announce, describe_braille_cell

#: ترتيب النقاط: (صف، عمود، رقم النقطة). الأعمدة: 0 = يسار، 1 = يمين.
_DOT_LAYOUT: tuple[tuple[int, int, int], ...] = (
    (0, 0, 1), (1, 0, 2), (2, 0, 3),
    (0, 1, 4), (1, 1, 5), (2, 1, 6),
)

#: الألوان الافتراضية إذا لم تُطبَّق أي سمة بعد.
_DEFAULT_COLORS = {
    "dot_on": "#111418",
    "dot_off": "#d8dee5",
    "dot_border": "#5a636d",
    "focus": "#ff8c00",
    "accent": "#0b5fa5",
    "text": "#111418",
}


def current_colors() -> dict[str, str]:
    """ألوان الثيم الحالي (تقرأ من التطبيق، مع قيم افتراضية آمنة)."""
    app = QApplication.instance()
    if app is not None:
        value = app.property("brailleGoColors")
        if isinstance(value, dict):
            merged = dict(_DEFAULT_COLORS)
            merged.update({k: v for k, v in value.items() if isinstance(v, str)})
            return merged
    return dict(_DEFAULT_COLORS)


class _DotCanvas(QWidget):
    """أساس مشترك: يرسم خلية من ست نقاط."""

    dots_changed = Signal(object)  # frozenset[int]

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        interactive: bool = False,
        scale: float = 1.0,
    ) -> None:
        super().__init__(parent)
        self._dots: set[int] = set()
        self._interactive = interactive
        self._scale = max(0.5, float(scale))
        self._show_numbers = True
        self._cursor = 1
        self.setLayoutDirection(Qt.LeftToRight)  # برايل يُقرأ من اليسار لليمين
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.StrongFocus if interactive else Qt.NoFocus)
        self.setAccessibleName("خلية برايل")
        self._refresh_accessible_description()

    # ------------------------------------------------------------------
    # الدقّة والحجم
    # ------------------------------------------------------------------
    def set_scale(self, scale: float) -> None:
        self._scale = max(0.5, float(scale))
        self.updateGeometry()
        self.update()

    def set_show_numbers(self, show: bool) -> None:
        self._show_numbers = bool(show)
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt naming
        width = int(96 * self._scale)
        height = int(132 * self._scale)
        return QSize(width, height)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(int(60 * self._scale), int(84 * self._scale))

    # ------------------------------------------------------------------
    # النقاط
    # ------------------------------------------------------------------
    def dots(self) -> tuple[int, ...]:
        return tuple(sorted(self._dots))

    def cell(self) -> BrailleCell:
        return BrailleCell.from_dots(self._dots)

    def has_dot(self, dot: int) -> bool:
        return dot in self._dots

    def set_dots(self, dots: Sequence[int] | BrailleCell, *, notify: bool = True) -> None:
        if isinstance(dots, BrailleCell):
            values = set(dots.dots)
        else:
            values = {int(d) for d in dots if 1 <= int(d) <= STANDARD_DOT_COUNT}
        if values == self._dots:
            return
        self._dots = values
        self._refresh_accessible_description()
        self.update()
        if notify:
            self.dots_changed.emit(frozenset(self._dots))

    def clear(self, *, notify: bool = True) -> None:
        self.set_dots((), notify=notify)

    def toggle_dot(self, dot: int, *, announce_change: bool = True) -> None:
        if not 1 <= dot <= STANDARD_DOT_COUNT:
            return
        if dot in self._dots:
            self._dots.discard(dot)
        else:
            self._dots.add(dot)
        self._cursor = dot
        self._refresh_accessible_description()
        self.update()
        self.dots_changed.emit(frozenset(self._dots))
        if announce_change:
            state = "محدَّدة" if dot in self._dots else "غير محدَّدة"
            announce(self, f"{DOT_NAMES_AR[dot]} {state}. {self._summary_ar()}")

    # ------------------------------------------------------------------
    # إمكانية الوصول
    # ------------------------------------------------------------------
    def _summary_ar(self) -> str:
        if not self._dots:
            return "الخلية فارغة"
        return "النقاط المحددة: " + "، ".join(str(d) for d in sorted(self._dots))

    def _refresh_accessible_description(self) -> None:
        description = describe_braille_cell(self.cell())
        if self._interactive:
            description += (
                " استخدم مفاتيح الأرقام من 1 إلى 6 لتبديل النقاط، "
                "ومفاتيح الأسهم للتنقل بين النقاط، ومفتاح المسافة للتبديل، "
                "ومفتاح الإدخال للتأكيد."
            )
        self.setAccessibleDescription(description)

    def state_text_ar(self) -> str:
        """وصف نصي كامل للحالة (يُستخدم في التغذية الراجعة والنطق)."""
        return describe_braille_cell(self.cell())

    # ------------------------------------------------------------------
    # الرسم
    # ------------------------------------------------------------------
    def _dot_geometry(self) -> dict[int, tuple[QPoint, float]]:
        width = max(1, self.width())
        height = max(1, self.height())
        padding = 6.0 * self._scale
        available_w = max(1.0, width - 2 * padding)
        available_h = max(1.0, height - 2 * padding)
        col_step = available_w / 2.0
        row_step = available_h / 3.0
        radius = max(3.0, min(col_step, row_step) * 0.30)
        geometry: dict[int, tuple[QPoint, float]] = {}
        for row, col, dot in _DOT_LAYOUT:
            cx = padding + col_step * (col + 0.5)
            cy = padding + row_step * (row + 0.5)
            geometry[dot] = (QPoint(int(cx), int(cy)), radius)
        return geometry

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt naming
        colors = current_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        geometry = self._dot_geometry()
        on_pen = QPen(QColor(colors["dot_border"]))
        on_pen.setWidthF(max(1.5, 2.0 * self._scale))

        font = QFont(self.font())
        font.setPointSizeF(max(7.0, 9.0 * self._scale))
        font.setBold(True)
        painter.setFont(font)

        has_focus = self.hasFocus()

        for dot, (center, radius) in geometry.items():
            selected = dot in self._dots
            rect = QRectF(
                center.x() - radius,
                center.y() - radius,
                radius * 2,
                radius * 2,
            )
            if selected:
                painter.setBrush(QColor(colors["dot_on"]))
                painter.setPen(on_pen)
                painter.drawEllipse(rect)
                # علامة اختيار واضحة للأشخاص ذوي البصر المحدود.
                tick = QPen(QColor(colors["dot_off"]))
                tick.setWidthF(max(1.5, 2.2 * self._scale))
                painter.setPen(tick)
                painter.drawLine(
                    QPoint(int(rect.left() + rect.width() * 0.28),
                           int(rect.center().y())),
                    QPoint(int(rect.center().x() - rect.width() * 0.02),
                           int(rect.bottom() - rect.height() * 0.28)),
                )
                painter.drawLine(
                    QPoint(int(rect.center().x() - rect.width() * 0.02),
                           int(rect.bottom() - rect.height() * 0.28)),
                    QPoint(int(rect.right() - rect.width() * 0.26),
                           int(rect.top() + rect.height() * 0.30)),
                )
            else:
                painter.setBrush(QColor(colors["dot_off"]))
                border = QPen(QColor(colors["dot_border"]))
                border.setStyle(Qt.DashLine)
                border.setWidthF(max(1.0, 1.6 * self._scale))
                painter.setPen(border)
                painter.drawEllipse(rect)

            if self._show_numbers:
                painter.setPen(QColor(colors["text"]))
                label = str(dot)
                metrics = painter.fontMetrics()
                text_w = metrics.horizontalAdvance(label)
                text_h = metrics.height()
                painter.drawText(
                    QPoint(int(center.x() - text_w / 2),
                           int(center.y() + text_h / 4)),
                    label,
                )

        # حلقة التركيز حول النقطة الحالية عند وجود تركيز لوحة المفاتيح.
        if self._interactive and has_focus:
            center, radius = geometry[self._cursor]
            focus_pen = QPen(QColor(colors["focus"]))
            focus_pen.setWidthF(max(2.0, 3.0 * self._scale))
            painter.setPen(focus_pen)
            painter.setBrush(Qt.NoBrush)
            r = radius + 4.0 * self._scale
            painter.drawEllipse(QRectF(center.x() - r, center.y() - r, r * 2, r * 2))

        painter.end()

    # ------------------------------------------------------------------
    # أحداث الماوس
    # ------------------------------------------------------------------
    def _dot_at(self, pos: QPoint) -> int | None:
        geometry = self._dot_geometry()
        best: int | None = None
        best_distance = float("inf")
        for dot, (center, radius) in geometry.items():
            dx = pos.x() - center.x()
            dy = pos.y() - center.y()
            distance = (dx * dx + dy * dy) ** 0.5
            if distance <= radius * 1.8 and distance < best_distance:
                best = dot
                best_distance = distance
        return best

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if not self._interactive or event.button() != Qt.LeftButton:
            super().mousePressEvent(event)
            return
        dot = self._dot_at(event.position().toPoint())
        if dot is not None:
            self.setFocus(Qt.MouseFocusReason)
            self.toggle_dot(dot)
        event.accept()

    # ------------------------------------------------------------------
    # أحداث لوحة المفاتيح
    # ------------------------------------------------------------------
    def keyPressEvent(self, event) -> None:  # noqa: N802
        if not self._interactive:
            super().keyPressEvent(event)
            return

        key = event.key()
        text = event.text()

        if text and text in "123456":
            self.toggle_dot(int(text))
            event.accept()
            return
        if key == Qt.Key_Space:
            self.toggle_dot(self._cursor)
            event.accept()
            return
        if key in (Qt.Key_Return, Qt.Key_Enter):
            # تُعالَج في :class:`BrailleCellInput`؛ نتجاهلها هنا.
            super().keyPressEvent(event)
            return
        if key in (Qt.Key_Backspace, Qt.Key_Delete):
            self.clear()
            announce(self, "تم مسح النقاط. الخلية فارغة.")
            event.accept()
            return
        if key == Qt.Key_Up:
            self._move_cursor(0, -1)
            event.accept()
            return
        if key == Qt.Key_Down:
            self._move_cursor(0, 1)
            event.accept()
            return
        if key in (Qt.Key_Left, Qt.Key_Home):
            self._move_cursor(-1, 0)
            event.accept()
            return
        if key in (Qt.Key_Right, Qt.Key_End):
            self._move_cursor(1, 0)
            event.accept()
            return
        super().keyPressEvent(event)

    def _move_cursor(self, dcol: int, drow: int) -> None:
        current = next(pos for pos in _DOT_LAYOUT if pos[2] == self._cursor)
        row, col = current[0], current[1]
        if dcol:
            col = 1 if dcol > 0 else 0
        if drow:
            row = max(0, min(2, row + drow))
        for pos in _DOT_LAYOUT:
            if pos[0] == row and pos[1] == col:
                self._cursor = pos[2]
                break
        self.update()
        state = "محدَّدة" if self._cursor in self._dots else "غير محدَّدة"
        announce(self, f"{DOT_NAMES_AR[self._cursor]} {state}.")

    def focusInEvent(self, event) -> None:  # noqa: N802
        super().focusInEvent(event)
        if self._interactive:
            self.update()

    def focusOutEvent(self, event) -> None:  # noqa: N802
        super().focusOutEvent(event)
        self.update()


class BrailleCellInput(_DotCanvas):
    """خلية برايل تفاعلية مع إشارة تأكيد."""

    confirmed = Signal()

    def __init__(self, parent: QWidget | None = None, *, scale: float = 1.0) -> None:
        super().__init__(parent, interactive=True, scale=scale)
        self.setAccessibleName("خلية برايل التفاعلية")
        self.setToolTip(
            "حدّد النقاط بمفاتيح الأرقام 1-6 أو بالفأرة، ثم اضغط تأكيد الإجابة."
        )

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if self._interactive and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.confirmed.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class BrailleCellsView(QWidget):
    """عرض للقراءة فقط لسلسلة خلايا برايل (نمط المحفّز في الأسئلة)."""

    def __init__(self, parent: QWidget | None = None, *, scale: float = 1.0) -> None:
        super().__init__(parent)
        self._cells: tuple[BrailleCell, ...] = ()
        self._scale = max(0.5, float(scale))
        self._show_numbers = False
        self.setLayoutDirection(Qt.LeftToRight)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setAccessibleName("نمط برايل")

    def set_scale(self, scale: float) -> None:
        self._scale = max(0.5, float(scale))
        self.updateGeometry()
        self.update()

    def set_show_numbers(self, show: bool) -> None:
        self._show_numbers = bool(show)
        self.update()

    def set_cells(self, cells: Sequence[BrailleCell]) -> None:
        self._cells = tuple(cells)
        parts = []
        for index, cell in enumerate(self._cells, start=1):
            if cell.is_empty:
                parts.append(f"الخلية {index}: فراغ")
            else:
                parts.append(f"الخلية {index}: النقاط {cell.to_dot_string()}")
        self.setAccessibleDescription(
            "؛ ".join(parts) if parts else "لا توجد خلايا لعرضها."
        )
        self.setAccessibleName("نمط برايل: " + "؛ ".join(parts) if parts else "نمط برايل فارغ")
        self.updateGeometry()
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        count = max(1, len(self._cells))
        return QSize(int(52 * self._scale) * count, int(116 * self._scale))

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(int(40 * self._scale), int(80 * self._scale))

    def paintEvent(self, event) -> None:  # noqa: N802
        colors = current_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if not self._cells:
            painter.setPen(QColor(colors["text"]))
            painter.drawText(self.rect(), Qt.AlignCenter, "—")
            painter.end()
            return

        cell_width = self.width() / len(self._cells)
        height = max(1, self.height())
        padding = 4.0 * self._scale
        col_step = (cell_width - 2 * padding) / 2.0
        row_step = (height - 2 * padding) / 3.0
        radius = max(2.5, min(col_step, row_step) * 0.30)

        font = QFont(self.font())
        font.setPointSizeF(max(6.0, 8.0 * self._scale))
        painter.setFont(font)

        for index, cell in enumerate(self._cells):
            left = index * cell_width
            for row, col, dot in _DOT_LAYOUT:
                cx = left + padding + col_step * (col + 0.5)
                cy = padding + row_step * (row + 0.5)
                rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
                if cell.has(dot):
                    painter.setBrush(QColor(colors["dot_on"]))
                    pen = QPen(QColor(colors["dot_border"]))
                    pen.setWidthF(max(1.0, 1.4 * self._scale))
                    painter.setPen(pen)
                    painter.drawEllipse(rect)
                else:
                    painter.setBrush(QColor(colors["dot_off"]))
                    pen = QPen(QColor(colors["dot_border"]))
                    pen.setStyle(Qt.DotLine)
                    pen.setWidthF(max(0.8, 1.0 * self._scale))
                    painter.setPen(pen)
                    painter.drawEllipse(rect)
                if self._show_numbers:
                    painter.setPen(QColor(colors["text"]))
                    label = str(dot)
                    metrics = painter.fontMetrics()
                    painter.drawText(
                        QPoint(int(cx - metrics.horizontalAdvance(label) / 2),
                               int(cy + metrics.height() / 4)),
                        label,
                    )
        painter.end()
