"""أمر ``python -m braille_go`` — مشغّل مختصر لواجهة wxPython.

طبقة ``braille_go`` مخصّصة للمنطق والبيانات (Core/Data)، والواجهة في
``braille_wx``. هذا الملف مجرّد مُشغّل يعادل ``python run.py``.
"""

from braille_wx.app import main

if __name__ == "__main__":
    raise SystemExit(main())
