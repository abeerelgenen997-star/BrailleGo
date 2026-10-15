"""Braille Go — نسخة واجهة wxPython.

هذه الحزمة توفر واجهة رسومية مبنية على **wxPython** (عناصر Windows الأصلية)
مع إعادة استخدام كامل لطبقة المنطق ``braille_go.core`` وطبقة البيانات
``braille_go.data`` الموجودة دون أي تعديل عليها.

الهدف الأساسي من هذه النسخة هو أفضل توافق ممكن مع قارئات الشاشة (NVDA و
Windows Narrator) لأن عناصر wx كلها عناصر Win32 أصلية، وهذا ما أوصى به
المراجع.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "1.4.0"
