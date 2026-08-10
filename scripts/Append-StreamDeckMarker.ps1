<#
.SYNOPSIS
  Append one Stream Deck marker line to SESSION.jsonl (contract v0).
.DESCRIPTION
  Fail-open: creates day markers\ folder if missing.
  No publish. Wire Stream Deck multi-action → this script with -ButtonId.
.EXAMPLE
  .\Append-StreamDeckMarker.ps1 -ButtonId layer_c.broll_enter -Label "Enter b-roll" -State begin
  .\Append-StreamDeckMarker.ps1 -ButtonId layer_c.talk_peak -Label "Talk peak" -State pulse
  .\Append-StreamDeckMarker.ps1 -ButtonId layer_c.gather_ui_on -Label "Gather UI ON" -State begin
  .\Append-StreamDeckMarker.ps1 -ButtonId layer_c.gather_ui_off -Label "Gather UI OFF" -State end
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$ButtonId,
  [string]$Label = '',
  [ValidateSet('begin', 'end', 'pulse')][string]$State = 'pulse',
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd'),
  [string]$ObsOutputPath = '',
  [bool]$Recording = $true,
  [string]$HostName = $env:COMPUTERNAME
)

$ErrorActionPreference = 'Stop'
$dayRoot = "D:\WoW B-Roll Storage\$Day"
$markers = Join-Path $dayRoot 'markers'
New-Item -ItemType Directory -Force -Path $markers | Out-Null
$jsonl = Join-Path $markers 'SESSION.jsonl'

if (-not $Label) {
  $Label = $ButtonId
}

$now = [DateTimeOffset]::UtcNow
$local = [DateTimeOffset]::Now
$sessionId = $Day
# Prefer first record_start line if present
if (Test-Path -LiteralPath $jsonl) {
  $first = Get-Content -LiteralPath $jsonl -TotalCount 5 -ErrorAction SilentlyContinue |
    Where-Object { $_ -match 'record_start' } | Select-Object -First 1
  if ($first) {
    try {
      $o = $first | ConvertFrom-Json
      if ($o.session_id) { $sessionId = [string]$o.session_id }
    } catch {}
  }
}

$row = [ordered]@{
  schema          = 'gcs_obs_marker/v1'
  ts_utc          = $now.ToString('o')
  ts_local        = $local.ToString('o')
  host            = $HostName
  session_id      = $sessionId
  button_id       = $ButtonId
  label           = $Label
  state           = $State
  recording       = $Recording
  source          = 'stream_deck'
}
if ($ObsOutputPath) { $row.obs_output_path = $ObsOutputPath }

$line = ($row | ConvertTo-Json -Compress)
Add-Content -LiteralPath $jsonl -Value $line -Encoding utf8
Write-Output ("APPENDED {0} -> {1}" -f $ButtonId, $jsonl)
Write-Output $line
