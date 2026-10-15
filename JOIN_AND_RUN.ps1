# =====================================================================
#  Braille Go v1.2.0 — إعادة تجميع الحزم المُجزّأة والتحقق من السلامة
#  Braille Go — reassemble split packages and verify integrity
#
#  ضع هذا الملف في نفس مجلد ملفات الأجزاء، ثم شغّله.
#  سيُعيد تجميع كل حزمة موجودة أجزاؤها إلى ملف واحد ويتحقق من SHA-256:
#     BrailleGo-Standalone.exe.partNN  ->  BrailleGo.exe
#     BrailleGo-Setup-1.2.0.exe.partNN ->  BrailleGo-Setup-1.2.0.exe
#
#  التشغيل:  powershell -ExecutionPolicy Bypass -File JOIN_AND_RUN.ps1
# =====================================================================

$ErrorActionPreference = "Stop"

$dir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $dir

# بصمات SHA-256 المتوقّعة (الإصدار 1.2.0)
$EXPECTED = @{
    "BrailleGo-Standalone.exe"   = "CED33A438C1837A95F49C7062D3B8912C9D448C82513A8E557EFFA2721CBEDDC"
    "BrailleGo-Setup-1.2.0.exe"  = "3D549F08D64F00CC440EF856EC650A66020CEC8345968678265251AB3C7B20EE"
}

# الاسم النهائي لكل حزمة (المفتاح = بادئة ملفات الأجزاء).
$FINAL_NAME = @{
    "BrailleGo-Standalone.exe"  = "BrailleGo.exe"
    "BrailleGo-Setup-1.2.0.exe" = "BrailleGo-Setup-1.2.0.exe"
}

function Join-Package {
    param(
        [Parameter(Mandatory = $true)][string]$Prefix
    )

    $parts = Get-ChildItem -Filter "$Prefix.part*" -ErrorAction SilentlyContinue | Sort-Object Name
    if (-not $parts -or $parts.Count -eq 0) {
        return $false
    }

    $final = $FINAL_NAME[$Prefix]
    $target = Join-Path $dir $final
    if (Test-Path $target) { Remove-Item $target -Force }

    Write-Host ("Reassembling {0} from {1} part(s)..." -f $final, $parts.Count) -ForegroundColor Cyan

    $out = [System.IO.File]::Create($target)
    try {
        foreach ($p in $parts) {
            $bytes = [System.IO.File]::ReadAllBytes($p.FullName)
            $out.Write($bytes, 0, $bytes.Length)
        }
    } finally {
        $out.Close()
    }

    $expected = $EXPECTED[$Prefix]
    if ($expected) {
        $actual = (Get-FileHash $target -Algorithm SHA256).Hash
        Write-Host ("SHA256: {0}" -f $actual)
        if ($actual -ne $expected) {
            Write-Warning "تحذير: بصمة $final لا تطابق المتوقّع. قد يكون التنزيل غير مكتمل أو تالفًا."
            Write-Warning "Checksum mismatch for $final."
        } else {
            Write-Host "تم التحقق من السلامة بنجاح. / Integrity OK." -ForegroundColor Green
        }
    }

    Write-Host ("  -> {0}" -f $target) -ForegroundColor Green
    return $true
}

$didAnything = $false
foreach ($prefix in $EXPECTED.Keys) {
    if (Join-Package -Prefix $prefix) { $didAnything = $true }
}

if (-not $didAnything) {
    Write-Error "لم يتم العثور على أي ملفات أجزاء (*.exe.part*) في: $dir"
}

Write-Host ""
Write-Host "تم. / Done." -ForegroundColor Green
Write-Host "  BrailleGo.exe               : شغّله مباشرة (نسخة محمولة)."
Write-Host "  BrailleGo-Setup-1.2.0.exe   : ثبّت البرنامج على الجهاز."
