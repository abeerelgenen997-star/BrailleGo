# BRAILLE_DATA_SOURCES.md

## مصادر موثوقة

يعتمد Braille Go على مصادر تعليمية موثقة لرموز برايل (غير مختَرعة):

1. **Wikipedia – Braille Arabic**  
   - https://en.wikipedia.org/wiki/Arabic_Braille  
   يصف الأحرف العربية، التشكيل (diacritics)، علامة الرقم، وعلامات الترقيم الشائعة.  
   *استُند إليها في*: جداول الحروف (`braille_alphabet_ar.py`)، التشكيل (`braille_diacritics.py`)، الأرقام (`braille_digits.py`)، الترقيم العربي (`braille_punctuation.py`).

2. **Wikipedia – English Braille**  
   - https://en.wikipedia.org/wiki/English_Braille  
   يوضح Grade 1 (uncontracted) ومواضع النقاط، وعلامة الحرف الكبير (`⠠` dot 6).  
   *استُند إليها في*: الحروف الإنجليزية (`braille_alphabet_en.py`).

3. **Wikipedia – Braille Patterns (Unicode)**  
   - https://en.wikipedia.org/wiki/Braille_Patterns  
   مرجع لترقيم النقاط (international convention 1-2-3 left column top-to-bottom, 4-5-6 right column) والتحقق من Unicode (U+2800–U+28FF).  
   *استُند إليه في*: `core/braille.py` (نموذج النقاط وترقيمها).

4. **RNIB – Braille** (مراجع توضيحية)  
   - https://www.rnib.org.uk/living-with-sight-loss/education-and-learning/braille/  
   توضيح مبادئ برايل العامة (6-dot) مناسب للمبتدئين. *مرجع توضيحي فقط*.

## ملاحظات مهمة

- **نظام النقاط**: 6 نقاط وفق Convention الدولية (1,2,3 عمود يسار من الأعلى للأسفل؛ 4,5,6 عمود يمين).
- **الترتيب العربي**: نحافظ على الترتيب المنطقي للحروف (left-to-right reading) كما في النص المطبوع؛ لا نطبّق انعكاسًا بصريًا. مثال موثق: `"بريل عربية"` → `⠃⠗⠊⠇ ⠷⠗⠃⠊⠡`.
- **الشدة (Shadda)**: تُكتب **قبل** الحرف الساكن الذي تُشدّد عليه في تمثيل برايل العربي (موثق في Wikipedia Arabic Braille).
- **الأرقام**: تُسبَق بعلامة الرقم `⠼` (dots 3-4-5-6). الأرقام 1-0 تستخدم الأنماط 1,12,14,145,15,124,1245,125,24,245.
- **الإنجليزي**: علامة الحرف الكبير `⠠` (dot 6) تسبق الحرف الكبير (uncontracted Grade 1).
- **تمييز الأنظمة**: الفواصل وعلامات الاستفهام/التنصيص تختلف بين العربي والإنجليزي؛ حُدّدت صراحة في `braille_punctuation.py` مع حقل `language`.
- **غير مختصر (Uncontracted)**: المنهج الحالي يستخدم المستوى غير المختصر لسهولة المبتدئين. يمكن توسيعه لاحقًا إلى contractions دون كسر البنية.
- **اختصارات**: بعض الرموز مثل `sym_abbreviation`/`sym_contraction_prefix` أُدرجت كرموز تعليمية توضيحية مع ملاحظات، دون افتراض قواعد اختصار معقدة غير موثقة صراحة.

## قائمة الملفات التي تحتوي البيانات

- `braille_go/core/braille_alphabet_ar.py` – الحروف العربية
- `braille_go/core/braille_alphabet_en.py` – الحروف الإنجليزية + علامة كبير
- `braille_go/core/braille_digits.py` – الأرقام + علامة الرقم
- `braille_go/core/braille_diacritics.py` – الحركات والتنوين والسكون والشدة
- `braille_go/core/braille_punctuation.py` – علامات الترقيم (عربي/إنجليزي)
- `braille_go/core/braille_symbols.py` – رموز شائعة
- `braille_go/core/braille_entries.py` – أنواع الإدخالات (`SymbolEntry`, `MultiCellEntry`)

## حدود

- لم يُنفّذ Braille Grade 2 الكامل؛ يركز التطبيق على التعليم المبتدئ (Grade 1) مع توثيق واضح.
- بعض الرموز التقنية (الرياضيات/الكمبيوتر المتقدمة) غير مضمّنة حاليًا لتفادي الافتراضات غير الموثقة.
- أي إضافة مستقبلية لرموز جديدة يجب توثيق مصدرها في هذا الملف قبل الإضافة.
