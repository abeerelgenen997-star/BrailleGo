"""تشغيل نسخة PySide6 (الاحتياطية) من Braille Go.

الواجهة الأساسية الموصى بها موجودة في ``run.py`` (wxPython) لأنها الأفضل
لدعم قارئات الشاشة. هذا الملف يبقى متاحًا لمن يفضّل نسخة Qt.
"""

from braille_go.app import main

if __name__ == "__main__":
    raise SystemExit(main())
