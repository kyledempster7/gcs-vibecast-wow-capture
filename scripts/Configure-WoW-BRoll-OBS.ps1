<#
.SYNOPSIS
  Configure OBS WoW_BRoll profile for product nights (path + dual audio tracks).
.DESCRIPTION
  Law: no invent FOOTAGE · no publish · refuse Fable profile path for product.
  Safe when OBS is not running. If OBS is running, writes STAGED config next to profile
  and exits 3 (do not thrash live OBS).
.NOTES
  RecTracks bitmask: 1=T1, 2=T2, 4=T3 → 3 = Desktop(T1)+Mic(T2).
  DesktopAudio mixers=1, AuxAudio mixers=2 after scene patch.
#>
[CmdletBinding()]
param(
  [switch]$ForceWhileObsRunning,
  [string]$DayRootBase = 'D:\WoW B-Roll Storage',
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$receiptDir = Join-Path $DayRootBase '_receipts'
New-Item -ItemType Directory -Force -Path $receiptDir | Out-Null
$receipt = Join-Path $receiptDir "OBS_CONFIGURE_$stamp.json"

$obsProc = Get-Process -Name 'obs64','obs32','obs' -ErrorAction SilentlyContinue
$obsRunning = [bool]$obsProc

$profileDir = Join-Path $env:APPDATA 'obs-studio\basic\profiles\WoW_BRoll_1440p60'
$basicIni = Join-Path $profileDir 'basic.ini'
$scenesDir = Join-Path $env:APPDATA 'obs-studio\basic\scenes'
$untitled = Join-Path $scenesDir 'Untitled.json'
$wowScene = Join-Path $scenesDir 'WoW_BRoll_Product.json'

$result = [ordered]@{
  schema = 'gcs_obs_configure/v1'
  ts_local = (Get-Date).ToString('o')
  host = $env:COMPUTERNAME
  obs_running = $obsRunning
  profile_ini = $basicIni
  day_root_base = $DayRootBase
  actions = @()
  law = 'no_invent_no_publish; product path D: not Fable Videos folder'
}

if (-not (Test-Path -LiteralPath $basicIni)) {
  $result.error = "missing profile: $basicIni"
  $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receipt -Encoding utf8
  Write-Error $result.error
  exit 2
}

if ($obsRunning -and -not $ForceWhileObsRunning) {
  $result.status = 'STAGED_OBS_RUNNING'
  $result.note = 'OBS process present — refuse live rewrite. Close OBS then re-run, or -ForceWhileObsRunning.'
  # still write a staged basic.ini next to profile for apply later
  $staged = Join-Path $profileDir "basic.ini.STAGED_PRODUCT_$stamp"
  $ini = Get-Content -LiteralPath $basicIni -Raw
  $ini2 = $ini
  $ini2 = $ini2 -replace '(?m)^FilePath=.*$', "FilePath=$($DayRootBase -replace '\\','\\')"
  # PowerShell -replace uses regex; escape carefully
  $pathEsc = $DayRootBase.Replace('\', '\\')
  $ini2 = [regex]::Replace($ini, '(?m)^FilePath=.*$', "FilePath=$pathEsc")
  $ini2 = [regex]::Replace($ini2, '(?m)^RecFilePath=.*$', "RecFilePath=$pathEsc")
  $ini2 = [regex]::Replace($ini2, '(?m)^Mode=Simple$', 'Mode=Advanced')
  $ini2 = [regex]::Replace($ini2, '(?m)^RecTracks=\d+$', 'RecTracks=3')
  if (-not $DryRun) {
    Set-Content -LiteralPath $staged -Value $ini2 -Encoding utf8
    $result.staged_ini = $staged
  }
  $result.actions += 'wrote_staged_ini_only'
  $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receipt -Encoding utf8
  Write-Output "STAGED obs_running receipt=$receipt"
  Write-Output ($result | ConvertTo-Json -Compress)
  exit 3
}

# Backup + apply profile
$bak = Join-Path $profileDir "basic.ini.bak_$stamp"
if (-not $DryRun) {
  Copy-Item -LiteralPath $basicIni -Destination $bak -Force
}
$ini = Get-Content -LiteralPath $basicIni -Raw
$pathEsc = $DayRootBase.Replace('\', '\\')
$ini2 = [regex]::Replace($ini, '(?m)^FilePath=.*$', "FilePath=$pathEsc")
$ini2 = [regex]::Replace($ini2, '(?m)^RecFilePath=.*$', "RecFilePath=$pathEsc")
# Advanced multi-track: bitmask 3 = track1+track2
if ($ini2 -match '(?m)^Mode=Simple') {
  $ini2 = [regex]::Replace($ini2, '(?m)^Mode=Simple$', 'Mode=Advanced')
  $result.actions += 'mode_simple_to_advanced'
}
$ini2 = [regex]::Replace($ini2, '(?m)^RecTracks=\d+$', 'RecTracks=3')
$result.actions += 'path_to_d_storage', 'rectracks_3_dual'

if (-not $DryRun) {
  # OBS basic.ini is often UTF-8 BOM
  $utf8bom = New-Object System.Text.UTF8Encoding $true
  [System.IO.File]::WriteAllText($basicIni, $ini2, $utf8bom)
  $result.backup = $bak
}

# Ensure day folders exist for today
$today = Get-Date -Format 'yyyy-MM-dd'
$dayRoot = Join-Path $DayRootBase $today
foreach ($sub in @('', 'raw', 'candidates', 'markers', 'stills')) {
  $p = if ($sub) { Join-Path $dayRoot $sub } else { $dayRoot }
  if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $p | Out-Null }
}
$result.day_root = $dayRoot
$result.actions += 'ensured_day_tree'

# Patch Untitled scene collection: dual-track mixer routing
# Desktop → track 1 (bit 0 = 1), Mic → track 2 (bit 1 = 2)
if (Test-Path -LiteralPath $untitled) {
  $sceneBak = Join-Path $scenesDir "Untitled.json.bak_$stamp"
  $raw = Get-Content -LiteralPath $untitled -Raw -Encoding utf8
  $j = $raw | ConvertFrom-Json
  if ($j.DesktopAudioDevice1) {
    $j.DesktopAudioDevice1.mixers = 1
    $j.DesktopAudioDevice1.muted = $false
    $j.DesktopAudioDevice1.enabled = $true
    $result.actions += 'desktop_mixers_track1'
  }
  if ($j.AuxAudioDevice1) {
    $j.AuxAudioDevice1.mixers = 2
    $j.AuxAudioDevice1.muted = $false
    $j.AuxAudioDevice1.enabled = $true
    $result.actions += 'mic_mixers_track2'
  }
  # Prefer scene with WOW window capture if present
  $hasWow = $false
  foreach ($s in $j.sources) {
    if ($s.name -eq 'WOW' -or ($s.settings -and $s.settings.window -match 'Wow\.exe')) {
      $hasWow = $true
    }
  }
  $result.has_wow_window_source = $hasWow
  if (-not $DryRun) {
    Copy-Item -LiteralPath $untitled -Destination $sceneBak -Force
    $jsonOut = $j | ConvertTo-Json -Depth 100
    [System.IO.File]::WriteAllText($untitled, $jsonOut, (New-Object System.Text.UTF8Encoding $false))
    # Product-named clone for operators
    Copy-Item -LiteralPath $untitled -Destination $wowScene -Force
    $result.scene_backup = $sceneBak
    $result.product_scene = $wowScene
  }
  $result.actions += 'scene_dual_route'
}

# Verify
$verifyIni = Get-Content -LiteralPath $basicIni -Raw
$result.path_ok = ($verifyIni -match [regex]::Escape($DayRootBase.Replace('\','\\')) -or $verifyIni -match [regex]::Escape($DayRootBase))
$result.rectracks_ok = ($verifyIni -match '(?m)^RecTracks=3')
$result.status = if ($result.path_ok -and $result.rectracks_ok) { 'CONFIGURED' } else { 'PARTIAL' }

if (-not $DryRun) {
  $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8
}
Write-Output "STATUS=$($result.status) receipt=$receipt"
Write-Output ($result | ConvertTo-Json -Compress)
if ($result.status -ne 'CONFIGURED') { exit 1 }
exit 0
