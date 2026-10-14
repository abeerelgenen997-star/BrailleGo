# Build Braille Go EXE for Windows

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

Write-Host "Building Braille Go..." -ForegroundColor Cyan
$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  Write-Error "Virtualenv not found. Run: py -3 -m venv .venv; .\.venv\Scripts\activate; pip install -r requirements.txt"
}

& $python -m pip install --upgrade pyinstaller | Out-Null
& $python -m PyInstaller --clean BrailleGo.spec

if (Test-Path "dist\BrailleGo\BrailleGo.exe") {
  Write-Host "Build successful:" -ForegroundColor Green
  Write-Host "  dist\BrailleGo\BrailleGo.exe"
} else {
  Write-Error "Build failed: BrailleGo.exe not found"
}
