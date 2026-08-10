# Soft-poll WoW B-Roll harvest stage (Windows). No invent, no publish.
# Emits human lines + one machine READY_JSON line. Exit: 0=ready, 1=not ready, 2=error.
# Usage: .\soft_poll_windows.ps1 [-Days @('2026-08-10')] [-JsonOnly]
param(
  [string[]]$Days = @(),
  [switch]$JsonOnly
)
$ErrorActionPreference = 'Continue'
if (-not $Days -or $Days.Count -eq 0) {
  $today = Get-Date -Format 'yyyy-MM-dd'
  $yest = (Get-Date).AddDays(-1).ToString('yyyy-MM-dd')
  $Days = @($today, $yest)
}

function Count-Mp4([string]$path) {
  if (-not (Test-Path -LiteralPath $path)) { return 0 }
  return @((Get-ChildItem -LiteralPath $path -File -Filter '*.mp4' -ErrorAction SilentlyContinue)).Count
}

function Count-Files([string]$path) {
  if (-not (Test-Path -LiteralPath $path)) { return 0 }
  return @((Get-ChildItem -LiteralPath $path -File -ErrorAction SilentlyContinue)).Count
}

$dayReports = New-Object System.Collections.Generic.List[object]
$anyReady = $false

if (-not $JsonOnly) {
  Write-Output '=== ROOT D:\WoW B-Roll Storage ==='
  if (Test-Path -LiteralPath 'D:\WoW B-Roll Storage') {
    Get-ChildItem -LiteralPath 'D:\WoW B-Roll Storage' -Directory -ErrorAction SilentlyContinue |
      Where-Object { $_.Name -match '^\d{4}-\d{2}-\d{2}$' } |
      Sort-Object Name -Descending |
      Select-Object -First 10 |
      ForEach-Object { Write-Output ("  {0}  {1}" -f $_.LastWriteTime.ToString('s'), $_.Name) }
  } else {
    Write-Output 'MISS D:\WoW B-Roll Storage'
  }
  Write-Output '=== TEMP gcs_cand* ==='
  Get-ChildItem -LiteralPath 'C:\Users\kyled\AppData\Local\Temp' -Filter 'gcs_cand*' -ErrorAction SilentlyContinue |
    ForEach-Object { Write-Output ("  {0}  {1}" -f $_.LastWriteTime.ToString('s'), $_.Name) }
}

foreach ($day in $Days) {
  if (-not $JsonOnly) { Write-Output ("=== DAY {0} ===" -f $day) }
  $cand = "D:\WoW B-Roll Storage\$day\candidates"
  $stage = "C:\Users\kyled\AppData\Local\Temp\gcs_cand_$day"
  $markers = "D:\WoW B-Roll Storage\$day\markers"
  $raw = "D:\WoW B-Roll Storage\$day\raw"
  $dayRoot = "D:\WoW B-Roll Storage\$day"
  $jsonl = Join-Path $markers 'SESSION.jsonl'

  $candN = Count-Mp4 $cand
  $stageN = Count-Mp4 $stage
  $markerFiles = Count-Files $markers
  $hasJsonl = Test-Path -LiteralPath $jsonl
  $jsonlBytes = if ($hasJsonl) { (Get-Item -LiteralPath $jsonl).Length } else { 0 }
  $rawN = Count-Mp4 $raw
  $dayRootExists = Test-Path -LiteralPath $dayRoot

  # READY = harvestable candidates exist (day candidates or staged temp)
  $ready = ($candN -gt 0) -or ($stageN -gt 0)
  $reason = if ($ready) {
    if ($candN -gt 0) { 'candidates_present' } else { 'stage_present' }
  } elseif ($hasJsonl -and $jsonlBytes -gt 20 -and $rawN -eq 0 -and $candN -eq 0) {
    'markers_only_no_candidates'
  } elseif ($dayRootExists) {
    'day_root_empty'
  } else {
    'no_day_root'
  }

  if ($ready) { $anyReady = $true }

  $rep = [ordered]@{
    day              = $day
    ready            = $ready
    reason           = $reason
    candidates_n     = $candN
    stage_mp4_n      = $stageN
    markers_n        = $markerFiles
    session_jsonl    = $hasJsonl
    session_jsonl_bytes = $jsonlBytes
    raw_mp4_n        = $rawN
    day_root         = $dayRootExists
    paths            = [ordered]@{
      candidates = $cand
      stage      = $stage
      markers    = $markers
    }
  }
  $dayReports.Add($rep) | Out-Null

  if (-not $JsonOnly) {
    foreach ($p in @($stage, $cand, $dayRoot, $markers, $raw)) {
      if (Test-Path -LiteralPath $p) {
        Write-Output ("FOUND {0}" -f $p)
        $files = Get-ChildItem -LiteralPath $p -File -ErrorAction SilentlyContinue
        $mp4 = @($files | Where-Object { $_.Extension -eq '.mp4' })
        Write-Output ("  counts files={0} mp4={1}" -f @($files).Count, $mp4.Count)
      } else {
        Write-Output ("MISS  {0}" -f $p)
      }
    }
    Write-Output ("READY day={0} ready={1} reason={2}" -f $day, $ready, $reason)
  }
}

$payload = [ordered]@{
  schema           = 'gcs_soft_poll_ready/v1'
  generated_at_utc = (Get-Date).ToUniversalTime().ToString('o')
  host             = $env:COMPUTERNAME
  ready            = $anyReady
  days             = $dayReports
  law              = 'no_invent_no_publish; ready=candidates_or_stage_mp4'
}
$json = ($payload | ConvertTo-Json -Compress -Depth 6)
Write-Output ("READY_JSON:{0}" -f $json)
if (-not $JsonOnly) { Write-Output '=== DONE soft_poll ===' }

if ($anyReady) { exit 0 } else { exit 1 }
