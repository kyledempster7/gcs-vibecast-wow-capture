<#
.SYNOPSIS
  Agent-prove full Layer C marker sequence + Stream Deck Open command sheet.
.DESCRIPTION
  source labels use agent_install_prove prefix (not human press).
  Law: no publish · does not close human Deck multi-act night.
#>
[CmdletBinding()]
param(
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd'),
  [string]$ScriptsRoot = 'D:\WoW B-Roll Storage\_scripts'
)

$ErrorActionPreference = 'Stop'
$append = Join-Path $ScriptsRoot 'Append-StreamDeckMarker.ps1'
if (-not (Test-Path -LiteralPath $append)) {
  Write-Error "Missing Append script at $append"
  exit 2
}

$seq = @(
  @{ ButtonId = 'layer_c.record_start'; Label = 'Record start'; State = 'begin' }
  @{ ButtonId = 'layer_c.broll_enter'; Label = 'Enter b-roll'; State = 'begin' }
  @{ ButtonId = 'layer_c.rotate_begin'; Label = 'Begin rotate'; State = 'begin' }
  @{ ButtonId = 'layer_c.rotate_end'; Label = 'End rotate'; State = 'end' }
  @{ ButtonId = 'layer_c.broll_exit'; Label = 'Exit b-roll'; State = 'end' }
  @{ ButtonId = 'layer_c.talk_peak'; Label = 'Talk peak'; State = 'pulse' }
  @{ ButtonId = 'layer_c.gather_ui_on'; Label = 'Gather UI ON'; State = 'begin' }
  @{ ButtonId = 'layer_c.gather_ui_off'; Label = 'Gather UI OFF'; State = 'end' }
  @{ ButtonId = 'layer_c.skip_zone'; Label = 'Skip / bad'; State = 'pulse' }
  @{ ButtonId = 'layer_c.record_mark'; Label = 'Chapter mark'; State = 'pulse' }
)

foreach ($s in $seq) {
  $lab = 'agent_install_prove::' + $s.Label
  & $append -ButtonId $s.ButtonId -Label $lab -State $s.State -Day $Day
  Start-Sleep -Milliseconds 120
}

$dayRoot = Join-Path 'D:\WoW B-Roll Storage' $Day
$jsonl = Join-Path $dayRoot 'markers\SESSION.jsonl'
$lineCount = 0
if (Test-Path -LiteralPath $jsonl) {
  $lineCount = @(Get-Content -LiteralPath $jsonl).Count
}

$sheet = Join-Path $ScriptsRoot 'DECK_OPEN_COMMANDS.txt'
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('# Stream Deck multi-action Open commands - Layer C') | Out-Null
$lines.Add('# Action: System -> Open') | Out-Null
$lines.Add('# Generated: ' + (Get-Date).ToString('o')) | Out-Null
$lines.Add('') | Out-Null
foreach ($s in $seq) {
  $cmd = 'powershell -NoProfile -ExecutionPolicy Bypass -File "' + $append + '" -ButtonId ' + $s.ButtonId + ' -Label "' + $s.Label + '" -State ' + $s.State
  $lines.Add('## ' + $s.ButtonId + ' (' + $s.State + ')') | Out-Null
  $lines.Add($cmd) | Out-Null
  $lines.Add('') | Out-Null
}
Set-Content -LiteralPath $sheet -Value $lines -Encoding utf8

$mapOut = Join-Path $ScriptsRoot 'DECK_BUTTON_MAP.md'
if (Test-Path -LiteralPath $mapOut) {
  $map = Get-Content -LiteralPath $mapOut -Raw
  if ($map -notmatch 'record_start') {
    Add-Content -LiteralPath $mapOut -Value ''
    Add-Content -LiteralPath $mapOut -Value '| layer_c.record_start | Record start | begin | First press of night before or with OBS record |'
  }
}

Write-Output ("PROVE_OK day={0} session_lines={1} sheet={2}" -f $Day, $lineCount, $sheet)
Write-Output ("jsonl={0}" -f $jsonl)
exit 0
