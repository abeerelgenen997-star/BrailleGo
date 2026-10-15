# =====================================================================
#  Braille Go — إعادة تجميع الحزم المُجزّأة والتحقق من السلامة
#  Braille Go — reassemble split packages and verify integrity
#
#  ملاحظة: اعتبارًا من الإصدار 1.4.0 يُرفع البرنامج على GitHub كملف
#  كامل واحد (BrailleGo.exe و BrailleGo-Setup-1.4.0.exe) بدون تجزئة،
#  فلا حاجة لهذا السكربت. يبقى هذا الملف لخدمة الإصدارات الأقدم
#  (1.3.0 و1.2.0 و1.0.1) التي رُفعت مقسّمة إلى أجزاء.
#
#  NOTE: as of v1.4.0 the app ships as a single full file per package,
#  so this script is no longer needed for it. It is kept for the older
#  releases (1.3.0 / 1.2.0 / 1.0.1) that were uploaded split into parts.
#
#  ضع هذا الملف في نفس مجلد ملفات الأجزاء، ثم شغّله.
#  سيُعيد تجميع كل حزمة موجودة أجزاؤها إلى ملف واحد ويتحقق من SHA-256:
#     BrailleGo-Standalone.exe.partNN  ->  BrailleGo.exe
#     BrailleGo-Setup-1.3.0.exe.partNN ->  BrailleGo-Setup-1.3.0.exe
#
#  التشغيل:  powershell -ExecutionPolicy Bypass -File JOIN_AND_RUN.ps1
# =====================================================================

$ErrorActionPreference = "Stop"

$dir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $dir

# بصمات SHA-256 المتوقّعة (الإصدار 1.3.0)
$EXPECTED = @{
    "BrailleGo-Standalone.exe"   = "DC0D81A189898F0CEDF2607948E35C1D99E504A07752D849E6CA926F9A6F6250"
    "BrailleGo-Setup-1.3.0.exe"  = "EB97A2F6951EB4778DB120FCA09E1D7A0DEEE65F0CE9B968B40968AFC6B842A1"
}

# الاسم النهائي لكل حزمة (المفتاح = بادئة ملفات الأجزاء).
$FINAL_NAME = @{
    "BrailleGo-Standalone.exe"  = "BrailleGo.exe"
    "BrailleGo-Setup-1.3.0.exe" = "BrailleGo-Setup-1.3.0.exe"
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
Write-Host "  BrailleGo-Setup-1.3.0.exe   : ثبّت البرنامج على الجهاز."
