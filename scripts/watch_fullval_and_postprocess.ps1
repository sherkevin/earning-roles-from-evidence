#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Polls until all three fullval metrics.json files exist, then runs post_fullval_chain.ps1.
.PARAMETER RunDir
  Relative or absolute path to the run directory (e.g. artifacts\round1\run_20260413_075132).
.PARAMETER PollIntervalSec
  How many seconds to sleep between checks (default 300).
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$RunDir,

    [int]$PollIntervalSec = 300
)

$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not [System.IO.Path]::IsPathRooted($RunDir)) {
    $RunDir = Join-Path $repoRoot $RunDir
}

$methods = @("fixed_peer_calibrated", "fixed_static_roles", "fixed_self_claim")
$startTime = Get-Date

Write-Host "[watch_fullval] Watching run dir: $RunDir"
Write-Host "[watch_fullval] Waiting for metrics.json in: $($methods -join ', ')"
Write-Host "[watch_fullval] Poll interval: ${PollIntervalSec}s"

while ($true) {
    $elapsed = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
    $done = @()
    $pending = @()

    foreach ($m in $methods) {
        $metricsFile = Join-Path $RunDir "$m\metrics.json"
        if (Test-Path $metricsFile) {
            $done += $m
        } else {
            $pending += $m
        }
    }

    Write-Host "[watch_fullval] ${elapsed}min elapsed — done: $($done.Count)/3  pending: $($pending -join ', ')"

    $expected = 7405
    foreach ($m in $methods) {
        $ckpt = Join-Path $RunDir "$m\_ckpt_preds.jsonl"
        $n = 0
        if (Test-Path $ckpt) { $n = (Get-Content $ckpt | Measure-Object -Line).Lines }
        if ($n -gt 0 -and -not (Test-Path (Join-Path $RunDir "$m\metrics.json"))) {
            $pct = [math]::Round(100.0 * $n / $expected, 1)
            Write-Host "  checkpoint $m : $n / $expected ($pct%)"
        }
    }

    if ($done.Count -eq 3) {
        Write-Host "[watch_fullval] All 3 methods complete! Running post_fullval_chain.ps1..."
        $postScript = Join-Path $repoRoot "scripts\post_fullval_chain.ps1"
        & $postScript -RunDir $RunDir
        Write-Host "[watch_fullval] post_fullval_chain.ps1 finished with exit code $LASTEXITCODE"
        break
    }

    Start-Sleep -Seconds $PollIntervalSec
}
