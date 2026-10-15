# TESTING.md

## نظرة عامة

تم تنفيذ اختبارات آلية لوحدات Core الأساسية باستخدام pytest. اختبارات UI محدودة عبر pytest-qt (حيثما أمكن بدون تعقيد زائد).

## بيئة الاختبار

- Python 3.14.7
- pytest 8.4.2, pytest-qt 4.5.0
- wxPython 4.3.2 (اختبارات الواجهة الأساسية) + PySide6 6.12.0 (احتياطي)
- pyttsx3 2.99 + comtypes 1.4.17
- OS: Windows 11 (بيئة التطوير الحالية)

## أوامر التشغيل

```powershell
cd C:\Users\Hamadah\Downloads\BrailleGo
.\.venv\Scripts\python.exe -m pytest -v
```

تشغيل ملف محدد:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_braille.py -v
```

## الملفات المختبرة

1. `tests/test_braille.py`
- تحويل خلية من dots إلى Unicode والعكس
- `transcribe()` للعربية والإنجليزية
- `describe_difference_ar()` لشرح الفرق بين خليتين
- معالجة أرقام مختلطة + فراغ + خلية فارغة

2. `tests/test_exercises.py`
- تصحيح `CHOOSE_TEXT` صحيح/خاطئ
- تصحيح `BUILD_CELL` بناءً على dots
- تصحيح `BUILD_CELLS` يتحقق من عدد الخلايا

3. `tests/test_progress.py`
- `evaluate_level()` يمرر المستوى عند استيفاء الشروط
- `can_advance()` يعود false عند عدم الاكتمال
- `available_levels()` يفتح المستوى الأول فقط مبدئيًا
- `overall_progress()` حساب عام صحيح
- `SymbolStat.needs_review()` صحيح
- `ProgressStore.save_session()` يحفظ جلسة كاملة في معاملة

4. `tests/test_settings.py`
- قيم افتراضية صحيحة
- حفظ واستعادة عبر SQLite
- coerce للحدود (min/max)
- reset إلى الافتراضي

## نتائج فعلية

**آخر تشغيل ناجح:** `61 passed`

يشمل ذلك اختبارات الوحدات (Core/Data) + اختبارات دخانية لواجهة **wxPython**
(`tests/test_wx_smoke.py`) تتحقق من بناء كل الشاشات (ومنها **تحديد المستوى** و**تطابق الحرف**)،
وتوليد التدريبات (بما فيها تدريبات التطابق)، وتركيز صندوق السؤال (Ctrl+E)،
والتصحيح وحفظ التقدّم، وتبديل الأنماط، وحفظ الإعدادات، و**أربع لغات واجهة**،
وإدارة المستخدمين، ومحتوى **دليل برايل**، ووجود **قوائم الدروس/التدريبات/الاختبارات**.
اختبارات wx تُتخطّى تلقائيًا إذا لم يكن `wxPython` مثبّتًا.

## ما تم اختباره / ما تعذّر

- **نجح**: منطق برايل، تصحيح تدريبات، قواعد تقدّم، إعدادات، تخزين SQLite، وبناء شاشات wx والتفاعل معها.
- **نجح**: تشغيل الملف التنفيذي الواحد (`dist\BrailleGo.exe`) واختبار المُثبِّت (Inno Setup) تثبيتًا وإزالةً.
- **يحتاج اختبارًا يدويًا**: قراءة فعلية عبر NVDA/Narrator على جهاز نظيف (انظر ACCESSIBILITY.md).

## تغطية مقترحة لاحقة

- اختبار تصحيح `CHOOSE_PATTERN`, `TYPE_TEXT`, `BUILD_WORD`
- اختبار `braille_text.transcribe()` مع تشكيل عربي وشدة
- اختبار `curriculum` يولّد جميع الدروس بدون فجوات
- اختبار `app_context.snapshot()` كاملًا
- اختبار smoke لـMainWindow عبر pytest-qt
