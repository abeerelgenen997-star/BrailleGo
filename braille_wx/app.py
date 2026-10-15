"""نقطة الدخول لنسخة wxPython من Braille Go.

يُنشئ هذا الملف تطبيق wx، ويهيّئ السياق (قاعدة البيانات والإعدادات والنطق)،
ويكوّن النافذة الرئيسية. أي خطأ غير متوقع يُعرض برسالة عربية واضحة بدل أن
يتوقف التطبيق صامتًا.
"""

from __future__ import annotations

import sys


def main() -> int:
    import wx

    from .context import build_context
    from .main_frame import MainFrame

    app = wx.App(False)
    app.SetAppName("Braille Go")
    app.SetAppDisplayName("Braille Go")

    try:
        context = build_context()
    except Exception as exc:  # pragma: no cover - startup guard
        wx.MessageBox(
            f"تعذّر تهيئة التطبيق: {exc}",
            "Braille Go",
            wx.OK | wx.ICON_ERROR,
        )
        return 1

    try:
        frame = MainFrame(context)
    except Exception as exc:  # pragma: no cover - startup guard
        try:
            context.shutdown()
        except Exception:
            pass
        wx.MessageBox(
            f"تعذّر فتح الواجهة: {exc}",
            "Braille Go",
            wx.OK | wx.ICON_ERROR,
        )
        return 1

    frame.Show()
    app.MainLoop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
