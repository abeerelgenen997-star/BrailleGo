# Braille Go

تطبيق سطح مكتب حقيقي تعليمي لتعلّم برايل العربي والإنجليزي للمكفوفين وضعاف البصر، مبني باستخدام Python + PySide6.

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
