"""عناصر واجهة مشتركة لنسخة wxPython.

كل عنصر هنا يضمن أمرين أساسيين لإمكانية الوصول:

* **اسم واضح** لكل عنصر تفاعلي (``SetName``) يقرأه NVDA.
* **حالة تركيز ظاهرة** قابلة للوصول بلوحة المفاتيح.
"""

from __future__ import annotations

from collections.abc import Callable

import wx


def heading(parent: wx.Window, text: str, theme=None) -> wx.StaticText:
    label = wx.StaticText(parent, label=text)
    label.SetName(text)
    if theme is not None:
        font = theme.make_font(15.0)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        label.SetFont(font)
    return label


def subheading(parent: wx.Window, text: str, theme=None) -> wx.StaticText:
    label = wx.StaticText(parent, label=text)
    label.SetName(text)
    if theme is not None:
        font = theme.make_font(12.5)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        label.SetFont(font)
    return label


def body(parent: wx.Window, text: str) -> wx.StaticText:
    label = wx.StaticText(parent, label=text)
    label.SetName(text)
    return label


def wrapped_text(parent: wx.Window, text: str, width: int = 720) -> wx.StaticText:
    """نص متعدّد الأسطر مع التفاف تلقائي."""
    label = wx.StaticText(parent, label=text)
    label.SetName(text)
    try:
        label.Wrap(width)
    except Exception:
        pass
    return label


def card(parent: wx.Window, container: wx.Sizer, title: str = "", theme=None) -> tuple[wx.Panel, wx.Sizer]:
    """أنشئ بطاقة (لوحة بإطار) وأضِفها إلى الحاوية، وأعد (اللوحة، المحتوى)."""
    if title:
        box = wx.StaticBox(parent, label=title)
        panel = wx.Panel(box)
        outer = wx.StaticBoxSizer(box, wx.VERTICAL)
    else:
        panel = wx.Panel(parent)
        outer = wx.BoxSizer(wx.VERTICAL)
    outer.Add(panel, 1, wx.EXPAND | wx.ALL, 6)
    inner = wx.BoxSizer(wx.VERTICAL)
    panel.SetSizer(inner)
    container.Add(outer, 0, wx.EXPAND | wx.ALL, 6)
    return panel, inner


def action_button(
    parent: wx.Window,
    label: str,
    *,
    on_click: Callable[[], None] | None = None,
    name: str | None = None,
    tooltip: str = "",
    primary: bool = False,
    enabled: bool = True,
) -> wx.Button:
    """أنشئ زرًا باسم واضح لقارئ الشاشة."""
    button = wx.Button(parent, label=label)
    button.SetName(name or label)
    if tooltip:
        button.SetToolTip(tooltip)
        button.SetHelpText(tooltip)
    if primary:
        try:
            button.SetFont(button.GetFont().Bold())
        except Exception:
            pass
    button.Enable(enabled)
    if on_click is not None:
        button.Bind(wx.EVT_BUTTON, lambda event: on_click())
    return button


def read_only_box(
    parent: wx.Window,
    *,
    multiline: bool = True,
    height: int = 90,
    name: str = "",
) -> wx.TextCtrl:
    """صندوق كتابة للقراءة فقط — يُقرأ بالكامل بقارئات الشاشة (Edit Box)."""
    style = wx.TE_READONLY | wx.TE_PROCESS_ENTER | wx.BORDER_SUNKEN
    if multiline:
        control = wx.TextCtrl(parent, style=style | wx.TE_MULTILINE | wx.TE_WORDWRAP, size=(-1, height))
    else:
        control = wx.TextCtrl(parent, style=style, size=(-1, height))
    if name:
        control.SetName(name)
    control.SetCanFocus(True)
    return control


def editable_box(
    parent: wx.Window,
    *,
    name: str = "",
    on_enter: Callable[[], None] | None = None,
) -> wx.TextCtrl:
    """صندوق كتابة قابل للتعديل (حقل إدخال الإجابة)."""
    control = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
    if name:
        control.SetName(name)
    if on_enter is not None:
        control.Bind(wx.EVT_TEXT_ENTER, lambda event: on_enter())
    return control


def informational(parent: wx.Window, title: str, text: str) -> None:
    """رسالة معلومات قابلة للقراءة بقارئ الشاشة."""
    wx.MessageBox(text, title, wx.OK | wx.ICON_INFORMATION, parent)


def confirm(parent: wx.Window, title: str, text: str) -> bool:
    """نافذة تأكيد نعم/لا."""
    return wx.MessageBox(text, title, wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT, parent) == wx.YES


def set_items_enabled(widgets, enabled: bool) -> None:
    for widget in widgets:
        try:
            widget.Enable(enabled)
        except Exception:
            pass
