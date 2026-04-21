#!/usr/bin/env pwsh
# -----------------------------------------------------------------------------
# build_paper.ps1
# Single entry point for compiling the EMNLP long paper LaTeX source.
# Runs latexmk -pdf with bibtex, captures exit code, page count, overfull/
# underfull warnings, and prints a one-line summary the scientist can read in
# every "edit .tex -> compile -> verify" cycle.
#
# Usage (from repo root):
#   pwsh scripts/build_paper.ps1                    # build edo_paper.tex (default)
#   pwsh scripts/build_paper.ps1 -Tex acl_latex     # build acl_latex.tex (template smoke)
#   pwsh scripts/build_paper.ps1 -Clean             # clean build artifacts first
# -----------------------------------------------------------------------------
[CmdletBinding()]
param(
    [string]$Tex = 'edo_paper',
    [switch]$Clean
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$texDir   = Join-Path $repoRoot 'article\latex'
$buildDir = Join-Path $repoRoot 'article\build'
$texFile  = Join-Path $texDir   "$Tex.tex"
$pdfFile  = Join-Path $buildDir "$Tex.pdf"
$logFile  = Join-Path $buildDir "$Tex.log"

if (-not (Test-Path $texFile)) {
    Write-Error "Source not found: $texFile"
    exit 2
}
if (-not (Test-Path $buildDir)) { New-Item -ItemType Directory -Force -Path $buildDir | Out-Null }

if ($Clean) {
    Get-ChildItem $buildDir -Filter "$Tex.*" -EA SilentlyContinue | Remove-Item -Force
    Write-Host "[clean] removed prior build artifacts for $Tex" -ForegroundColor DarkGray
}

# latexmk argument order matters; -output-directory must be quoted in PS
$outDirArg = "-output-directory=$buildDir"
Push-Location $texDir
try {
    Write-Host ("[build] latexmk -pdf " + $outDirArg + " " + (Split-Path $texFile -Leaf)) -ForegroundColor DarkCyan
    & latexmk -pdf -interaction=nonstopmode -file-line-error "$outDirArg" (Split-Path $texFile -Leaf) | Out-Null
    $exit = $LASTEXITCODE
} finally {
    Pop-Location
}

# Parse log: page count, overfull/underfull lines, errors
$pageCount = $null
$overfull = 0
$underfull = 0
$errors = @()
if (Test-Path $logFile) {
    $logText = Get-Content $logFile -Raw
    if ($logText -match 'Output written on .*\((\d+) pages?,') {
        $pageCount = [int]$matches[1]
    }
    $overfull  = ([regex]::Matches($logText, [regex]::Escape('Overfull \hbox'))).Count
    $underfull = ([regex]::Matches($logText, [regex]::Escape('Underfull \hbox'))).Count
    $errLines = $logText -split "`n" | Where-Object { $_ -match '^! ' -or $_ -match ':\d+:.*Error' }
    $errors = @($errLines | Select-Object -First 10)
}

Write-Host ''
Write-Host ('=' * 60) -ForegroundColor DarkGray
if ($exit -eq 0) {
    Write-Host "[OK]   build succeeded" -ForegroundColor Green
} else {
    Write-Host "[FAIL] latexmk exit code = $exit" -ForegroundColor Red
}
if ($null -ne $pageCount) {
    Write-Host "[INFO] PDF pages (incl. Limitations + Refs): $pageCount"
}

# ACL strict rule: main body only counts toward the 8-page limit.
# Locate the page on which Limitations starts via pdftotext.
$mainBodyPages = $null
if (Test-Path $pdfFile) {
    try {
        $limitsPage = $null
        for ($p = 1; $p -le $pageCount; $p++) {
            $txt = & pdftotext -f $p -l $p $pdfFile - 2>$null
            if ($txt -match '(?m)^\s*Limitations\s*$') { $limitsPage = $p; break }
        }
        if ($null -ne $limitsPage) {
            # Per demand.md §2: main body <= 8 content pages; Limitations does NOT count.
            # If Limitations appears at the TOP of page N (first content heading with <= 4 lines
            # of preceding content on that page), the main body ended at page N-1 → COMPLIANT.
            # Otherwise main body used all of page N-1 + part of page N → OVER.
            # Use non-layout mode to detect Limitations heading reliably
            $limitsPageText = & pdftotext -f $limitsPage -l $limitsPage $pdfFile - 2>$null
            $linesBeforeLimits = 0
            foreach ($L in ($limitsPageText -split "`r?`n")) {
                # Limitations as section heading: exact line match (pdftotext non-layout puts headings on own lines)
                if ($L -match '^\s*Limitations\s*$') { break }
                if ($L.Trim().Length -gt 0 -and $L -notmatch '^\s*\d+\s*$') { $linesBeforeLimits++ }
            }
            # Threshold: if ≤ 3 non-empty lines precede "Limitations" on its page,
            # treat Limitations as page-top → main body = limitsPage - 1.
            if ($linesBeforeLimits -le 3) {
                $mainBodyPages = $limitsPage - 1
            } else {
                $mainBodyPages = $limitsPage
            }
            $color = if ($mainBodyPages -le 8) { 'Green' } else { 'Red' }
            $verdict = if ($mainBodyPages -le 8) { 'COMPLIANT' } else { 'OVER 8-page submission cap' }
            Write-Host ("[INFO] Main body ends on page $mainBodyPages (Limitations on page $limitsPage, $linesBeforeLimits preceding lines): $verdict") -ForegroundColor $color
        } else {
            Write-Host "[WARN] Could not locate Limitations heading; cannot verify ACL 8-page rule." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[WARN] pdftotext probe failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "[INFO] Overfull hboxes: $overfull   Underfull hboxes: $underfull"
if ($errors.Count -gt 0) {
    Write-Host "[ERR ] First $($errors.Count) error/critical lines:" -ForegroundColor Red
    foreach ($e in $errors) { Write-Host "       $e" -ForegroundColor Red }
}
Write-Host ('=' * 60) -ForegroundColor DarkGray
if (Test-Path $pdfFile) {
    $sz = [math]::Round((Get-Item $pdfFile).Length / 1KB, 1)
    Write-Host "[PDF ] $pdfFile ($sz KB)"
}

exit $exit
