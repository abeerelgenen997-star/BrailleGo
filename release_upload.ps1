# Upload Braille Go release assets to GitHub with retries.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File release_upload.ps1 -Tag v1.3.0
#
# Expects the split parts in dist\parts\ (see Split-File helper / build_wx.ps1).

param(
    [string]$Tag = "v1.3.0",
    [int]$MaxAttempts = 12,
    [int]$BackoffSeconds = 8
)

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

$partsDir = Join-Path $root "dist\parts"
if (-not (Test-Path $partsDir)) {
    Write-Error "Parts folder not found: $partsDir"
}

$files = Get-ChildItem $partsDir -File | Sort-Object Name
if (-not $files -or $files.Count -eq 0) {
    Write-Error "No assets found in $partsDir"
}

Write-Host ("Uploading {0} asset(s) to release {1}..." -f $files.Count, $Tag) -ForegroundColor Cyan

$failed = @()
foreach ($f in $files) {
    $ok = $false
    for ($attempt = 1; $attempt -le $MaxAttempts -and -not $ok; $attempt++) {
        Write-Host ("  [{0}] {1} (attempt {2}/{3})" -f (Get-Date -Format HH:mm:ss), $f.Name, $attempt, $MaxAttempts)
        $output = & gh release upload $Tag $f.FullName --clobber 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0) {
            $ok = $true
            Write-Host ("  OK: {0}" -f $f.Name) -ForegroundColor Green
        } else {
            Write-Host ("  retry in {0}s ..." -f $BackoffSeconds) -ForegroundColor Yellow
            Start-Sleep -Seconds $BackoffSeconds
        }
    }
    if (-not $ok) {
        Write-Host ("  FAILED: {0}" -f $f.Name) -ForegroundColor Red
        $failed += $f.Name
    }
}

if ($failed.Count -gt 0) {
    Write-Host ("`nThese assets failed: {0}" -f ($failed -join ", ")) -ForegroundColor Red
    exit 1
}
Write-Host "`nAll assets uploaded successfully." -ForegroundColor Green
