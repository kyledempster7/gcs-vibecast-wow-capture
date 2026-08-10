<#
.SYNOPSIS
  One-shot after play stop: move OBS masters into day\raw + export ship candidates with markers.
.DESCRIPTION
  Zero memory for Kyle. No invent. No publish.
  Uses today's day root under D:\WoW B-Roll Storage.
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Session-End-Ship.ps1"
#>
[CmdletBinding()]
param(
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd'),
  [string]$Base = 'D:\WoW B-Roll Storage',
  [int]$Seconds = 30,
  [switch]$ToDrive
)

$ErrorActionPreference = 'Stop'
$scripts = Join-Path $Base '_scripts'
$move = Join-Path $scripts 'Move-TodayMastersToDayRoot.ps1'
$export = Join-Path $scripts 'Export-ShipCandidates.ps1'

if (-not (Test-Path -LiteralPath $move)) { Write-Error "Missing $move"; exit 2 }
if (-not (Test-Path -LiteralPath $export)) { Write-Error "Missing $export"; exit 2 }

Write-Host "==== Session-End-Ship day=$Day ===="
& $move -Base $Base -Day $Day

$raw = Join-Path (Join-Path $Base $Day) 'raw'
$masters = @()
if (Test-Path -LiteralPath $raw) {
  $masters = @(Get-ChildItem -LiteralPath $raw -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -ExpandProperty FullName)
}

# Also pick any leftover masters still sitting on Base root (Move may have been partial)
$masters += @(Get-ChildItem -LiteralPath $Base -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' } |
  Select-Object -ExpandProperty FullName)

$masters = @($masters | Select-Object -Unique)
if ($masters.Count -eq 0) {
  Write-Host "NO_MASTERS day=$Day — record in OBS first (profile WoW B-Roll path = $Base)"
  Write-Host "SESSION_END_NOT_READY"
  exit 1
}

Write-Host ("MASTERS n={0}" -f $masters.Count)
$masters | ForEach-Object { Write-Host ("  {0}" -f $_) }

$exportArgs = @{
  Day         = $Day
  Seconds     = $Seconds
  MasterPaths = $masters
  UseMarkers  = $true
}
if ($ToDrive) { $exportArgs.ToDrive = $true }

& $export @exportArgs
$rc = $LASTEXITCODE
if ($null -eq $rc) { $rc = 0 }

$cand = Join-Path (Join-Path $Base $Day) 'candidates'
$nCand = 0
if (Test-Path -LiteralPath $cand) {
  $nCand = @(Get-ChildItem -LiteralPath $cand -Filter '*.mp4' -ErrorAction SilentlyContinue).Count
}
$man = Join-Path (Join-Path $Base $Day) 'MANIFEST.json'
Write-Host ("SESSION_END_DONE day={0} candidates_mp4={1} manifest={2} export_rc={3}" -f $Day, $nCand, (Test-Path $man), $rc)
Write-Host "Mac next: bash .../post_play_harvest.sh"
exit $rc
