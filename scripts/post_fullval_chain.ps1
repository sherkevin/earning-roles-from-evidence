# Post-process a completed chain fullval run (7405 x three main methods):
# validate_logs -> paired bootstrap -> merge round1_v3_main_table_fullval.csv
#
# Usage (PowerShell, repo root = current dir or auto-detected):
#   .\scripts\post_fullval_chain.ps1 -RunDir artifacts\round1\run_YYYYMMDD_HHMMSS
param(
    [Parameter(Mandatory = $true)]
    [string] $RunDir
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$run = $RunDir
if (-not [System.IO.Path]::IsPathRooted($run)) {
    $run = Join-Path $repoRoot $RunDir
}
if (-not (Test-Path $run)) {
    Write-Error "Run directory not found: $run"
}

Write-Host "[post_fullval_chain] validate_logs --all-methods"
python scripts/validate_logs.py $run --all-methods

Write-Host "[post_fullval_chain] paired bootstrap -> artifacts/round1_v3_paired_stats_fullval.csv"
python scripts/compute_paired_bootstrap.py `
    --run-dir $run `
    --baseline fixed_peer_calibrated `
    --compare fixed_static_roles fixed_self_claim `
    --metric answer_f1 `
    --n-bootstrap 10000 `
    --seed 42 `
    --out-csv artifacts/round1_v3_paired_stats_fullval.csv

Write-Host "[post_fullval_chain] merge fullval main table"
python scripts/run_round1_v3.py `
    --merge-summary-only `
    --resume-run-dir $run `
    --methods fixed_peer_calibrated,fixed_static_roles,fixed_self_claim `
    --artifacts-root artifacts/round1 `
    --summary-csv-name round1_v3_main_table_fullval.csv `
    --no-canonical-self-override

Write-Host "[post_fullval_chain] done."
