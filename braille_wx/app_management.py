"""إدارة التطبيق على ويندوز: المشاركة، فتح الروابط، مجلّد البيانات، والإزالة.

تُستخدم هذه الوحدة من شاشة الإعدادات لتوفير خيارات «مشاركة التطبيق»
و«التحقّق من التحديثات» و«فتح مجلّد البيانات» و«إزالة التطبيق»، بما يناسب
نظام ويندوز. كل العمليات محاطة بمعالجة أخطاء حتى يبقى التطبيق يعمل حتى لو
تعذّر تنفيذ أي منها (مثلًا تشغيله من نسخة محمولة بلا تثبيت).
"""

from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path

#: روابط المشروع الرسمية على GitHub.
REPO_URL = "https://github.com/abeerelgenen997-star/BrailleGo"
RELEASES_URL = REPO_URL + "/releases"
LATEST_RELEASE_URL = RELEASES_URL + "/latest"
ISSUES_URL = REPO_URL + "/issues"

#: الاسم الظاهر للتطبيق كما هو مسجَّل في المُثبِّت على ويندوز.
APP_DISPLAY_NAME = "Braille Go"


def open_url(url: str) -> bool:
    """افتح رابطًا في المتصفّح الافتراضي وأعِد نجاح العملية."""
    try:
        return bool(webbrowser.open(url))
    except Exception:
        return False


def open_data_folder() -> bool:
    """افتح مجلّد بيانات التطبيق (قاعدة البيانات والإعدادات) في مدير الملفات."""
    try:
        from braille_go.data.db import default_data_dir

        path = default_data_dir()
        path.mkdir(parents=True, exist_ok=True)
        os.startfile(str(path))  # type: ignore[attr-defined]
        return True
    except Exception:
        return False


def data_folder() -> Path | None:
    """أعِد مسار مجلّد بيانات التطبيق أو ``None`` عند تعذّر تحديده."""
    try:
        from braille_go.data.db import default_data_dir

        return default_data_dir()
    except Exception:
        return None


def find_uninstaller() -> str | None:
    """ابحث عن برنامج إزالة Braille Go المسجَّل على ويندوز.

    يبحث أولًا في سجل ويندوز عن أي برنامج عرضه يحتوي «braille»، ثم يتحقّق
    من المسارات المعتادة التي يستخدمها المُثبِّت. أعِد أمر الإزالة أو ``None``
    إن كانت النسخة محمولة (غير مثبّتة).
    """
    found = _find_uninstaller_in_registry()
    if found:
        return found
    for candidate in _candidate_uninstaller_paths():
        try:
            if candidate.exists():
                return str(candidate)
        except Exception:
            continue
    return None


def run_uninstaller(command: str) -> bool:
    """شغّل برنامج الإزالة بأفضل شكل ممكن."""
    command = (command or "").strip()
    if not command:
        return False
    for kwargs in ({}, {"shell": True}):
        try:
            subprocess.Popen(command, **kwargs)  # noqa: S603 - مسار موثوق من السجل
            return True
        except Exception:
            continue
    return False


# ----------------------------------------------------------------------
# تفاصيل التنفيذ
# ----------------------------------------------------------------------
def _find_uninstaller_in_registry() -> str | None:
    if sys.platform != "win32":
        return None
    try:
        import winreg  # type: ignore[import-not-found]
    except Exception:
        return None

    subkeys = (
        r"Software\Microsoft\Windows\CurrentVersion\Uninstall",
        r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    )
    roots = (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE)
    for root in roots:
        for subkey in subkeys:
            try:
                with winreg.OpenKey(root, subkey) as key:
                    count = winreg.QueryInfoKey(key)[0]
                    for index in range(count):
                        result = _probe_registry_entry(winreg, key, index)
                        if result:
                            return result
            except OSError:
                continue
    return None


def _probe_registry_entry(winreg, key, index: int) -> str | None:
    try:
        name = winreg.EnumKey(key, index)
    except OSError:
        return None
    try:
        with winreg.OpenKey(key, name) as entry:
            try:
                display = str(winreg.QueryValueEx(entry, "DisplayName")[0])
            except OSError:
                return None
            if "braille" not in display.lower():
                return None
            try:
                return str(winreg.QueryValueEx(entry, "UninstallString")[0])
            except OSError:
                return None
    except OSError:
        return None


def _candidate_uninstaller_paths() -> list[Path]:
    paths: list[Path] = []
    for env_key, sub in (
        ("LOCALAPPDATA", ("Programs", APP_DISPLAY_NAME)),
        ("ProgramFiles", (APP_DISPLAY_NAME,)),
        ("ProgramFiles(x86)", (APP_DISPLAY_NAME,)),
        ("ProgramW6432", (APP_DISPLAY_NAME,)),
    ):
        base = os.environ.get(env_key)
        if base:
            folder = Path(base).joinpath(*sub)
            paths.append(folder / "unins000.exe")
            paths.append(folder / "BrailleGo.exe")
    return paths


__all__ = [
    "REPO_URL",
    "RELEASES_URL",
    "LATEST_RELEASE_URL",
    "ISSUES_URL",
    "APP_DISPLAY_NAME",
    "open_url",
    "open_data_folder",
    "data_folder",
    "find_uninstaller",
    "run_uninstaller",
]
