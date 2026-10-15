"""Braille Go - تطبيق تعليمي تفاعلي لتعلّم طريقة برايل.

Braille Go is an offline, accessible desktop application that teaches Arabic and
English braille to blind and low-vision learners.

The package is organised as follows::

    braille_go.core       # منطق برايل، المحتوى التعليمي، التدريبات، التقدّم
    braille_go.data       # قاعدة البيانات المحلية والإعدادات

الواجهة الرسومية في حزمة منفصلة ``braille_wx`` (wxPython) تعيد استخدام
``braille_go.core`` و``braille_go.data`` دون أي اعتماد على مكتبة الواجهة.
"""

__all__ = ["__app_name__", "__version__"]

__app_name__ = "Braille Go"
__version__ = "1.4.0"
