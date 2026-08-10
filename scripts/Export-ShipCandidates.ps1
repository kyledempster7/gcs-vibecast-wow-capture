<#
.SYNOPSIS
  Export short ship candidates from WoW OBS masters (Windows).
.DESCRIPTION
  Law: approved candidates only — not raw OBS dump.
  Default: first N seconds (-t) via ffmpeg stream copy into
  D:\WoW B-Roll Storage\<day>\candidates\ + MANIFEST.json
  Optional: -ToDrive stages under G:\My Drive\GCS-VibeCast-Offload\<day>\
.EXAMPLE
  .\Export-ShipCandidates.ps1 -Day 2026-08-09 -Seconds 30 -ToDrive
#>
[CmdletBinding()]
param(
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd'),
  [int]$Seconds = 30,
  [string[]]$MasterPaths = @(),
  [switch]$ToDrive,
  [string]$Ffmpeg = '',
  # When set (or day markers\SESSION.jsonl exists), prefer talk/broll/gather windows; hard-skip skip_zone.
  [string]$MarkersJsonl = '',
  [switch]$UseMarkers,
  # Codex W0-4: silent t=0 after marker reject is banned unless explicitly allowed
  [switch]$AllowFallbackT0,
  # Allow weak record_start = first marker timestamp (default OFF when UseMarkers)
  [switch]$AllowWeakRecordStart
)

$ErrorActionPreference = 'Stop'
if (-not $Ffmpeg) {
  $winget = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter 'ffmpeg.exe' -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName
  $Ffmpeg = if ($winget) { $winget } else { 'ffmpeg' }
}
$ffprobe = Join-Path (Split-Path $Ffmpeg) 'ffprobe.exe'
if (-not (Test-Path $ffprobe)) { $ffprobe = 'ffprobe' }

$dayRoot = "D:\WoW B-Roll Storage\$Day"
$cand = Join-Path $dayRoot 'candidates'
New-Item -ItemType Directory -Force -Path $cand | Out-Null

if (-not $MasterPaths -or $MasterPaths.Count -eq 0) {
  Write-Error 'Pass -MasterPaths with one or more master .mp4 paths'
  exit 2
}

if (-not $MarkersJsonl) {
  $defaultMarkers = Join-Path $dayRoot 'markers\SESSION.jsonl'
  if (Test-Path -LiteralPath $defaultMarkers) { $MarkersJsonl = $defaultMarkers }
}

# Align with join_markers.py: paired broll/rotate/gather ends, talk pad, skip intervals.
$TalkPad = 15.0
$SkipPad = 5.0

function Get-MarkerWindows([string]$jsonlPath) {
  $windows = New-Object System.Collections.Generic.List[object]
  $skips = New-Object System.Collections.Generic.List[object]
  $recordStart = $null
  $openBroll = $null
  $openRotate = $null
  $openGather = $null
  if (-not $jsonlPath -or -not (Test-Path -LiteralPath $jsonlPath)) {
    return @{ windows = @(); skips = @(); record_start = $null; status = 'NO_MARKERS' }
  }
  $lines = Get-Content -LiteralPath $jsonlPath -ErrorAction SilentlyContinue
  foreach ($line in $lines) {
    if (-not $line) { continue }
    try { $o = $line | ConvertFrom-Json } catch { continue }
    $bid = [string]$o.button_id
    $st = [string]$o.state
    if (-not $st) { $st = 'pulse' }
    $ts = $null
    if ($o.ts_utc) {
      try { $ts = [DateTimeOffset]::Parse([string]$o.ts_utc) } catch {}
    }
    if (-not $ts) { continue }
    if ($bid -match 'record_start' -and -not $recordStart) { $recordStart = $ts }
  }
  $usedWeak = $false
  if (-not $recordStart) {
    if ($AllowWeakRecordStart) {
      foreach ($line in $lines) {
        try { $o = $line | ConvertFrom-Json } catch { continue }
        if ($o.ts_utc) {
          try { $recordStart = [DateTimeOffset]::Parse([string]$o.ts_utc); $usedWeak = $true; break } catch {}
        }
      }
    }
  }
  if (-not $recordStart) {
    return @{ windows = @(); skips = @(); record_start = $null; status = 'NO_RECORD_START'; weak = $false }
  }
  if ($usedWeak) {
    Write-Host 'MARKERS record_start=WEAK first_marker (AllowWeakRecordStart)'
  }

  function Sec([DateTimeOffset]$t) {
    return [math]::Round([math]::Max(0, ($t - $recordStart).TotalSeconds), 3)
  }

  foreach ($line in $lines) {
    if (-not $line) { continue }
    try { $o = $line | ConvertFrom-Json } catch { continue }
    $bid = [string]$o.button_id
    $st = [string]$o.state
    if (-not $st) { $st = 'pulse' }
    if (-not $o.ts_utc) { continue }
    try { $ts = [DateTimeOffset]::Parse([string]$o.ts_utc) } catch { continue }
    $t = Sec $ts
    if ($bid -eq 'layer_c.broll_enter' -and $st -eq 'begin') { $openBroll = $t }
    elseif ($bid -eq 'layer_c.broll_exit' -and $st -eq 'end' -and $null -ne $openBroll) {
      $windows.Add([ordered]@{ kind = 'broll'; start_sec = $openBroll; end_sec = $t }) | Out-Null
      $openBroll = $null
    }
    elseif ($bid -eq 'layer_c.rotate_begin' -and $st -eq 'begin') { $openRotate = $t }
    elseif ($bid -eq 'layer_c.rotate_end' -and $st -eq 'end' -and $null -ne $openRotate) {
      $windows.Add([ordered]@{ kind = 'rotate'; start_sec = $openRotate; end_sec = $t }) | Out-Null
      $openRotate = $null
    }
    elseif ($bid -eq 'layer_c.talk_peak') {
      $windows.Add([ordered]@{
          kind = 'talk_peak'
          start_sec = [math]::Round([math]::Max(0, $t - $TalkPad), 3)
          end_sec = [math]::Round($t + $TalkPad, 3)
        }) | Out-Null
    }
    elseif ($bid -eq 'layer_c.skip_zone') {
      $skips.Add([ordered]@{
          start_sec = [math]::Round([math]::Max(0, $t - $SkipPad), 3)
          end_sec = [math]::Round($t + $SkipPad, 3)
        }) | Out-Null
    }
    elseif ($bid -match 'gather_ui_on' -and $st -in @('begin', 'pulse')) { $openGather = $t }
    elseif ($bid -match 'gather_ui_off' -and $st -in @('end', 'pulse') -and $null -ne $openGather) {
      $windows.Add([ordered]@{ kind = 'gather_broll'; start_sec = $openGather; end_sec = $t }) | Out-Null
      $openGather = $null
    }
  }

  $status = if ($windows.Count -gt 0) { 'MARKER_WINDOWS' } else { 'RECORD_START_ONLY' }
  return @{ windows = $windows; skips = $skips; record_start = $recordStart; status = $status }
}

function Test-OverlapsSkip([double]$start, [double]$end, $skips) {
  foreach ($sk in @($skips)) {
    $ss = [double]$sk.start_sec
    $se = [double]$sk.end_sec
    if (-not ($end -lt $ss -or $start -gt $se)) { return $true }
  }
  return $false
}

function Invoke-TrimAt([string]$src, [string]$dest, [double]$startSec, [double]$sec) {
  $arg = '-y -ss {0} -t {1} -i "{2}" -c copy -avoid_negative_ts make_zero "{3}"' -f $startSec, $sec, $src, $dest
  $log = Join-Path $env:TEMP 'ff_ship_candidate.log'
  $p = Start-Process -FilePath $Ffmpeg -ArgumentList $arg -Wait -PassThru -NoNewWindow -RedirectStandardError $log
  return $p.ExitCode
}

$markerInfo = @{ windows = @(); skips = @(); record_start = $null; status = 'OFF' }
if ($UseMarkers -or $MarkersJsonl) {
  $markerInfo = Get-MarkerWindows $MarkersJsonl
  Write-Host ("MARKERS status={0} windows={1} skips={2}" -f $markerInfo.status, @($markerInfo.windows).Count, @($markerInfo.skips).Count)
}

$items = @()
$i = 0
foreach ($src in $MasterPaths) {
  if (-not (Test-Path -LiteralPath $src)) { Write-Error "missing $src"; exit 2 }
  $clips = @()
  $rejectedSkip = 0
  if ($markerInfo.status -eq 'MARKER_WINDOWS' -and @($markerInfo.windows).Count -gt 0) {
    foreach ($w in @($markerInfo.windows)) {
      $st = [double]$w.start_sec
      $en = [double]$w.end_sec
      if ($en -le $st) { continue }
      if (Test-OverlapsSkip $st $en $markerInfo.skips) {
        Write-Host ("SKIP_ZONE reject window kind={0} {1}-{2}" -f $w.kind, $st, $en)
        $rejectedSkip++
        continue
      }
      $dur = [math]::Min([double]$Seconds, [math]::Max(1.0, $en - $st))
      $clips += [ordered]@{ start_sec = $st; duration_sec = $dur; kind = [string]$w.kind; end_sec = $en }
    }
  }

  if ($clips.Count -eq 0) {
    # Codex W0-4: silent t=0 after skip-zone rejection is banned.
    # Product still allows first-N-seconds when markers exist but define no windows
    # (RECORD_START_ONLY / NO_MARKERS) — that is intentional ship policy, not a reject fallback.
    if ($UseMarkers -or $MarkersJsonl) {
      if ($markerInfo.status -eq 'NO_RECORD_START' -and -not $AllowFallbackT0) {
        Write-Error 'EXPORT_FAIL NO_RECORD_START — press record_start or -AllowWeakRecordStart / -AllowFallbackT0'
        exit 6
      }
      if ($rejectedSkip -gt 0 -and -not $AllowFallbackT0) {
        Write-Error ("EXPORT_FAIL NO_USABLE_WINDOWS all marker windows hit skip_zone (n={0}) — no silent t=0" -f $rejectedSkip)
        exit 5
      }
      if ($markerInfo.status -eq 'MARKER_WINDOWS' -and $rejectedSkip -eq 0 -and -not $AllowFallbackT0) {
        # Windows listed but none produced clips (bad intervals)
        Write-Error 'EXPORT_FAIL MARKER_WINDOWS empty after parse — no silent t=0'
        exit 5
      }
    }
    Write-Host ("FALLBACK_T0 status={0} rejected_skip={1} allow={2}" -f $markerInfo.status, $rejectedSkip, [bool]$AllowFallbackT0)
    $clips = @([ordered]@{ start_sec = 0; duration_sec = [double]$Seconds; kind = 'fallback_t0'; end_sec = [double]$Seconds })
  }

  foreach ($cl in $clips) {
    $i++
    $startSec = [double]$cl.start_sec
    $sec = [double]$cl.duration_sec
    # Unique name avoids concurrent overwrite of identical deterministic outputs (gap 37)
    $stamp = Get-Date -Format 'HHmmss'
    $outName = 'cand-{0}-{1:d2}-t{2}-s{3}-{4}.mp4' -f $Day, $i, [int][math]::Floor($sec), [int][math]::Floor($startSec), $stamp
    $dest = Join-Path $cand $outName
    if (Test-Path -LiteralPath $dest) {
      $outName = 'cand-{0}-{1:d2}-t{2}-s{3}-{4}-{5}.mp4' -f $Day, $i, [int][math]::Floor($sec), [int][math]::Floor($startSec), $stamp, $i
      $dest = Join-Path $cand $outName
    }
    Write-Host ("EXPORT {0} start={1} dur={2} kind={3}" -f $outName, $startSec, $sec, $cl.kind)
    $code = Invoke-TrimAt $src $dest $startSec $sec
    if ($code -ne 0 -or -not (Test-Path -LiteralPath $dest)) {
      Write-Error "ffmpeg failed exit=$code (see $env:TEMP\ff_ship_candidate.log)"
      exit 3
    }
    $sha = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLower()
    $srcSha = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLower()
    $len = (Get-Item -LiteralPath $dest).Length
    $dur = & $ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $dest 2>$null
    $extract = @{
      start_sec      = $startSec
      end_sec        = [double]$cl.end_sec
      duration_sec   = $sec
      method         = 'ffmpeg -c copy'
      marker_kind    = [string]$cl.kind
      marker_window  = ($markerInfo.status -eq 'MARKER_WINDOWS')
      markers_status = $markerInfo.status
    }
    $items += [ordered]@{
      id            = "cand-$Day-$i"
      role          = 'ship_candidate'
      localPath     = $dest
      filename      = $outName
      bytes         = $len
      duration_sec  = [math]::Round([double]$dur, 3)
      sha256        = $sha
      source_master = $src
      source_sha256 = $srcSha
      extract       = $extract
    }
  }
}

$manifest = [ordered]@{
  schema           = 'gcs_vibecast_ship_candidates/v1'
  day              = $Day
  generated_at_utc = (Get-Date).ToUniversalTime().ToString('o')
  host             = $env:COMPUTERNAME
  law              = 'approved candidates only — not raw OBS dump'
  transfer         = @{ preferred = 'tailscale_scp'; fallback = 'google_drive_GCS-VibeCast-Offload' }
  markers          = @{
    path     = $MarkersJsonl
    status   = $markerInfo.status
    windows  = @($markerInfo.windows)
    skips    = @($markerInfo.skips)
    note     = 'join_markers-aligned: paired ends, talk pad, skip_zone interval hard reject'
  }
  candidates       = $items
}
$manPath = Join-Path $dayRoot 'MANIFEST.json'
[IO.File]::WriteAllText($manPath, ($manifest | ConvertTo-Json -Depth 8))
Write-Host "MANIFEST $manPath"

if ($ToDrive) {
  $driveDay = "G:\My Drive\GCS-VibeCast-Offload\$Day"
  $driveCand = Join-Path $driveDay 'candidates'
  New-Item -ItemType Directory -Force -Path $driveCand | Out-Null
  Copy-Item -LiteralPath $manPath -Destination (Join-Path $driveDay 'MANIFEST.json') -Force
  foreach ($it in $items) {
    Copy-Item -LiteralPath $it.localPath -Destination (Join-Path $driveCand $it.filename) -Force
    Write-Host "DRIVE $($it.filename)"
  }
}
Write-Host 'OK'
