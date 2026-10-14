# Braille Go

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6.svg)](https://www.microsoft.com/windows)
[![UI: PySide6](https://img.shields.io/badge/UI-PySide6-41CD52.svg)](https://pypi.org/project/PySide6/)
[![Tests](https://img.shields.io/badge/tests-19%20passed-brightgreen.svg)](TESTING.md)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/abeerelgenen997-star/BrailleGo/releases)

**الإصدار:** `1.0.1` · **المنصة:** Windows 10/11 · **التقنيات:** Python + PySide6

تطبيق سطح مكتب حقيقي تعليمي لتعلّم برايل العربي والإنجليزي للمكفوفين وضعاف البصر، وللمبتدئين المبصرين، وللمدربين في مراكز التدريب والمؤسسات، مبني باستخدام Python + PySide6.

## الهدف

مساعدة المتعلّم على تعلّم برايل من الأساسيات حتى قراءة الكلمات والجمل، مع نظام مستويات، وتقدّم محفوظ محليًا، وإمكانية وصول متوافقة قدر الإمكان مع NVDA وWindows Narrator.

## المزايا

- واجهة عربية تدعم الاتجاه من اليمين إلى اليسار
- خلية برايل تفاعلية: تعمل بالماوس ولوحة المفاتيح ووصف نصي لقارئ الشاشة
- منهج متدرّج (11 مستوى، 41 درسًا) + تدريبات واختبارات ومراجعة الأخطاء
- تحويل نص <-> برايل (عربي/إنجليزي) مع التفسير عند الخطأ
- حفظ التقدّم والإعدادات محليًا في SQLite
- دعم صوتي اختياري عبر QtTextToSpeech (لا يُلزم استخدام التطبيق)
- إعدادات قابلة للتخصيص (خطوط، خلايا برايل، ثيم فاتح/داكن، تباين مرتفع، ألوان النقاط)
- عمل دون إنترنت بعد التثبيت
- قابل للتوسع (منهج وقواعد قابلة للإضافة دون إعادة بناء كبير)

## متطلبات التشغيل

- Windows 10 أو Windows 11
- 4GB RAM على الأقل (يوصى بـ 8GB)
- 200MB مساحة خالية

## تثبيت بيئة التطوير

```powershell
cd C:\Users\Hamadah\Downloads\BrailleGo
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## تشغيل المشروع

```powershell
cd C:\Users\Hamadah\Downloads\BrailleGo
.\.venv\Scripts\python.exe run.py
```

أو مباشرةً:

```powershell
cd C:\Users\Hamadah\Downloads\BrailleGo
.\.venv\Scripts\python.exe -m braille_go
```

## بناء ملف EXE (PyInstaller)

يوجد ملف `BrailleGo.spec` جاهز (يمكن تعديله إن رغبت). 

```powershell
cd C:\Users\Hamadah\Downloads\BrailleGo
.\.venv\Scripts\pyinstaller --clean BrailleGo.spec
```

سيظهر الملف التنفيذي في: `dist\BrailleGo\BrailleGo.exe`

بديل موصى به (يبني ويقلّم مكوّنات Qt غير المستخدمة تلقائيًا):

```powershell
powershell -ExecutionPolicy Bypass -File build_windows.ps1
```

يقوم `prune_build.ps1` بإزالة مكوّنات لا يستخدمها التطبيق (OpenGL البرمجي، وسائط FFmpeg، QML/Quick، الشبكة، الترجمات)، مما يقلّل الحجم بنحو 66 ميجابايت.

### بناء ملف واحد (Standalone)

لبناء ملف تنفيذي **واحد** يعمل بنقرة مزدوجة (يستبعد المكوّنات غير المستخدمة أثناء البناء):

```powershell
.\.venv\Scripts\pyinstaller --clean BrailleGo_onefile.spec
```

الناتج: `dist\BrailleGo.exe` (ملف واحد بحجم ~28 ميجابايت).

لإنشاء مجلد إصدار جاهز، انسخ `README.md` وملفات التوثيق مع المجلد `dist\BrailleGo` إلى مجلد `release\BrailleGo-<الإصدار>\`.

## الاختبارات

تشغيل جميع الاختبارات:

```powershell
cd C:\Users\Hamadah\Downloads\BrailleGo
.\.venv\Scripts\python.exe -m pytest -v
```

## بنية مختصرة

```
braille_go/
  core/        # منطق برايل، منهج، تدريبات، تقدّم
  data/        # SQLite + إعدادات + تخزين التقدّم
  services/    # صوت + إمكانية وصول
  ui/          # PySide6 شاشات + خلايا برايل + ثيم
  app.py       # مدخل التطبيق
  app_context.py
```

## توثيق إضافي

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [TECH_STACK.md](TECH_STACK.md)
- [BRAILLE_DATA_SOURCES.md](BRAILLE_DATA_SOURCES.md)
- [ACCESSIBILITY.md](ACCESSIBILITY.md)
- [TESTING.md](TESTING.md)
- [USER_GUIDE.md](USER_GUIDE.md)

## ملاحظات

- التطبيق يعمل دون إنترنت بعد التثبيت. البيانات تحفظ في `%APPDATA%\BrailleGo\braille_go.sqlite3` (أو عبر `BRAILLE_GO_DATA_DIR`).
- دعم النطق اختياري؛ إذا لم يتوفر صوت عربي، يظل التطبيق صالحًا للاستخدام.
- عدم تغيير إعدادات النظام أو قارئ الشاشة.
- أنظمة الأرقام وعلامات الترقيم الوثيقة فيها في [BRAILLE_DATA_SOURCES.md](BRAILLE_DATA_SOURCES.md).

## التنزيل والإصدارات (Releases)

يمكنك تنزيل النسخة الجاهزة للتشغيل (بدون تثبيت Python) من صفحة الإصدارات:

- **أحدث إصدار:** [Releases](https://github.com/abeerelgenen997-star/BrailleGo/releases/latest)
- الحزمة **ملف واحد** مُقسّم إلى أجزاء `BrailleGo-Standalone.exe.part01` … `part07`. نزّل **كل** الأجزاء مع `JOIN_AND_RUN.ps1` إلى نفس المجلد، ثم شغّل السكربت (سيدمجها ويتحقق من SHA-256) فينتج ملف واحد `BrailleGo.exe`.
- شغّل `BrailleGo.exe` بنقرة مزدوجة.

راجع [CHANGELOG.md](CHANGELOG.md) لمعرفة الجديد في كل إصدار.

## المساهمة (Contributing)

نرحّب بمساهمات المبرمجين والمعلّمين ومختصّي إمكانية الوصول. الطريقة:

1. اعمل **Fork** للمستودع.
2. أنشئ فرعًا جديدًا: `git checkout -b feature/اسم-الميزة`.
3. نفّذ تعديلاتك، وتأكد أن الاختبارات تنجح: `python -m pytest -q`.
4. ارفع الفرع وافتح **Pull Request**.

التفاصيل الكاملة في [CONTRIBUTING.md](CONTRIBUTING.md)، ونرجو الالتزام بـ [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## الترخيص (License)

هذا المشروع مُرخّص تحت **MIT License** — راجع ملف [LICENSE](LICENSE).
