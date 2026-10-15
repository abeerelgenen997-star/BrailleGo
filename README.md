# Braille Go · برايل جو

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6.svg)](https://www.microsoft.com/windows)
[![UI: wxPython](https://img.shields.io/badge/UI-wxPython-1B7FBF.svg)](https://wxpython.org/)
[![Tests](https://img.shields.io/badge/tests-26%20passed-brightgreen.svg)](TESTING.md)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/abeerelgenen997-star/BrailleGo/releases)

**الإصدار:** `1.2.0` · **المنصة:** Windows 10/11 · **التقنيات:** Python + wxPython

تطبيق سطح مكتب حقيقي تعليمي لتعلّم برايل العربي والإنجليزي للمكفوفين وضعاف البصر، وللمبتدئين المبصرين، وللمدربين في مراكز التدريب والمؤسسات. الواجهة مبنية بـ **wxPython** لأن عناصرها عناصر Windows أصلية (Win32)، وهذا يمنح **توافقًا ممتازًا مع قارئات الشاشة** مثل NVDA وWindows Narrator وJAWS.

## الهدف

مساعدة المتعلّم على تعلّم برايل من الأساسيات حتى قراءة الكلمات والجمل، مع نظام مستويات، وتقدّم محفوظ محليًا، وإمكانية وصول متوافقة قدر الإمكان مع قارئات الشاشة.

## المزايا

- **واجهة wxPython** تمكّن قارئات الشاشة من قراءة كل عنصر (أزرار، حقول، بطاقات).
- **السؤال داخل صندوق نصّي (Edit Box)** قابل للقراءة الكاملة، مع **Ctrl+E** لتركيز صندوق الإدخال ونطق السؤال.
- واجهة عربية تدعم الاتجاه من اليمين إلى اليسار، مع تبديل فوري للغة (عربي/إنجليزي).
- خلية برايل تفاعلية: تعمل بالماوس ولوحة المفاتيح ووصف نصي لقارئ الشاشة.
- منهج متدرّج (11 مستوى، 41 درسًا) + تدريبات واختبارات ومراجعة الأخطاء + **الأرقام** داخل الدروس.
- تحويل نص <-> برايل (عربي/إنجليزي) مع التفسير عند الخطأ.
- حفظ التقدّم والإعدادات محليًا في SQLite (دون إنترنت).
- نطق موسّع عبر `pyttsx3` (SAPI5) مع اختيار الصوت، وأصوات تطبيق للصحيح/الخطأ.
- **إعدادات غنية ووضعيات عرض لكل أنواع ضعف البصر**: عادي فاتح/داكن، تباين مرتفع فاتح/داكن، أصفر على أسود، أبيض على أسود، عمى ألوان (deuteranopia/protanopia)، مع تحكّم مستقل بحجم الخط وحجم خلية برايل، والنص العريض، وتباعد الأسطر.
- **مختصرات لوحة مفاتيح شاملة** مع شاشة مخصّصة لعرضها.
- عمل دون إنترنت بعد التثبيت، وقابل للتنصيب كبرنامج حقيقي عبر **مُثبِّت**.

## متطلبات التشغيل

- Windows 10 أو Windows 11 (64-بت)
- 4GB RAM على الأقل (يوصى بـ 8GB)
- 250MB مساحة خالية

## التثبيت للمستخدم النهائي

نزّل أحد الخيارين من صفحة الإصدارات:

1. **المُثبِّت (موصى به):** `BrailleGo-Setup-1.2.0.exe` — ثبّت البرنامج بشكل طبيعي (اختصار في قائمة ابدأ + إزالة من «إضافة أو إزالة البرامج»).
2. **النسخة المحمولة (ملف واحد):** `BrailleGo.exe` — شغّله بنقرة مزدوجة مباشرة.

> التنزيل من: [Releases](https://github.com/abeerelgenen997-star/BrailleGo/releases/latest)

## تثبيت بيئة التطوير

```powershell
cd C:\Users\Hamadah\Downloads\BrailleGo
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## تشغيل المشروع

الواجهة الأساسية (wxPython):

```powershell
cd C:\Users\Hamadah\Downloads\BrailleGo
.\.venv\Scripts\python.exe run.py
```

أو مباشرةً:

```powershell
.\.venv\Scripts\python.exe -m braille_wx
```

النسخة الاحتياطية بواجهة Qt (PySide6) ما زالت متاحة:

```powershell
.\.venv\Scripts\python.exe run_qt.py
```

## بناء الملف التنفيذي (PyInstaller)

### ملف تنفيذي واحد (Standalone)

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm BrailleGo_wx_onefile.spec
```

الناتج: `dist\BrailleGo.exe` (ملف واحد بحجم ~18 ميجابايت).

أو استخدم السكربت الجاهز:

```powershell
powershell -ExecutionPolicy Bypass -File build_wx.ps1
```

### بناء المُثبِّت (Inno Setup)

بعد إنتاج `dist\BrailleGo.exe`، ولديك [Inno Setup 6](https://jrsoftware.org/isdl.php):

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm BrailleGo_wx_onefile.spec
"$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" /DAppVersion=1.2.0 installer\BrailleGo.iss
```

أو بأمر واحد:

```powershell
powershell -ExecutionPolicy Bypass -File build_wx.ps1 -Version 1.2.0 -Installer
```

الناتج: `dist\installer\BrailleGo-Setup-1.2.0.exe`.

> نسخة Qt القديمة: `BrailleGo.spec` و`BrailleGo_onefile.spec` (تعتمدان `run_qt.py`).

## الاختبارات

```powershell
cd C:\Users\Hamadah\Downloads\BrailleGo
.\.venv\Scripts\python.exe -m pytest -v
```

اختبارات واجهة wx تُتخطّى تلقائيًا إذا لم يتوفّر `wxPython`.

## بنية مختصرة

```
braille_go/            # طبقة مشتركة (منطق + بيانات) لا تعتمد على الواجهة
  core/                # منطق برايل، منهج، تدريبات، تقدّم، i18n
  data/                # SQLite + إعدادات + تخزين التقدّم + المستخدمون
  services/            # خدمة الصوت/النطق
  ui/                  # واجهة PySide6 (نسخة احتياطية)
  app.py, app_context.py
braille_wx/            # الواجهة الأساسية (wxPython)
  app.py, __main__.py  # نقطة الدخول
  main_frame.py        # النافذة الرئيسية والقوائم والمختصرات والتنقّل
  screens.py           # كل الشاشات (رئيسية، دروس، تدريب، اختبارات، مراجعة، ...)
  lesson_view.py       # شاشة الدرس وصندوق السؤال القابل للقراءة
  braille_cell.py      # خلية برايل التفاعلية (رسم مخصّص)
  theme.py             # وضعيات العرض والألوان
  speech.py, sounds.py # النطق وأصوات التطبيق
  a11y.py, widgets.py  # مساعدات إمكانية الوصول والعناصر
run.py                 # تشغيل wx (الأساسي)
run_qt.py              # تشغيل Qt (احتياطي)
installer/BrailleGo.iss
BrailleGo_wx_onefile.spec
```

## توثيق إضافي

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [TECH_STACK.md](TECH_STACK.md)
- [BRAILLE_DATA_SOURCES.md](BRAILLE_DATA_SOURCES.md)
- [ACCESSIBILITY.md](ACCESSIBILITY.md)
- [TESTING.md](TESTING.md)
- [USER_GUIDE.md](USER_GUIDE.md)

## ملاحظات

- التطبيق يعمل دون إنترنت بعد التثبيت. البيانات تُحفظ في `%APPDATA%\BrailleGo\braille_go.sqlite3` (أو عبر `BRAILLE_GO_DATA_DIR`).
- دعم النطق اختياري؛ إذا لم يتوفّر صوت عربي، يظل التطبيق صالحًا للاستخدام.
- عدم تغيير إعدادات النظام أو قارئ الشاشة.
- أنظمة الأرقام وعلامات الترقيم الوثيقة فيها في [BRAILLE_DATA_SOURCES.md](BRAILLE_DATA_SOURCES.md).

## التنزيل والإصدارات (Releases)

- **أحدث إصدار:** [Releases](https://github.com/abeerelgenen997-star/BrailleGo/releases/latest)
- إذا تجاوز الملف حدّ الرفع، يُقسّم إلى أجزاء `BrailleGo.exe.part01` … إلخ مع `JOIN_AND_RUN.ps1`؛ نزّل **كل** الأجزاء إلى نفس المجلد وشغّل السكربت (سيدمجها ويتحقق من SHA-256) فينتج ملف واحد `BrailleGo.exe`.

راجع [CHANGELOG.md](CHANGELOG.md) لمعرفة الجديد في كل إصدار.

## المساهمة (Contributing)

نرحّب بمساهمات المبرمجين والمعلّمين ومختصّي إمكانية الوصول:

1. اعمل **Fork** للمستودع.
2. أنشئ فرعًا جديدًا: `git checkout -b feature/اسم-الميزة`.
3. نفّذ تعديلاتك، وتأكد أن الاختبارات تنجح: `python -m pytest -q`.
4. ارفع الفرع وافتح **Pull Request**.

التفاصيل الكاملة في [CONTRIBUTING.md](CONTRIBUTING.md)، ونرجو الالتزام بـ [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## الترخيص (License)

هذا المشروع مُرخّص تحت **MIT License** — راجع ملف [LICENSE](LICENSE).
