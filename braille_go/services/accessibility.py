"""أدوات إمكانية الوصول: التسميات والإعلانات لقارئات الشاشة.

These helpers wrap Qt's accessibility API so that the whole application speaks
the same "language" to NVDA and Windows Narrator:

* :func:`set_accessible` gives every interactive widget a clear Arabic name and
  a longer description, which screen readers read out on focus.
* :func:`announce` pushes a *live* announcement (correct/incorrect answer,
  screen changes, braille cell state) without moving the keyboard focus, which
  is what blind users expect while they are working inside the braille cell.

Qt exposes ``QAccessibleAnnouncementEvent`` on Qt 6.8+, which NVDA and Narrator
honour.  On older runtimes we fall back to an ``Alert`` accessibility event,
which is less polite but still announced.
"""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtGui import QAccessible, QAccessibleEvent, QAccessibleAnnouncementEvent
from PySide6.QtWidgets import QWidget

from ..core.braille import BrailleCell

#: مستويات الأولوية في الإعلان (تطابق Qt).
POLITE = "polite"
ASSERTIVE = "assertive"


def set_accessible(
    widget: QWidget,
    name: str = "",
    description: str = "",
    help_text: str = "",
) -> QWidget:
    """اضبط اسم ووصف العنصر لقارئ الشاشة ثم أعِده."""
    if name:
        widget.setAccessibleName(name)
    if description:
        widget.setAccessibleDescription(description)
    if help_text:
        widget.setToolTip(help_text)
        widget.setStatusTip(help_text)
    return widget


def set_accessible_name(widget: QWidget, name: str) -> QWidget:
    widget.setAccessibleName(name)
    return widget


def describe_braille_cell(cell: BrailleCell) -> str:
    """وصف نصي كامل لحالة خلية برايل (للنطق والقراءة)."""
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


def announce(target: QWidget | None, message: str, politeness: str = POLITE) -> None:
    """أعلن رسالة لقارئ الشاشة دون تغيير موضع التركيز.

    ``target`` يُستخدم لتحديد النافذة التي يخصّها الإعلان.
    """
    if not message:
        return
    try:
        event = QAccessibleAnnouncementEvent(target, message)
        # الخاصية موجودة في Qt 6.8+؛ اسم التعداد هو ``AnnouncementPoliteness``.
        if hasattr(event, "setPoliteness"):
            enum = getattr(QAccessible, "AnnouncementPoliteness", None)
            if enum is not None:
                try:
                    event.setPoliteness(
                        enum.Assertive if politeness == ASSERTIVE else enum.Polite
                    )
                except Exception:  # pragma: no cover - enum naming differences
                    pass
        QAccessible.updateAccessibility(event)
    except Exception:
        # بديل: حدث تنبيه عادي على العنصر نفسه.
        try:
            if target is not None:
                alert = QAccessibleEvent(target, QAccessible.Event.Alert)
                QAccessible.updateAccessibility(alert)
        except Exception:  # pragma: no cover - accessibility must never crash
            pass


def announce_alert(target: QWidget | None, message: str) -> None:
    """إعلان عاجل (نتيجة إجابة مثلًا)."""
    announce(target, message, politeness=ASSERTIVE)


def bind_live_region(label: QWidget, description: str = "") -> None:
    """علّم عنصرًا نصيًا كمنطقة حيّة يقرأها قارئ الشاشة عند تغيّرها."""
    try:
        label.setAccessibleName(label.text() if hasattr(label, "text") else "")
    except Exception:  # pragma: no cover
        pass
    if description:
        label.setAccessibleDescription(description)


def ensure_focus_visible(widget: QWidget) -> None:
    """تأكد من أن العنصر يقبل التركيز بلوحة المفاتيح."""
    widget.setFocusPolicy(widget.focusPolicy())
