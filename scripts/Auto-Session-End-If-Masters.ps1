<#
.SYNOPSIS
  If TODAY masters sit on storage base or day\raw but need export, run Session-End-Ship.
.DESCRIPTION
  No invent. No publish. Ignores historical masters (mtime must be today).
  W0-3: existing candidates do not strand NEW base/raw masters without export.
  Exit 0 = exported or already complete; 1 = no today masters; 2 = fail; 3 = busy; 4 = recording
#>
[CmdletBinding()]
param(
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd'),
  [string]$Base = 'D:\WoW B-Roll Storage'
)

$ErrorActionPreference = 'Stop'
$scripts = Join-Path $Base '_scripts'
$ship = Join-Path $scripts 'Session-End-Ship.ps1'
$guards = Join-Path $scripts 'Gcs-SessionEnd-Guards.ps1'
if (-not (Test-Path -LiteralPath $guards)) {
  $guards = Join-Path $PSScriptRoot 'Gcs-SessionEnd-Guards.ps1'
}
if (Test-Path -LiteralPath $guards) { . $guards }

$raw = Join-Path (Join-Path $Base $Day) 'raw'
$cand = Join-Path (Join-Path $Base $Day) 'candidates'
$dayStart = [DateTime]::ParseExact($Day, 'yyyy-MM-dd', $null).Date
$dayEnd = $dayStart.AddDays(1)

function Test-IsTodayMaster([System.IO.FileInfo]$f) {
  if (Get-Command Test-GcsTodayMasterStrict -ErrorAction SilentlyContinue) {
    return (Test-GcsTodayMasterStrict -File $f -DayStart $dayStart -DayEnd $dayEnd)
  }
  return ($f.LastWriteTime -ge $dayStart -and $f.LastWriteTime -lt $dayEnd)
}

$candN = 0
if (Test-Path -LiteralPath $cand) {
  $candN = @(Get-ChildItem -LiteralPath $cand -Filter '*.mp4' -ErrorAction SilentlyContinue).Count
}

$masters = @()
if (Test-Path -LiteralPath $Base) {
  $masters += @(Get-ChildItem -LiteralPath $Base -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' -and (Test-IsTodayMaster $_) })
}
if (Test-Path -LiteralPath $raw) {
  $masters += @(Get-ChildItem -LiteralPath $raw -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' -and (Test-IsTodayMaster $_) })
}

# Base-only masters always need ship. Raw masters with zero candidates need ship.
# Raw masters with candidates: still ship if base has extras OR raw count suggests new files
# without a MANIFEST newer than newest master.
$needShip = $false
if ($masters.Count -eq 0) {
  Write-Output 'NO_MASTERS - record first (today only)'
  exit 1
}

$baseOnly = @(Get-ChildItem -LiteralPath $Base -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' -and (Test-IsTodayMaster $_) })
if ($baseOnly.Count -gt 0) { $needShip = $true }
elseif ($candN -eq 0) { $needShip = $true }
else {
  $man = Join-Path (Join-Path $Base $Day) 'MANIFEST.json'
  $newestMaster = ($masters | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
  if (-not (Test-Path -LiteralPath $man)) {
    $needShip = $true
  } else {
    $manTime = (Get-Item -LiteralPath $man).LastWriteTime
    if ($newestMaster -gt $manTime) { $needShip = $true }
  }
}

if (-not $needShip) {
  Write-Output ("ALREADY_CANDIDATES n={0} (no newer masters than MANIFEST)" -f $candN)
  exit 0
}

Write-Output ("FOUND_TODAY_MASTERS n={0} cand={1} - running Session-End-Ship" -f $masters.Count, $candN)
if (-not (Test-Path -LiteralPath $ship)) {
  Write-Error "Missing $ship"
  exit 2
}
& $ship -Day $Day
exit $LASTEXITCODE
