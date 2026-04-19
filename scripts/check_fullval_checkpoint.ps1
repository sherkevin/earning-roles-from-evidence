#!/usr/bin/env powershell
<#
.SYNOPSIS
  Print per-method checkpoint progress for a fullval run dir (no API calls).
.PARAMETER RunDir
  e.g. artifacts\round1\run_20260413_075132
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$RunDir
)

$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not [System.IO.Path]::IsPathRooted($RunDir)) {
    $RunDir = Join-Path $repoRoot $RunDir
}

$methods = @("fixed_peer_calibrated", "fixed_static_roles", "fixed_self_claim")
$expected = 7405

Write-Host "Run dir: $RunDir"
Write-Host ("=" * 72)
foreach ($m in $methods) {
    $d = Join-Path $RunDir $m
    $ckpt = Join-Path $d "_ckpt_preds.jsonl"
    $done = 0
    if (Test-Path $ckpt) {
        $done = (Get-Content $ckpt | Measure-Object -Line).Lines
    }
    $hasMetrics = Test-Path (Join-Path $d "metrics.json")
    $pct = if ($expected -gt 0) { [math]::Round(100.0 * $done / $expected, 2) } else { 0 }
    $status = if ($hasMetrics) { "DONE" } elseif ($done -gt 0) { "CHECKPOINT" } else { "EMPTY" }
    Write-Host ("{0,-22} {1,5}/{2} ({3}%)  {4}" -f $m, $done, $expected, $pct, $status)
}
Write-Host ("=" * 72)
Write-Host "Resume: same --resume-run-dir + --workers N; do not delete _ckpt_preds.jsonl."
Write-Host "If quota/API errors: fix key/billing, re-run; only missing task_ids execute."
