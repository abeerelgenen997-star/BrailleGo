# -*- mode: python ; coding: utf-8 -*-
#
# Onedir build of Braille Go — wxPython edition.
# Produces: dist\BrailleGo\BrailleGo.exe (folder distribution).
#
# Build:  .\.venv\Scripts\python.exe -m PyInstaller --clean BrailleGo_wx.spec

from pathlib import Path

block_cipher = None

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
        'numpy',
        'PIL',
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BrailleGo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='BrailleGo',
)
