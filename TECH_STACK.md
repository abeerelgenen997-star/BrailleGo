# TECH_STACK

## تقنيات أساسية

- Python 3.14.7
- PySide6-Essentials 6.12.0, PySide6-Addons 6.12.0 (Qt 6.12.0)
- SQLite3 (مدمج مع Python)
- PyInstaller 6.16.0 (تغليف EXE)
- pytest 8.4.2 + pytest-qt 4.5.0 (اختبارات)

## ملاحظات

- QtTextToSpeech من PySide6-Addons (لا حاجة لمكتبات خارجية للنطق)
- استخدام QAccessible للإعلانات + أسماء الوصول
- QPainter لرسم خلية برايل التفاعلية (تحكّم كامل بالتركيز والحالة)
- قاعدة بيانات مع PRAGMA journal_mode=WAL، synchronous=NORMAL
- إعدادات مخزنة كـ JSON في عمود `value` بجدول `settings`

## أسباب الاختيار

- PySide6: واجهة سطح مكتب أصلية، دعم جيد لـ accessibility، يدعم Arabic RTL، متوافق مع Windows 10/11.
- SQLite: محلي بالكامل، سريع، مناسب للتطبيقات التعليمية، بدون خادم.
- PyInstaller: شائع، يجمع الموارد، ينتج مجلد قابل للتشغيل.
- pytest-qt: لاختبار UI أساسيات دون متصفح.
