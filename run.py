"""نقطة التشغيل الرئيسية لـ Braille Go (واجهة wxPython).

اختيار wxPython يجعل التطبيق متوافقًا مع قارئات الشاشة (NVDA، Narrator، JAWS)
على Windows، لأن عناصره عناصر Windows أصلية (Win32).
"""

from braille_wx.app import main

if __name__ == "__main__":
    raise SystemExit(main())
