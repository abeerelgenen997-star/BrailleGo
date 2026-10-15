"""خلية برايل التفاعلية لنسخة wxPython (رسم مخصّص + دعم كامل للوحة المفاتيح).

الخلية هي قلب التطبيق، لذا نرسمها يدويًا بدل شبكة أزرار عادية، ما يمنحنا:

* حالة واضحة لكل نقطة (دائرة مصمتة + علامة صح + رقم النقطة) فلا يكون اللون
  هو الإشارة الوحيدة.
* مؤشّر لوحة مفاتيح يتحرّك بالأسهم ويبدّل النقطة بمفاتيح الأرقام أو المسافة.
* وصف نصي دقيق يُنشر لقارئ الشاشة عبر ``SetName`` و``SetHelpText``.

برايل يُقرأ من اليسار إلى اليمين دائمًا، لذا تُرسم الخلية هكذا بغضّ النظر عن
اتجاه الواجهة العربية.
"""

from __future__ import annotations

from typing import Callable, Sequence

import wx

from braille_go.core.braille import (
    BrailleCell,
    DOT_NAMES_AR,
    STANDARD_DOT_COUNT,
)

#: ترتيب النقاط: (صف، عمود، رقم النقطة). الأعمدة: 0 = يسار، 1 = يمين.
_DOT_LAYOUT: tuple[tuple[int, int, int], ...] = (
    (0, 0, 1), (1, 0, 2), (2, 0, 3),
    (0, 1, 4), (1, 1, 5), (2, 1, 6),
)

_NUMBER_KEYS = {
    ord("1"): 1, ord("2"): 2, ord("3"): 3, ord("4"): 4, ord("5"): 5, ord("6"): 6,
    wx.WXK_NUMPAD1: 1, wx.WXK_NUMPAD2: 2, wx.WXK_NUMPAD3: 3,
    wx.WXK_NUMPAD4: 4, wx.WXK_NUMPAD5: 5, wx.WXK_NUMPAD6: 6,
}


class _DotCanvas(wx.Panel):
    """أساس مشترك: يرسم خلية من ستّ نقاط."""

    def __init__(
        self,
        parent: wx.Window,
        *,
        interactive: bool = False,
        scale: float = 1.0,
        theme=None,
    ) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self._dots: set[int] = set()
        self._interactive = interactive
        self._scale = max(0.5, float(scale))
        self._show_numbers = True
        self._cursor = 1
        self._theme = theme
        self.on_change: Callable[[frozenset[int]], None] | None = None
        self.on_confirm: Callable[[], None] | None = None

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetCanFocus(interactive)
        if interactive:
            self.SetName("خلية برايل التفاعلية")
        else:
            self.SetName("نمط برايل")

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        if interactive:
            self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
            self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
            self.Bind(wx.EVT_SET_FOCUS, lambda event: self.Refresh())
            self.Bind(wx.EVT_KILL_FOCUS, lambda event: self.Refresh())
        self._refresh_accessible()

    # ------------------------------------------------------------------
    # إعدادات
    # ------------------------------------------------------------------
    def set_theme(self, theme) -> None:
        self._theme = theme
        self.Refresh()

    def set_scale(self, scale: float) -> None:
        self._scale = max(0.5, float(scale))
        self.InvalidateBestSize()
        self.Refresh()

    def set_show_numbers(self, show: bool) -> None:
        self._show_numbers = bool(show)
        self.Refresh()

    def _colors(self) -> dict[str, str]:
        if self._theme is not None:
            return self._theme.colors
        return {
            "background": "#f4f6f8", "surface": "#ffffff", "text": "#111418",
            "dot_on": "#111418", "dot_off": "#d8dee5", "dot_border": "#5a636d",
            "focus": "#ff8c00", "accent": "#0b5fa5",
        }

    # ------------------------------------------------------------------
    # النقاط
    # ------------------------------------------------------------------
    def dots(self) -> tuple[int, ...]:
        return tuple(sorted(self._dots))

    def cell(self) -> BrailleCell:
        return BrailleCell.from_dots(self._dots)

    def has_dot(self, dot: int) -> bool:
        return dot in self._dots

    def set_cell(self, cells: Sequence[int] | BrailleCell | None, notify: bool = True) -> None:
        if isinstance(cells, BrailleCell):
            values = set(cells.dots)
        elif cells is None:
            values = set()
        else:
            values = {int(d) for d in cells if 1 <= int(d) <= STANDARD_DOT_COUNT}
        if values == self._dots:
            return
        self._dots = values
        self._refresh_accessible()
        self.Refresh()
        if notify and self.on_change is not None:
            self.on_change(frozenset(self._dots))

    def clear(self, notify: bool = True) -> None:
        self.set_cell((), notify=notify)

    def toggle_dot(self, dot: int, *, announce_change: bool = True) -> None:
        if not 1 <= dot <= STANDARD_DOT_COUNT:
            return
        if dot in self._dots:
            self._dots.discard(dot)
        else:
            self._dots.add(dot)
        self._cursor = dot
        self._refresh_accessible()
        self.Refresh()
        if self.on_change is not None:
            self.on_change(frozenset(self._dots))
        if announce_change:
            state = "محدَّدة" if dot in self._dots else "غير محدَّدة"
            self.SetHelpText(f"{DOT_NAMES_AR[dot]} {state}. {self._summary_ar()}")

    # ------------------------------------------------------------------
    # إمكانية الوصول
    # ------------------------------------------------------------------
    def _summary_ar(self) -> str:
        if not self._dots:
            return "الخلية فارغة"
        return "النقاط المحددة: " + "، ".join(str(d) for d in sorted(self._dots))

    def state_text_ar(self) -> str:
        from .a11y import describe_braille_cell

        return describe_braille_cell(self.cell())

    def _refresh_accessible(self) -> None:
        description = self.state_text_ar()
        if self._interactive:
            description += (
                " استخدم مفاتيح الأرقام من 1 إلى 6 لتبديل النقاط، "
                "ومفاتيح الأسهم للتنقل بين النقاط، ومفتاح المسافة للتبديل، "
                "ومفتاح الإدخال للتأكيد."
            )
        self.SetHelpText(description)

    # ------------------------------------------------------------------
    # الرسم
    # ------------------------------------------------------------------
    def DoGetBestSize(self) -> wx.Size:  # noqa: N802 - wx naming
        return wx.Size(int(110 * self._scale), int(150 * self._scale))

    def _dot_geometry(self) -> dict[int, tuple[float, float, float]]:
        width = max(1, self.GetClientSize().width)
        height = max(1, self.GetClientSize().height)
        padding = 8.0 * self._scale
        available_w = max(1.0, width - 2 * padding)
        available_h = max(1.0, height - 2 * padding)
        col_step = available_w / 2.0
        row_step = available_h / 3.0
        radius = max(4.0, min(col_step, row_step) * 0.32)
        geometry: dict[int, tuple[float, float, float]] = {}
        for row, col, dot in _DOT_LAYOUT:
            cx = padding + col_step * (col + 0.5)
            cy = padding + row_step * (row + 0.5)
            geometry[dot] = (cx, cy, radius)
        return geometry

    def _on_paint(self, event: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        colours = self._colors()
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return

        bg = wx.Colour(self.GetBackgroundColour())
        gc.SetBrush(wx.Brush(bg))
        gc.DrawRectangle(0, 0, self.GetClientSize().width, self.GetClientSize().height)

        geometry = self._dot_geometry()
        font = wx.Font(
            int(max(7, 10 * self._scale)),
            wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,
        )
        gc.SetFont(font, wx.Colour(_hex(colours["text"])))
        has_focus = self.HasFocus()

        for dot, (cx, cy, radius) in geometry.items():
            selected = dot in self._dots
            if selected:
                gc.SetBrush(wx.Brush(wx.Colour(_hex(colours["dot_on"]))))
                pen = gc.CreatePen(wx.Pen(wx.Colour(_hex(colours["dot_border"])), int(max(2, 2 * self._scale))))
            else:
                gc.SetBrush(wx.Brush(wx.Colour(_hex(colours["dot_off"]))))
                pen = gc.CreatePen(wx.Pen(wx.Colour(_hex(colours["dot_border"])), int(max(1, 1.5 * self._scale))))
            gc.SetPen(pen)
            gc.DrawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

            if selected:
                # علامة صح واضحة للأشخاص ذوي البصر المحدود.
                gc.SetPen(gc.CreatePen(wx.Pen(wx.Colour(_hex(colours["dot_off"])), int(max(2, 2.4 * self._scale)))))
                gc.StrokeLineSegments([
                    (cx - radius * 0.45, cy),
                    (cx - radius * 0.05, cy + radius * 0.40),
                    (cx - radius * 0.05, cy + radius * 0.40),
                    (cx + radius * 0.50, cy - radius * 0.40),
                ])

            if self._show_numbers:
                label = str(dot)
                text_w, text_h = gc.GetTextExtent(label)
                gc.DrawText(label, cx - text_w / 2, cy - text_h / 2)

        if self._interactive and has_focus:
            cx, cy, radius = geometry[self._cursor]
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(gc.CreatePen(wx.Pen(wx.Colour(_hex(colours["focus"])), int(max(3, 3 * self._scale)))))
            r = radius + 5 * self._scale
            gc.DrawEllipse(cx - r, cy - r, r * 2, r * 2)

    # ------------------------------------------------------------------
    # الفأرة
    # ------------------------------------------------------------------
    def _on_left_down(self, event: wx.MouseEvent) -> None:
        if not self._interactive:
            event.Skip()
            return
        position = event.GetPosition()
        geometry = self._dot_geometry()
        best: int | None = None
        best_distance = float("inf")
        for dot, (cx, cy, radius) in geometry.items():
            distance = ((position.x - cx) ** 2 + (position.y - cy) ** 2) ** 0.5
            if distance <= radius * 1.9 and distance < best_distance:
                best = dot
                best_distance = distance
        if best is not None:
            self.SetFocus()
            self.toggle_dot(best)

    # ------------------------------------------------------------------
    # لوحة المفاتيح
    # ------------------------------------------------------------------
    def _on_key_down(self, event: wx.KeyEvent) -> None:
        if not self._interactive:
            event.Skip()
            return
        code = event.GetKeyCode()
        if code in _NUMBER_KEYS:
            self.toggle_dot(_NUMBER_KEYS[code])
            return
        if code == wx.WXK_SPACE:
            self.toggle_dot(self._cursor)
            return
        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            if self.on_confirm is not None:
                self.on_confirm()
            return
        if code in (wx.WXK_BACK, wx.WXK_DELETE):
            self.clear()
            self.SetHelpText("تم مسح النقاط. الخلية فارغة.")
            return
        if code == wx.WXK_UP:
            self._move_cursor(0, -1)
            return
        if code == wx.WXK_DOWN:
            self._move_cursor(0, 1)
            return
        if code in (wx.WXK_LEFT, wx.WXK_HOME):
            self._move_cursor(-1, 0)
            return
        if code in (wx.WXK_RIGHT, wx.WXK_END):
            self._move_cursor(1, 0)
            return
        event.Skip()

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
        self.Refresh()
        state = "محدَّدة" if self._cursor in self._dots else "غير محدَّدة"
        self.SetHelpText(f"{DOT_NAMES_AR[self._cursor]} {state}.")


class BrailleCellInput(_DotCanvas):
    """خلية برايل تفاعلية مع إمكانية التأكيد."""

    def __init__(self, parent: wx.Window, *, scale: float = 1.4, theme=None) -> None:
        super().__init__(parent, interactive=True, scale=scale, theme=theme)
        self.SetToolTip("حدّد النقاط بمفاتيح الأرقام 1-6 أو بالفأرة، ثم اضغط تأكيد الإجابة (Ctrl+Enter).")


class BrailleCellsView(_DotCanvas):
    """عرض للقراءة فقط لسلسلة خلايا برايل (نمط المحفّز في الأسئلة)."""

    def __init__(self, parent: wx.Window, *, scale: float = 1.2, theme=None) -> None:
        super().__init__(parent, interactive=False, scale=scale, theme=theme)
        self._cells: tuple[BrailleCell, ...] = ()
        self._show_numbers = False

    def set_cells(self, cells: Sequence[BrailleCell] | str) -> None:
        if isinstance(cells, str):
            from braille_go.core.braille import unicode_to_cells

            self._cells = tuple(unicode_to_cells(cells))
        else:
            self._cells = tuple(cells)
        from .a11y import describe_cells

        description = describe_cells(self._cells)
        self.SetName("نمط برايل: " + description)
        self.SetHelpText(description)
        self.InvalidateBestSize()
        self.Refresh()

    def DoGetBestSize(self) -> wx.Size:  # noqa: N802
        count = max(1, len(self._cells))
        return wx.Size(int(64 * self._scale) * count, int(140 * self._scale))

    def _on_paint(self, event: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        colours = self._colors()
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return

        size = self.GetClientSize()
        bg = wx.Colour(self.GetBackgroundColour())
        gc.SetBrush(wx.Brush(bg))
        gc.DrawRectangle(0, 0, size.width, size.height)

        if not self._cells:
            gc.SetFont(wx.Font(int(max(10, 12 * self._scale)), wx.FONTFAMILY_SWISS,
                               wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL),
                       wx.Colour(_hex(colours["text"])))
            gc.DrawText("—", size.width / 2 - 6, size.height / 2 - 8)
            return

        cell_width = size.width / len(self._cells)
        height = max(1, size.height)
        padding = 5.0 * self._scale
        col_step = (cell_width - 2 * padding) / 2.0
        row_step = (height - 2 * padding) / 3.0
        radius = max(3.0, min(col_step, row_step) * 0.32)
        font = wx.Font(int(max(6, 9 * self._scale)), wx.FONTFAMILY_SWISS,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        gc.SetFont(font, wx.Colour(_hex(colours["text"])))

        for index, cell in enumerate(self._cells):
            left = index * cell_width
            for row, col, dot in _DOT_LAYOUT:
                cx = left + padding + col_step * (col + 0.5)
                cy = padding + row_step * (row + 0.5)
                if cell.has(dot):
                    gc.SetBrush(wx.Brush(wx.Colour(_hex(colours["dot_on"]))))
                    gc.SetPen(gc.CreatePen(wx.Pen(wx.Colour(_hex(colours["dot_border"])), int(max(1, 1.4 * self._scale)))))
                else:
                    gc.SetBrush(wx.Brush(wx.Colour(_hex(colours["dot_off"]))))
                    gc.SetPen(gc.CreatePen(wx.Pen(wx.Colour(_hex(colours["dot_border"])), 1)))
                gc.DrawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)
                if self._show_numbers:
                    label = str(dot)
                    text_w, text_h = gc.GetTextExtent(label)
                    gc.DrawText(label, cx - text_w / 2, cy - text_h / 2)


def _hex(value: str) -> str:
    """طبّع قيمة لون إلى ``#rrggbb``."""
    text = (value or "").strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        return "#000000"
    return "#" + text
