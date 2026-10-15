"""أدوات إمكانية الوصول لنسخة wxPython.

عناصر wx هي عناصر Win32 أصلية يقرأها NVDA وWindows Narrator مباشرة. الإعلان
عن رسالة *دون* تغيير التركيز غير متاح مباشرةً في wx، لذا نعتمد على
أسلوبين موثوقين:

* نقل التركيز إلى عنصر قراءة فقط يحمل الرسالة، فيقرأها قارئ الشاشة.
* كتابة الرسالة في شريط الحالة (Status Bar) للنافذة.
"""

from __future__ import annotations

import wx

from braille_go.core.braille import BrailleCell

from . import i18n


def set_accessible(window: wx.Window, name: str = "", description: str = "") -> wx.Window:
    """اضبط الاسم/الوصف لقارئ الشاشة إن كان متاحًا، ثم أعِد العنصر."""
    try:
        if name:
            window.SetName(name)
            if hasattr(window, "SetHelpText"):
                window.SetHelpText(description or name)
        if description and hasattr(window, "SetToolTip"):
            window.SetToolTip(description)
    except Exception:
        pass
    return window


def describe_braille_cell(cell: BrailleCell) -> str:
    """وصف نصي كامل لحالة خلية برايل (للقراءة والنطق)، بلغة الواجهة."""
    if cell.is_empty:
        return i18n.t("a11y_cell_empty")
    if i18n.get_lang() == "ar":
        dots = cell.describe_ar()
    else:
        dots = i18n.t("ex_separator").join(
            i18n.t("dot_name", n=d) for d in cell.dots
        )
    return i18n.t(
        "a11y_cell_dots",
        dots=dots,
        count=cell.count,
        pattern=cell.to_dot_string(),
    )


def describe_cells(cells: tuple[BrailleCell, ...]) -> str:
    """وصف نصي لسلسلة خلايا (كلمة أو جملة)، بلغة الواجهة."""
    if not cells:
        return i18n.t("a11y_no_cells")
    parts = []
    for position, cell in enumerate(cells, start=1):
        if cell.is_empty:
            parts.append(i18n.t("a11y_cell_blank", n=position))
        else:
            parts.append(
                i18n.t("a11y_cell_position", n=position, dots=cell.to_dot_string())
            )
    return i18n.t("ex_separator").join(parts)


def set_status(window: wx.Window, message: str) -> None:
    """اكتب رسالة في شريط الحالة الخاص بالنافذة الأعلى."""
    try:
        top = window.GetTopLevelParent()
        frame = top if isinstance(top, wx.Frame) else None
        if frame is not None and frame.GetStatusBar() is not None:
            frame.SetStatusText(message)
    except Exception:
        pass


def announce(window: wx.Window | None, message: str) -> None:
    """أعلن رسالة: اكتبها في شريط الحالة وحدّث وصف العنصر."""
    if not message:
        return
    if window is not None:
        set_status(window, message)
        try:
            window.SetHelpText(message)
        except Exception:
            pass


def focus_and_announce(control: wx.Window) -> None:
    """انقل التركيز إلى العنصر ليقرأه قارئ الشاشة."""
    try:
        control.SetFocus()
    except Exception:
        pass


def ensure_focusable(window: wx.Window) -> None:
    """اجعل العنصر قابلًا للتركيز لوحة المفاتيح إن أمكن."""
    try:
        window.SetCanFocus(True)
    except Exception:
        pass
