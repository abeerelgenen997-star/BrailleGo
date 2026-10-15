"""Braille Go - تطبيق تعليمي تفاعلي لتعلّم طريقة برايل.

Braille Go is an offline, accessible desktop application that teaches Arabic and
English braille to blind and low-vision learners.

The package is organised as follows::

    braille_go.core       # منطق برايل، المحتوى التعليمي، التدريبات، التقدّم
    braille_go.data       # قاعدة البيانات المحلية والإعدادات
    braille_go.services   # الصوت وإمكانية الوصول
    braille_go.ui         # الواجهة الرسومية (PySide6)
"""

__all__ = ["__app_name__", "__version__"]

__app_name__ = "Braille Go"
__version__ = "1.3.0"
