# بنية التطبيق (Architecture)

## نظرة عامة

Braille Go هو تطبيق سطح مكتب منفصل الطبقات (layers):

- Presentation (UI): PySide6 (شاشات + خلايا برايل مخصصة)
- Services: Speech (QtTextToSpeech), Accessibility (QAccessible)
- Domain (Core): Braille model, Symbols, Curriculum, Exercises, Progress rules
- Data: SQLite (settings, progress, state) مع WAL ومعاملة واحدة

## الدوائر الأساسية

- `core/braille.py`: BrailleCell + تحويلات (Unicode/bitmask/dots). يدعم 8-dot داخليًا، ويستخدم 6-dot في العرض.
- `core/symbols.py`: `BrailleSymbol`, `SymbolRepository` يجمع البيانات من `braille_alphabet_*` و`braille_digits` و`braille_punctuation` و`braille_diacritics` و`braille_symbols`.
- `core/braille_text.py`: `transcribe()` عربي/إنجليزي. ملاحظة: العربية تحافظ على الترتيب المنطقي (لا انعكاس بصري)، والشدة تُدرج قبل الحرف الساكن وفق الممارسة.
- `core/curriculum.py`: بيانات منهجية (11 مستوى × 41 درس). قابل للتوسع.
- `core/exercises.py`: توليد + تصحيح (`grade`) مع تفسيرات عربية وبمشتّتات متشابهة.
- `core/progress.py`: قواعد إتقان (threshold 85% افتراضي) + تقييم المستوى + رموز تحتاج مراجعة.
- `data/db.py`: SCHEMA_VERSION 1، WAL، معاملات، quarantine للقاعدة التالفة، `backup_to`.
- `data/settings.py`: Settings + backend (SQLite/Memory)، coerce + bounds.
- `data/progress_store.py`: حفظ جلسة كاملة في معاملة + `record_answer`/`finalize_session` للحفظ التدريجي.
- `app_context.py`: يربط كل الخدمات + إشارات Qt (`settings_changed`, `progress_changed`).
- `ui/braille_cell_widget.py`: رسم مخصص + أحداث لوحة مفاتيح (1-6, arrows, space, enter, clear) + وصف وصولي حي.
- `ui/theme.py`: ثيم + palette + stylesheet + ألوان قابلة للتخصيص.
- `ui/screens/*`: شاشة لكل ميزة (Home, Lessons, Lesson, Practice, Exams, Review, Progress, Settings, Help).

## تدفق البيانات

1. المستخدم يفتح درس → `AppContext.generate_exercises()` 
2. يعرض `LessonScreen` كل تمرين → يقرأ إدخال خلية/خيارات
3. `grade()` يُصحّح ويُنشئ Feedback بالعربية
4. `progress.record_answer()` يحفظ فورًا (استقرار ضد الإغلاق غير المتوقع)
5. نهاية الجلسة `finalize_session()` يُحدّث `lesson_progress` + يحدّث نقطة الاستكمال
6. `evaluate_level()` + `available_levels()` تتحكّم بفتح المستويات التالية

## ملاحظات التصميم

- فصل تام بين Core وUI (Core لا يستورد PySide6)
- استثناءات برمجية تُحوّل لرسائل عربية (`SettingsError`, `DatabaseError`, `BrailleError`)
- Speech اختياري: NullSpeechService عند عدم التوفر
- إمكانية الوصول: أسماء واضحة، مناطق حيّة، إعلانات غير مُحوّلة للتركيز
- Arabic RTL في الواجهة، Braille يُقرأ LTR (منطقي)
- بيانات برايل لا تُختَرَع؛ مستندة إلى مصادر موثقة
