<#
.SYNOPSIS
  Read-only probe: OBS product path + today master counts. No invent. No thrash OBS.
#>
[CmdletBinding()]
param(
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd'),
  [string]$Base = 'D:\WoW B-Roll Storage'
)

$ErrorActionPreference = 'Continue'
$ini = Join-Path $env:APPDATA 'obs-studio\basic\profiles\WoW_BRoll_1440p60\basic.ini'
$out = [ordered]@{
  schema = 'gcs_obs_product_path_probe/v1'
  day = $Day
  host = $env:COMPUTERNAME
  ts_local = (Get-Date).ToString('o')
  obs_ini_exists = (Test-Path -LiteralPath $ini)
  obs_running = [bool](Get-Process -Name 'obs64','obs32','obs' -ErrorAction SilentlyContinue)
  file_path = $null
  rec_file_path = $null
  rec_tracks = $null
  mode = $null
  day_raw_mp4 = 0
  day_cand_mp4 = 0
  base_today_masters = 0
  newest = @()
  law = 'read_only; no invent'
}

if (Test-Path -LiteralPath $ini) {
  Get-Content -LiteralPath $ini | ForEach-Object {
    if ($_ -match '^FilePath=(.*)$') { $out.file_path = $Matches[1] }
    if ($_ -match '^RecFilePath=(.*)$') { $out.rec_file_path = $Matches[1] }
    if ($_ -match '^RecTracks=(.*)$') { $out.rec_tracks = $Matches[1] }
    if ($_ -match '^Mode=(.*)$') { $out.mode = $Matches[1] }
  }
}

$raw = Join-Path (Join-Path $Base $Day) 'raw'
$cand = Join-Path (Join-Path $Base $Day) 'candidates'
if (Test-Path -LiteralPath $raw) {
  $out.day_raw_mp4 = @(Get-ChildItem -LiteralPath $raw -Filter '*.mp4' -ErrorAction SilentlyContinue).Count
}
if (Test-Path -LiteralPath $cand) {
  $out.day_cand_mp4 = @(Get-ChildItem -LiteralPath $cand -Filter '*.mp4' -ErrorAction SilentlyContinue).Count
}

$dayStart = [DateTime]::ParseExact($Day, 'yyyy-MM-dd', $null).Date
$dayEnd = $dayStart.AddDays(1)
if (Test-Path -LiteralPath $Base) {
  $out.base_today_masters = @(
    Get-ChildItem -LiteralPath $Base -File -ErrorAction SilentlyContinue |
      Where-Object {
        $_.Extension -match '\.(mp4|mkv|mov)$' -and
        $_.LastWriteTime -ge $dayStart -and $_.LastWriteTime -lt $dayEnd
      }
  ).Count
  $out.newest = @(
    Get-ChildItem -LiteralPath $Base -Recurse -File -ErrorAction SilentlyContinue |
      Where-Object { $_.Extension -match '\.(mp4|mkv|mov)$' } |
      Sort-Object LastWriteTime -Descending |
      Select-Object -First 6 |
      ForEach-Object { '{0:o}|{1}' -f $_.LastWriteTime, $_.FullName }
  )
}

function Normalize-PathLike([string]$p) {
  if ([string]::IsNullOrWhiteSpace($p)) { return '' }
  $n = $p.Trim().Trim('"')
  # collapse doubled backslashes from ini/json noise
  while ($n.Contains('\\')) { $n = $n.Replace('\\', '\') }
  return $n
}
$fp = Normalize-PathLike ([string]$out.file_path)
$rp = Normalize-PathLike ([string]$out.rec_file_path)
$baseN = Normalize-PathLike $Base
$out.file_path_norm = $fp
$out.rec_file_path_norm = $rp
$pathOk = ($fp.Equals($baseN, [StringComparison]::OrdinalIgnoreCase)) -or
  ($fp.StartsWith($baseN + '\', [StringComparison]::OrdinalIgnoreCase)) -or
  ($rp.Equals($baseN, [StringComparison]::OrdinalIgnoreCase)) -or
  ($rp.StartsWith($baseN + '\', [StringComparison]::OrdinalIgnoreCase))
$out.product_path_ok = [bool]$pathOk
# ready_to_record = profile+path OK (does not require masters already present)
$out.ready_to_record = [bool]($out.obs_ini_exists -and $pathOk)
$out.has_today_masters = [bool](($out.day_raw_mp4 -gt 0) -or ($out.day_cand_mp4 -gt 0) -or ($out.base_today_masters -gt 0))

$json = $out | ConvertTo-Json -Depth 5
Write-Output $json
$receiptDir = Join-Path $Base '_receipts'
New-Item -ItemType Directory -Force -Path $receiptDir | Out-Null
$receipt = Join-Path $receiptDir ("OBS_PATH_PROBE_{0}.json" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))
Set-Content -LiteralPath $receipt -Value $json -Encoding utf8
Write-Output ("RECEIPT={0}" -f $receipt)
# Exit: 0 profile ready (path OK); 1 profile/path bad; 2 has today masters (optional signal for scripts)
if (-not $out.ready_to_record) { exit 1 }
if ($out.has_today_masters) { exit 2 }
exit 0
