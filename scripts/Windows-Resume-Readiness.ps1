<#
.SYNOPSIS
  Read-only Windows resume truth for the GCS VibeCast WoW capture seat.
#>
[CmdletBinding()]
param(
  [string]$Base = 'D:\WoW B-Roll Storage'
)

$ErrorActionPreference = 'SilentlyContinue'
$day = Get-Date -Format 'yyyy-MM-dd'
$scripts = Join-Path $Base '_scripts'
$dayRoot = Join-Path $Base $day
$profileRoot = Join-Path $env:APPDATA 'obs-studio\basic\profiles\WoW_BRoll_1440p60'
$profileIni = Join-Path $profileRoot 'basic.ini'

$settings = [ordered]@{}
if (Test-Path -LiteralPath $profileIni) {
  foreach ($line in Get-Content -LiteralPath $profileIni) {
    if ($line -match '^(FilePath|RecFilePath|RecTracks|Mode)=(.*)$') {
      $settings[$matches[1]] = $matches[2]
    }
  }
}

$addonRoots = @(
  'C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns',
  'C:\Program Files\World of Warcraft\_retail_\Interface\AddOns'
)
$autoHide = @()
foreach ($root in $addonRoots) {
  if (Test-Path -LiteralPath $root) {
    $autoHide += @(
      Get-ChildItem -LiteralPath $root -Directory |
        Where-Object { $_.Name -match '(?i)auto.*hide.*ui|hide.*ui' } |
        Select-Object -ExpandProperty FullName
    )
  }
}

$autoHideSaved = 'C:\Program Files (x86)\World of Warcraft\_retail_\WTF\Account\CERBERUS321\SavedVariables\AutoHideUI.lua'
$autoHideBackup = $autoHideSaved + '.pre-vibecast-20260811.bak'
$autoHideConfigured = $false
$autoHideActiveGather = $false
$autoHideSha = $null
if (Test-Path -LiteralPath $autoHideSaved) {
  $autoHideText = Get-Content -LiteralPath $autoHideSaved -Raw
  $autoHideConfigured = (
    $autoHideText.Contains('["VibeCast Gather"] = {') -and
    $autoHideText.Contains('["VibeCast Cinematic"] = {') -and
    $autoHideText.Contains('["ObjectiveTrackerFrame"] = true') -and
    $autoHideText.Contains('["MinimapCluster"] = false')
  )
  $autoHideActiveGather = $autoHideText.Contains('= "VibeCast Gather"')
  $autoHideSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $autoHideSaved).Hash.ToLowerInvariant()
}

$rawCount = 0
$candidateCount = 0
if (Test-Path -LiteralPath (Join-Path $dayRoot 'raw')) {
  $rawCount = @(
    Get-ChildItem -LiteralPath (Join-Path $dayRoot 'raw') -File -Filter '*.mp4'
  ).Count
}
if (Test-Path -LiteralPath (Join-Path $dayRoot 'candidates')) {
  $candidateCount = @(
    Get-ChildItem -LiteralPath (Join-Path $dayRoot 'candidates') -File -Filter '*.mp4'
  ).Count
}

$obsRunning = [bool](Get-Process -Name 'obs64', 'obs32', 'obs')
$wowRunning = [bool](Get-Process -Name 'Wow', 'WowClassic', 'WowClassicT')
$pathOk = (
  $settings.Contains('FilePath') -and
  (($settings['FilePath'] -replace '\\\\', '\') -eq $Base)
)

$body = [ordered]@{
  schema = 'gcs_windows_resume_readiness/v1'
  generated_at_local = (Get-Date).ToString('o')
  host = $env:COMPUTERNAME
  day = $day
  obs_running = $obsRunning
  wow_running = $wowRunning
  profile = [ordered]@{
    folder = 'WoW_BRoll_1440p60'
    ini_exists = (Test-Path -LiteralPath $profileIni)
    settings = $settings
    product_path_ok = $pathOk
  }
  auto_hide_ui = [ordered]@{
    installed = ($autoHide.Count -gt 0)
    matches = $autoHide
    saved_variables_path = $autoHideSaved
    saved_variables_exists = (Test-Path -LiteralPath $autoHideSaved)
    configured = $autoHideConfigured
    active_profile_is_gather = $autoHideActiveGather
    gather_profile = 'VibeCast Gather'
    cinematic_profile = 'VibeCast Cinematic'
    original_backup_exists = (Test-Path -LiteralPath $autoHideBackup)
    sha256 = $autoHideSha
  }
  today_media = [ordered]@{
    day_root_exists = (Test-Path -LiteralPath $dayRoot)
    raw_mp4 = $rawCount
    candidate_mp4 = $candidateCount
  }
  resume_card = [ordered]@{
    path = (Join-Path $scripts 'WINDOWS_RESUME_TODAY.md')
    exists = (Test-Path -LiteralPath (Join-Path $scripts 'WINDOWS_RESUME_TODAY.md'))
  }
  stream_deck = [ordered]@{
    running = [bool](Get-Process -Name 'StreamDeck' -ErrorAction SilentlyContinue)
    command_sheet_exists = (Test-Path -LiteralPath (Join-Path $scripts 'DECK_OPEN_COMMANDS.txt'))
  }
  may_publish = $false
  mutation = 'none_read_only'
}

$body | ConvertTo-Json -Depth 6
exit 0
