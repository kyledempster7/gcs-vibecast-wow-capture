<#
.SYNOPSIS
  If OBS masters sit on storage base or day\raw but candidates empty, run Session-End-Ship.
.DESCRIPTION
  Called from Mac after soft_poll when not READY. No invent. No publish.
  Exit 0 = exported or already have candidates; 1 = no masters; 2 = export fail
#>
[CmdletBinding()]
param(
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd'),
  [string]$Base = 'D:\WoW B-Roll Storage'
)

$ErrorActionPreference = 'Stop'
$scripts = Join-Path $Base '_scripts'
$ship = Join-Path $scripts 'Session-End-Ship.ps1'
$raw = Join-Path (Join-Path $Base $Day) 'raw'
$cand = Join-Path (Join-Path $Base $Day) 'candidates'

$candN = 0
if (Test-Path -LiteralPath $cand) {
  $candN = @(Get-ChildItem -LiteralPath $cand -Filter '*.mp4' -ErrorAction SilentlyContinue).Count
}
if ($candN -gt 0) {
  Write-Output ("ALREADY_CANDIDATES n={0}" -f $candN)
  exit 0
}

$masters = @()
if (Test-Path -LiteralPath $Base) {
  $masters += @(Get-ChildItem -LiteralPath $Base -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' })
}
if (Test-Path -LiteralPath $raw) {
  $masters += @(Get-ChildItem -LiteralPath $raw -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' })
}
$masters = @($masters | Select-Object -Unique FullName)

if ($masters.Count -eq 0) {
  Write-Output "NO_MASTERS — record first"
  exit 1
}

Write-Output ("FOUND_MASTERS n={0} — Session-End-Ship" -f $masters.Count)
if (-not (Test-Path -LiteralPath $ship)) {
  Write-Error "Missing $ship"
  exit 2
}
& $ship -Day $Day
exit $LASTEXITCODE
