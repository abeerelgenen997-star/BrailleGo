# Build Braille Go (wxPython) for Windows
#
# 1) Builds a single-file EXE (dist\BrailleGo.exe)
# 2) Optionally compiles the Inno Setup installer (dist\installer\BrailleGo-Setup-*.exe)
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File build_wx.ps1
#   powershell -ExecutionPolicy Bypass -File build_wx.ps1 -Version 1.4.0 -Installer

param(
    [string]$Version = "1.4.0",
    [switch]$Installer
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Virtualenv not found. Run: py -3 -m venv .venv; .\.venv\Scripts\activate; pip install -r requirements.txt"
}

Write-Host "Building Braille Go (wxPython) single-file EXE..." -ForegroundColor Cyan
if (Test-Path build) { Remove-Item build -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path dist)  { Remove-Item dist  -Recurse -Force -ErrorAction SilentlyContinue }

& $python -m PyInstaller --clean --noconfirm BrailleGo_wx_onefile.spec
if (-not (Test-Path "dist\BrailleGo.exe")) {
    Write-Error "Build failed: dist\BrailleGo.exe not found"
}

$exe = Get-Item "dist\BrailleGo.exe"
Write-Host ("Build successful: dist\BrailleGo.exe ({0:N1} MB)" -f ($exe.Length / 1MB)) -ForegroundColor Green

if ($Installer) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    $iscc = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $iscc) {
        Write-Error "Inno Setup 6 (ISCC.exe) not found. Install it from https://jrsoftware.org/isdl.php"
    }
    Write-Host "Compiling installer with Inno Setup..." -ForegroundColor Cyan
    & $iscc "/DAppVersion=$Version" "installer\BrailleGo.iss"
    Write-Host "Installer created in dist\installer\" -ForegroundColor Green
}
