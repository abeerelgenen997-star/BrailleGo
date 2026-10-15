# -*- mode: python ; coding: utf-8 -*-
#
# Single-file (standalone) build of Braille Go — wxPython edition.
# Produces: dist\BrailleGo.exe  — one file, just double-click to run.
#
# Unused wxPython / Python components are filtered out during analysis
# (see EXCLUDE_PATTERNS) so the resulting file is as small as possible.
#
# Build:  .\.venv\Scripts\python.exe -m PyInstaller --clean BrailleGo_wx_onefile.spec

import re
from pathlib import Path

block_cipher = None

# Files / folders that Braille Go never uses.
EXCLUDE_PATTERNS = [
    r'tests[\\/]',
    r'wx[\\/]py[\\/]tests[\\/]',
    r'wx[\\/]tools[\\/]',
    r'\.pyi$',
    r'libgcc_s_',
    r'msvcp140d\.dll',
    r'vcruntime140d\.dll',
    r'ucrtbased\.dll',
    r'pyttsx3[\\/]drivers[\\/]nsss\.py$',
    r'pyttsx3[\\/]drivers[\\/]espeak\.py$',
    r'pyttsx3[\\/]drivers[\\/]dummy\.py$',
]
_exclude = re.compile('|'.join(EXCLUDE_PATTERNS), re.IGNORECASE)

a = Analysis(
    ['run.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[],
    hiddenimports=[
        'wx',
        'wx.adv',
        'wx.lib.scrolledpanel',
        'sqlite3',
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'comtypes',
        'winsound',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6',
        'shiboken6',
        'PyQt5',
        'PyQt6',
        'tkinter',
        'unittest',
        'pydoc',
        'doctest',
        'numpy',
        'PIL',
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Drop unused test/doc data so the standalone file stays small.
a.binaries = [b for b in a.binaries if not _exclude.search(b[0])]
a.datas = [d for d in a.datas if not _exclude.search(d[0])]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BrailleGo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
