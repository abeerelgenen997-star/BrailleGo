"""نقطة التشغيل الرئيسية لـ Braille Go (واجهة wxPython).

اختيار wxPython يجعل التطبيق متوافقًا مع قارئات الشاشة (NVDA، Narrator، JAWS)
على Windows. لتشغيل نسخة Qt الاحتياطية استخدم ``python run_qt.py``.
"""

from braille_wx.app import main

if __name__ == "__main__":
    raise SystemExit(main())
