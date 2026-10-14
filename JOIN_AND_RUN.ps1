# =====================================================================
#  Braille Go — النسخة المحمولة (ملف واحد) إعادة تجميع
#  Braille Go — Standalone (single-file) reassembly
#
#  ضع هذا الملف في نفس المجلد الذي يحتوي على ملفات الأجزاء:
#     BrailleGo-Standalone.exe.part01 ... partNN
#  ثم شغّله بالزر الأيمن ← "Run with PowerShell"
#  (أو من الطرفية:  powershell -ExecutionPolicy Bypass -File JOIN_AND_RUN.ps1 )
#
#  الناتج: ملف واحد  BrailleGo.exe  — شغّله بضغطة مزدوجة.
# =====================================================================

$ErrorActionPreference = "Stop"

$dir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $dir

Write-Host "Braille Go — reassembling standalone app..." -ForegroundColor Cyan

$parts = Get-ChildItem -Filter "BrailleGo-Standalone.exe.part*" -ErrorAction SilentlyContinue | Sort-Object Name
if (-not $parts -or $parts.Count -eq 0) {
    Write-Error "لم يتم العثور على ملفات الأجزاء في: $dir`nNo part files found in this folder."
}

Write-Host ("Found {0} part(s)." -f $parts.Count)

$exe = Join-Path $dir "BrailleGo.exe"
if (Test-Path $exe) { Remove-Item $exe -Force }

# دمج الأجزاء بالترتيب إلى ملف تنفيذي واحد
$out = [System.IO.File]::Create($exe)
try {
    foreach ($p in $parts) {
        $bytes = [System.IO.File]::ReadAllBytes($p.FullName)
        $out.Write($bytes, 0, $bytes.Length)
    }
} finally {
    $out.Close()
}

# التحقق من السلامة (SHA-256)
$expected = "74D9CE2FDA2A4FF37887F4BEEBC54F7F12A0E7E80B5D890C226EC06AEE2A2884"
$actual = (Get-FileHash $exe -Algorithm SHA256).Hash
Write-Host ("SHA256: {0}" -f $actual)
if ($actual -ne $expected) {
    Write-Warning "تحذير: بصمة الملف لا تطابق المتوقّع. قد يكون التنزيل غير مكتمل أو تالفًا."
    Write-Warning "Checksum mismatch — the download may be incomplete or corrupted."
} else {
    Write-Host "تم التحقق من السلامة بنجاح. / Integrity check passed." -ForegroundColor Green
}

Write-Host ""
Write-Host "تم! شغّل التطبيق بالنقر المزدوج على:" -ForegroundColor Green
Write-Host ("  {0}" -f $exe)
Write-Host "Done. Just double-click the file above to run Braille Go."
