# -*- mode: python ; coding: utf-8 -*-
#
# Single-file (standalone) build of Braille Go.
# Produces: dist\BrailleGo.exe  — one file, just double-click to run.
#
# Unused Qt components are filtered out during analysis (see EXCLUDE_PATTERNS)
# so the resulting file is as small as possible.

import re
from pathlib import Path

block_cipher = None

# Files / folders that Braille Go never uses. Same pruning logic as prune_build.ps1.
EXCLUDE_PATTERNS = [
    r'opengl32sw\.dll',
    r'av(codec|format|util|device|filter)-',
    r'swscale-',
    r'swresample-',
    r'Qt6Multimedia',
    r'QtMultimedia',
    r'Qt6Network',
    r'QtNetwork',
    r'Qt6Qml',
    r'QtQml',
    r'Qt6Quick',
    r'QtQuick',
    r'Qt6Svg',
    r'QtSvg',
    r'Qt6VirtualKeyboard',
    r'qtvirtualkeyboardplugin',
    r'qsvg',
    r'translations',
    r'plugins[\\/]multimedia',
    r'plugins[\\/]tls',
    r'plugins[\\/]networkinformation',
    r'plugins[\\/]iconengines',
    r'plugins[\\/]platforminputcontexts',
]
_exclude = re.compile('|'.join(EXCLUDE_PATTERNS), re.IGNORECASE)

a = Analysis(
    ['run.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[
        ('braille_go', 'braille_go'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtTextToSpeech',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineCore',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.QtQuickWidgets',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtNetwork',
        'PySide6.QtSvg',
        'PySide6.QtVirtualKeyboard',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Drop unused Qt binaries / plugin data so the standalone file stays small.
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
