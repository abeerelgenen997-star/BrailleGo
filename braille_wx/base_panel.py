"""أساس الشاشات في نسخة wxPython."""

from __future__ import annotations

import wx


def clear_sizer(sizer: wx.Sizer) -> None:
    """احذف كل عناصر الحاوية بأمان (مع إتلاف صناديق StaticBox)."""
    if sizer is None:
        return
    while sizer.GetItemCount():
        item = sizer.GetItem(0)
        if item is None:
            break
        window = item.GetWindow()
        child_sizer = item.GetSizer()
        sizer.Detach(0)
        if window is not None:
            window.Destroy()
        elif child_sizer is not None:
            box = None
            try:
                if isinstance(child_sizer, wx.StaticBoxSizer):
                    box = child_sizer.GetStaticBox()
            except Exception:
                box = None
            clear_sizer(child_sizer)
            child_sizer.Clear(True)
            if box is not None:
                try:
                    box.Destroy()
                except Exception:
                    pass


class BasePanel(wx.ScrolledWindow):
    """شاشة قابلة للتمرير مع حاوية عمودية."""

    def __init__(self, parent: wx.Window, context, frame) -> None:
        super().__init__(parent, style=wx.VSCROLL | wx.TAB_TRAVERSAL)
        self.SetScrollRate(12, 12)
        self._context = context
        self._frame = frame
        self.content = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.content)

    # ------------------------------------------------------------------
    @property
    def context(self):
        return self._context

    @property
    def frame(self):
        return self._frame

    @property
    def theme(self):
        return self._frame.theme

    def finish_layout(self) -> None:
        """أعِد حساب التخطيط بعد بناء المحتوى."""
        try:
            self.Layout()
            self.FitInside()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # واجهة موحّدة للشاشات
    # ------------------------------------------------------------------
    def activate(self, **kwargs) -> None:  # pragma: no cover - overridden
        pass

    def deactivate(self) -> None:
        pass

    def focus_edit_box(self) -> None:
        """موضع (Ctrl+E): تركيز صندوق الكتابة الرئيسي في الشاشة.

        تُعيد ``True`` إن نجحت في التركيز على عنصر.
        """
        return False

    def focus_default(self) -> bool:
        """تركيز أوّل عنصر منطقي عند فتح الشاشة. أعِد ``True`` إن نجحت."""
        try:
            first = self.content.GetItem(0)
            if first is not None:
                window = first.GetWindow()
                if window is not None:
                    window.SetFocus()
                    return True
        except Exception:
            pass
        return False

    def on_enter(self) -> bool:
        """يُستدعى عند الضغط على مفتاح الإدخال (Enter) في هذه الشاشة.

        تُعيد ``True`` إذا عالجت الشاشة المفتاح (فلا يُمرَّر إلى العنصر الذي
        يحمل التركيز)، أو ``False`` ليُترك السلوك الافتراضي (مثل تفعيل الزر).
        """
        return False

    def confirm_action(self) -> None:
        """موضع (Ctrl+Enter): تنفيذ الإجراء الرئيسي إن وُجد."""
        return False

    def next_action(self) -> None:
        """موضع (Ctrl+N): الإجراء التالي إن وُجد."""
        return False

    def on_shortcut(self, key: str) -> bool:
        """تعامل مع اختصارات خاصة بالشاشة. أعِد ``True`` إذا تمّت المعالجة."""
        return False

    # ------------------------------------------------------------------
    def on_theme_changed(self) -> None:
        """يُستدعى بعد تغيير نمط العرض (يُعاد بناؤه في الشاشات الديناميكية)."""
        self.Refresh()
