<#
.SYNOPSIS
  One-shot after play stop: move TODAY masters into day\raw + export ship candidates with markers.
.DESCRIPTION
  Zero memory for Kyle. No invent. No publish.
  Guards (Codex W0): session mutex · no growing/locked masters · mtime-today only.
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File "D:\WoW B-Roll Storage\_scripts\Session-End-Ship.ps1"
#>
[CmdletBinding()]
param(
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd'),
  [string]$Base = 'D:\WoW B-Roll Storage',
  [int]$Seconds = 30,
  [switch]$ToDrive,
  [switch]$SkipStableCheck
)

$ErrorActionPreference = 'Stop'
$scripts = Join-Path $Base '_scripts'
$move = Join-Path $scripts 'Move-TodayMastersToDayRoot.ps1'
$export = Join-Path $scripts 'Export-ShipCandidates.ps1'
$guards = Join-Path $scripts 'Gcs-SessionEnd-Guards.ps1'
if (-not (Test-Path -LiteralPath $guards)) {
  $guards = Join-Path $PSScriptRoot 'Gcs-SessionEnd-Guards.ps1'
}
if (Test-Path -LiteralPath $guards) { . $guards }

if (-not (Test-Path -LiteralPath $move)) { Write-Error "Missing $move"; exit 2 }
if (-not (Test-Path -LiteralPath $export)) { Write-Error "Missing $export"; exit 2 }

$mutex = $null
if (Get-Command Enter-GcsSessionMutex -ErrorAction SilentlyContinue) {
  $mutex = Enter-GcsSessionMutex -TimeoutMs 500
  if ($null -eq $mutex) {
    Write-Host 'SESSION_END_BUSY another Session-End holds mutex'
    exit 3
  }
}

try {
  Write-Host ("==== Session-End-Ship day={0} ====" -f $Day)

  $dayStart = [DateTime]::ParseExact($Day, 'yyyy-MM-dd', $null).Date
  $dayEnd = $dayStart.AddDays(1)

  function Test-IsTodayMaster([System.IO.FileInfo]$f) {
    if (Get-Command Test-GcsTodayMasterStrict -ErrorAction SilentlyContinue) {
      return (Test-GcsTodayMasterStrict -File $f -DayStart $dayStart -DayEnd $dayEnd)
    }
    return ($f.LastWriteTime -ge $dayStart -and $f.LastWriteTime -lt $dayEnd)
  }

  # Pre-scan base for growing masters (OBS still recording)
  $pre = @()
  if (Test-Path -LiteralPath $Base) {
    $pre += @(Get-ChildItem -LiteralPath $Base -File -ErrorAction SilentlyContinue |
      Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' -and (Test-IsTodayMaster $_) } |
      Select-Object -ExpandProperty FullName)
  }
  $rawPre = Join-Path (Join-Path $Base $Day) 'raw'
  if (Test-Path -LiteralPath $rawPre) {
    $pre += @(Get-ChildItem -LiteralPath $rawPre -File -ErrorAction SilentlyContinue |
      Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' -and (Test-IsTodayMaster $_) } |
      Select-Object -ExpandProperty FullName)
  }
  $pre = @($pre | Select-Object -Unique)
  if (-not $SkipStableCheck -and $pre.Count -gt 0 -and (Get-Command Test-GcsAnyGrowingMaster -ErrorAction SilentlyContinue)) {
    if (Test-GcsAnyGrowingMaster -Paths $pre) {
      Write-Host 'SESSION_END_REFUSE masters still growing or locked — stop OBS Record first'
      exit 4
    }
  }

  $moveArgs = @{ Base = $Base; Day = $Day }
  if ($SkipStableCheck) { $moveArgs.SkipStableCheck = $true }
  & $move @moveArgs

  $raw = Join-Path (Join-Path $Base $Day) 'raw'
  $masters = @()
  if (Test-Path -LiteralPath $raw) {
    $masters += @(Get-ChildItem -LiteralPath $raw -File -ErrorAction SilentlyContinue |
      Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' -and (Test-IsTodayMaster $_) } |
      Sort-Object LastWriteTime -Descending |
      Select-Object -ExpandProperty FullName)
  }
  $masters += @(Get-ChildItem -LiteralPath $Base -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match '\.(mp4|mkv|mov|m4v)$' -and (Test-IsTodayMaster $_) } |
    Select-Object -ExpandProperty FullName)
  $masters = @($masters | Select-Object -Unique)

  if ($masters.Count -eq 0) {
    Write-Host ("NO_MASTERS day={0} - record in OBS first (profile WoW B-Roll path = {1})" -f $Day, $Base)
    Write-Host 'SESSION_END_NOT_READY'
    exit 1
  }

  if (-not $SkipStableCheck -and (Get-Command Test-GcsAnyGrowingMaster -ErrorAction SilentlyContinue)) {
    if (Test-GcsAnyGrowingMaster -Paths $masters) {
      Write-Host 'SESSION_END_REFUSE masters unstable after move — stop OBS / wait for flush'
      exit 4
    }
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
}
finally {
  if (Get-Command Exit-GcsSessionMutex -ErrorAction SilentlyContinue) {
    Exit-GcsSessionMutex -Mutex $mutex
  }
}
