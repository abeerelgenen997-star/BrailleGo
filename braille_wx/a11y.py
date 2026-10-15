"""أدوات إمكانية الوصول لنسخة wxPython.

عناصر wx هي عناصر Win32 أصلية يقرأها NVDA وWindows Narrator مباشرة. الإعلان
عن رسالة *دون* تغيير التركيز غير متاح في wx بنفس سهولة Qt، لذا نعتمد على
أسلوبين موثوقين:

* نقل التركيز إلى عنصر قراءة فقط يحمل الرسالة، فيقرأها قارئ الشاشة.
* كتابة الرسالة في شريط الحالة (Status Bar) للنافذة.
"""

from __future__ import annotations

import wx

from braille_go.core.braille import BrailleCell


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
    """وصف نصي كامل لحالة خلية برايل (للقراءة والنطق)."""
    if cell.is_empty:
        return (
            "خلية برايل فارغة. لا توجد نقاط محددة. "
            "النقاط المتاحة هي 1 و2 و3 في العمود الأيسر، و4 و5 و6 في العمود الأيمن."
        )
    return (
        f"خلية برايل: {cell.describe_ar()}. "
        f"عدد النقاط المحددة {cell.count} من 6. "
        f"النمط هو {cell.to_dot_string()}."
    )


def describe_cells(cells: tuple[BrailleCell, ...]) -> str:
    """وصف نصي لسلسلة خلايا (كلمة أو جملة)."""
    if not cells:
        return "لا توجد خلايا."
    parts = []
    for position, cell in enumerate(cells, start=1):
        if cell.is_empty:
            parts.append(f"الخلية {position}: فراغ")
        else:
            parts.append(f"الخلية {position}: النقاط {cell.to_dot_string()}")
    return "؛ ".join(parts)


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
