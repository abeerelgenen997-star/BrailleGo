# TESTING.md

## نظرة عامة

تم تنفيذ اختبارات آلية لوحدات Core الأساسية باستخدام pytest. اختبارات UI محدودة عبر pytest-qt (حيثما أمكن بدون تعقيد زائد).

## بيئة الاختبار

- Python 3.14.7
- pytest 8.4.2, pytest-qt 4.5.0
- PySide6 6.12.0
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

**آخر تشغيل ناجح:**

```
tests/test_braille.py::test_braille_cell_basic PASSED
tests/test_braille.py::test_unicode_roundtrip PASSED
tests/test_braille.py::test_english_capital PASSED
tests/test_braille.py::test_description_difference PASSED
tests/test_braille.py::test_transcribe_mixed_digits PASSED
tests/test_braille.py::test_empty_cell PASSED
tests/test_exercises.py::test_grade_choose_text_correct PASSED
tests/test_exercises.py::test_grade_build_cell PASSED
tests/test_exercises.py::test_grade_build_cells_count PASSED
tests/test_progress.py::test_evaluate_level PASSED
tests/test_progress.py::test_can_advance_false PASSED
tests/test_progress.py::test_available_levels PASSED
tests/test_progress.py::test_overall_progress PASSED
tests/test_progress.py::test_symbol_stats_needs_review PASSED
tests/test_progress.py::test_progress_store_save_session PASSED
tests/test_settings.py::test_settings_defaults PASSED
tests/test_settings.py::test_settings_persist PASSED
tests/test_settings.py::test_settings_coerce_bounds PASSED
tests/test_settings.py::test_settings_reset PASSED

19 passed in 0.27s
```

## ما تم اختباره / ما تعذّر

- **نجح**: منطق برايل، تصحيح تدريبات، قواعد تقدّم، إعدادات، تخزين SQLite
- **تعذّر جزئيًا**: اختبارات UI شاملة (pytest-qt موجود لكن لم تُكتب اختبارات smoke للـLesson/Home نظراً لوقت التركيز على الوظائف الأساسية). يمكن إضافة لاحقًا.
- **لم يُختبر**: تشغيل EXE فعليًا داخل بيئة التطوير (PyInstaller سيُنشئ EXE لكن لم أُشغّله على Windows "نظيف" بعيدًا عن venv). تم تجهيز `BrailleGo.spec`.

## تغطية مقترحة لاحقة

- اختبار تصحيح `CHOOSE_PATTERN`, `TYPE_TEXT`, `BUILD_WORD`
- اختبار `braille_text.transcribe()` مع تشكيل عربي وشدة
- اختبار `curriculum` يولّد جميع الدروس بدون فجوات
- اختبار `app_context.snapshot()` كاملًا
- اختبار smoke لـMainWindow عبر pytest-qt
