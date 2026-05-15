# WealthLens data pipeline runner for Windows.
# Usage: .\automation\data-pipelines\update_all.ps1

$ErrorActionPreference = "Stop"
$PipelineDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$scripts = @(
    "fetch_wid_data.py",
    "fetch_ons_housing.py",
    "fetch_ons_wealth.py",
    "fetch_hmrc_stats.py"
)

$failed = @()

foreach ($script in $scripts) {
    $path = Join-Path $PipelineDir $script
    Write-Host "`n=== Running $script ===" -ForegroundColor Cyan
    python $path
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAILED: $script" -ForegroundColor Red
        $failed += $script
    }
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Ran $($scripts.Count) pipelines."

if ($failed.Count -gt 0) {
    Write-Host "Failed: $($failed -join ', ')" -ForegroundColor Red
    exit 1
} else {
    Write-Host "All pipelines completed successfully." -ForegroundColor Green
}
