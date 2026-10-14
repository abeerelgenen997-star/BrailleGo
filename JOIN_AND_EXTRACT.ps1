# =====================================================================
#  Braille Go — إعادة تجميع الحزمة المُجزّأة ثم فك الضغط
#  Braille Go — reassemble the split download and extract it
#
#  ضع هذا الملف في نفس المجلد الذي يحتوي على ملفات الأجزاء:
#     BrailleGo-Windows-x64.zip.part01 ... partNN
#  ثم شغّله بالزر الأيمن ← "Run with PowerShell"
#  (أو من الطرفية:  powershell -ExecutionPolicy Bypass -File JOIN_AND_EXTRACT.ps1 )
# =====================================================================

$ErrorActionPreference = "Stop"

$dir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $dir

Write-Host "Braille Go — reassembling download..." -ForegroundColor Cyan

$parts = Get-ChildItem -Filter "BrailleGo-Windows-x64.zip.part*" -ErrorAction SilentlyContinue | Sort-Object Name
if (-not $parts -or $parts.Count -eq 0) {
    Write-Error "لم يتم العثور على ملفات الأجزاء في: $dir`nNo part files found in this folder."
}

Write-Host ("Found {0} part(s)." -f $parts.Count)

$zip = Join-Path $dir "BrailleGo-Windows-x64.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }

# دمج الأجزاء بالترتيب إلى ملف واحد
$out = [System.IO.File]::Create($zip)
try {
    foreach ($p in $parts) {
        $bytes = [System.IO.File]::ReadAllBytes($p.FullName)
        $out.Write($bytes, 0, $bytes.Length)
    }
} finally {
    $out.Close()
}

# التحقق من السلامة (SHA-256)
$expected = "57F137461B5302E683C92C8D278100418614056EB03BFCCC7445FDF8436B673D"
$actual = (Get-FileHash $zip -Algorithm SHA256).Hash
Write-Host ("SHA256: {0}" -f $actual)
if ($actual -ne $expected) {
    Write-Warning "تحذير: بصمة الملف لا تطابق المتوقّع. قد يكون التنزيل غير مكتمل أو تالفًا."
    Write-Warning "Checksum mismatch — the download may be incomplete or corrupted."
} else {
    Write-Host "تم التحقق من السلامة بنجاح. / Integrity check passed." -ForegroundColor Green
}

# فك الضغط
$dest = Join-Path $dir "BrailleGo"
Write-Host ("Extracting to: {0}" -f $dest)
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Expand-Archive -Path $zip -DestinationPath $dest -Force

Write-Host ""
Write-Host "تم! شغّل التطبيق من:" -ForegroundColor Green
Write-Host ("  {0}" -f (Join-Path $dest "BrailleGo.exe"))
Write-Host "Done. Launch the app from the path above."
