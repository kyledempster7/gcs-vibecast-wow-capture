<#
.SYNOPSIS
  One-screen preflight for product play night (no invent, no publish).
#>
[CmdletBinding()]
param(
  [string]$Base = 'D:\WoW B-Roll Storage'
)

$ErrorActionPreference = 'Continue'
$scripts = Join-Path $Base '_scripts'
$day = Get-Date -Format 'yyyy-MM-dd'
$dayRoot = Join-Path $Base $day

Write-Host "==== GCS Windows Preflight day=$day ===="
$need = @(
  'Append-StreamDeckMarker.ps1',
  'Export-ShipCandidates.ps1',
  'Move-TodayMastersToDayRoot.ps1',
  'Session-End-Ship.ps1',
  'Configure-WoW-BRoll-OBS.ps1',
  'DECK_OPEN_COMMANDS.txt',
  'DECK_BUTTON_MAP.md',
  'TODAY_SESSION.md'
)
foreach ($n in $need) {
  $p = Join-Path $scripts $n
  $ok = Test-Path -LiteralPath $p
  Write-Host ("  script {0} = {1}" -f $n, $ok)
}

$ini = Join-Path $env:APPDATA 'obs-studio\basic\profiles\WoW_BRoll_1440p60\basic.ini'
if (Test-Path -LiteralPath $ini) {
  Get-Content -LiteralPath $ini | Where-Object { $_ -match '^(FilePath|RecFilePath|RecTracks|Mode)=' } | ForEach-Object { Write-Host ("  OBS {0}" -f $_) }
} else {
  Write-Host '  OBS profile ini MISSING'
}

foreach ($sub in @('', 'raw', 'candidates', 'markers')) {
  $p = if ($sub) { Join-Path $dayRoot $sub } else { $dayRoot }
  New-Item -ItemType Directory -Force -Path $p | Out-Null
}
Write-Host ("  day_root {0}" -f $dayRoot)

$jsonl = Join-Path $dayRoot 'markers\SESSION.jsonl'
if (Test-Path -LiteralPath $jsonl) {
  $lines = Get-Content -LiteralPath $jsonl
  $n = @($lines).Count
  $human = @($lines | Where-Object { $_ -notmatch 'agent_' }).Count
  $agent = $n - $human
  Write-Host ("  SESSION lines={0} humanish={1} agentish={2}" -f $n, $human, $agent)
} else {
  Write-Host '  SESSION empty (good until record_start)'
}

$obs = Get-Process -Name 'obs64', 'obs32', 'obs' -ErrorAction SilentlyContinue
Write-Host ("  OBS_running={0}" -f [bool]$obs)
Write-Host '==== Open TODAY_SESSION.md then play ===='
exit 0
