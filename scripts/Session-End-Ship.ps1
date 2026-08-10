<#
.SYNOPSIS
  One-shot after play stop: move TODAY masters into day\raw + export ship candidates with markers.
.DESCRIPTION
  Zero memory for Kyle. No invent. No publish.
  Only masters for -Day (mtime or name stamp). Historical files on base are left alone.
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

Write-Host ("==== Session-End-Ship day={0} ====" -f $Day)
& $move -Base $Base -Day $Day

$raw = Join-Path (Join-Path $Base $Day) 'raw'
$dayStart = [DateTime]::ParseExact($Day, 'yyyy-MM-dd', $null).Date
$dayEnd = $dayStart.AddDays(1)
$stampA = $Day
$stampB = $Day.Replace('-', '')

function Test-IsTodayMaster([System.IO.FileInfo]$f) {
  if ($f.LastWriteTime -ge $dayStart -and $f.LastWriteTime -lt $dayEnd) { return $true }
  if ($f.Name.Contains($stampA) -or $f.Name.Contains($stampB)) { return $true }
  return $false
}

$masters = @()
if (Test-Path -LiteralPath $raw) {
  $masters += @(Get-ChildItem -LiteralPath $raw -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' -and (Test-IsTodayMaster $_) } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -ExpandProperty FullName)
}

# Leftover today masters still on Base (Move missed)
$masters += @(Get-ChildItem -LiteralPath $Base -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' -and (Test-IsTodayMaster $_) } |
  Select-Object -ExpandProperty FullName)

$masters = @($masters | Select-Object -Unique)
if ($masters.Count -eq 0) {
  Write-Host ("NO_MASTERS day={0} - record in OBS first (profile WoW B-Roll path = {1})" -f $Day, $Base)
  Write-Host 'SESSION_END_NOT_READY'
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
Write-Host 'Mac next: post_play_harvest.sh'
exit $rc
