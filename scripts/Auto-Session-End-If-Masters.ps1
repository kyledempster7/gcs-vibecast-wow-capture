<#
.SYNOPSIS
  If TODAY masters sit on storage base or day\raw but candidates empty, run Session-End-Ship.
.DESCRIPTION
  No invent. No publish. Ignores historical masters on base (mtime/name not today).
  Exit 0 = exported or already candidates; 1 = no today masters; 2 = fail
#>
[CmdletBinding()]
param(
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd'),
  [string]$Base = 'D:\WoW B-Roll Storage'
)

$ErrorActionPreference = 'Stop'
$scripts = Join-Path $Base '_scripts'
$ship = Join-Path $scripts 'Session-End-Ship.ps1'
$raw = Join-Path (Join-Path $Base $Day) 'raw'
$cand = Join-Path (Join-Path $Base $Day) 'candidates'
$dayStart = [DateTime]::ParseExact($Day, 'yyyy-MM-dd', $null).Date
$dayEnd = $dayStart.AddDays(1)
$stampA = $Day
$stampB = $Day.Replace('-', '')

function Test-IsTodayMaster([System.IO.FileInfo]$f) {
  if ($f.LastWriteTime -ge $dayStart -and $f.LastWriteTime -lt $dayEnd) { return $true }
  if ($f.Name.Contains($stampA) -or $f.Name.Contains($stampB)) { return $true }
  return $false
}

$candN = 0
if (Test-Path -LiteralPath $cand) {
  $candN = @(Get-ChildItem -LiteralPath $cand -Filter '*.mp4' -ErrorAction SilentlyContinue).Count
}
if ($candN -gt 0) {
  Write-Output ("ALREADY_CANDIDATES n={0}" -f $candN)
  exit 0
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

if ($masters.Count -eq 0) {
  Write-Output 'NO_MASTERS - record first (today only)'
  exit 1
}

Write-Output ("FOUND_TODAY_MASTERS n={0} - running Session-End-Ship" -f $masters.Count)
if (-not (Test-Path -LiteralPath $ship)) {
  Write-Error "Missing $ship"
  exit 2
}
& $ship -Day $Day
exit $LASTEXITCODE
