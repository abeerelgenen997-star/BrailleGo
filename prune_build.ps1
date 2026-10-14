# Prune unused PySide6/Qt components from a PyInstaller onedir build.
#
# Braille Go only uses: QtCore, QtGui, QtWidgets, QtTextToSpeech.
# Everything below is safe to remove and cuts the package size roughly in half:
#   - OpenGL software fallback (not used; widget painting uses the raster engine)
#   - QtMultimedia + FFmpeg codecs (no audio/video playback)
#   - QtQml / QtQuick (no QML)
#   - QtNetwork / TLS (the app is fully offline)
#   - QtSvg, VirtualKeyboard, Qt translations (UI strings come from the app itself)
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File prune_build.ps1 -Path dist\BrailleGo

param(
    [string]$Path = "dist\BrailleGo"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Path)) {
    Write-Error "Build folder not found: $Path"
}

$target = (Resolve-Path $Path).Path
$pyside = Join-Path $target "_internal\PySide6"

if (-not (Test-Path $pyside)) {
    Write-Error "PySide6 folder not found under: $target\_internal"
}

$before = (Get-ChildItem $target -Recurse -File | Measure-Object -Property Length -Sum).Sum

# File name patterns to remove anywhere under the PySide6 folder.
$filePatterns = @(
    "opengl32sw.dll",
    "av*.dll",
    "swscale-*.dll",
    "swresample-*.dll",
    "Qt6Multimedia*.dll",
    "QtMultimedia*.pyd",
    "Qt6Network.dll",
    "QtNetwork.pyd",
    "Qt6Qml*.dll",
    "QtQml*.pyd",
    "Qt6Quick*.dll",
    "QtQuick*.pyd",
    "Qt6Svg.dll",
    "QtSvg*.pyd",
    "Qt6VirtualKeyboard.dll",
    "qsvg.dll",
    "qsvgicon.dll",
    "qtvirtualkeyboardplugin.dll"
)

# Whole folders to remove (relative to the PySide6 folder).
$dirPatterns = @(
    "translations",
    "plugins\multimedia",
    "plugins\tls",
    "plugins\networkinformation",
    "plugins\iconengines",
    "plugins\platforminputcontexts"
)

foreach ($pattern in $filePatterns) {
    Get-ChildItem -Path $pyside -Recurse -File -Filter $pattern -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue }
}

foreach ($dir in $dirPatterns) {
    $full = Join-Path $pyside $dir
    if (Test-Path $full) {
        Remove-Item $full -Recurse -Force -ErrorAction SilentlyContinue
    }
}

$after = (Get-ChildItem $target -Recurse -File | Measure-Object -Property Length -Sum).Sum
$saved = ($before - $after) / 1MB

Write-Host ("Pruned unused Qt components: saved {0:N1} MB (now {1:N1} MB)" -f $saved, ($after / 1MB)) -ForegroundColor Green
