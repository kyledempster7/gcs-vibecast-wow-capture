<#
.SYNOPSIS
  Stage day candidates + MANIFEST to short temp path for scp (Windows).
.EXAMPLE
  .\Stage-ShipCandidates.ps1
  .\Stage-ShipCandidates.ps1 -Day 2026-08-09
#>
param(
  [Parameter(Mandatory = $false)][string]$Day = (Get-Date -Format 'yyyy-MM-dd')
)
$ErrorActionPreference = 'Continue'
$src = "D:\WoW B-Roll Storage\$Day\candidates"
$man = "D:\WoW B-Roll Storage\$Day\MANIFEST.json"
$markers = "D:\WoW B-Roll Storage\$Day\markers"
$dst = "C:\Users\kyled\AppData\Local\Temp\gcs_cand_$Day"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
if (Test-Path -LiteralPath $src) {
  Copy-Item -Path (Join-Path $src '*') -Destination $dst -Force -ErrorAction SilentlyContinue
}
if (Test-Path -LiteralPath $man) {
  Copy-Item -LiteralPath $man -Destination (Join-Path $dst 'MANIFEST.json') -Force
}
# markers optional
$mDst = Join-Path $dst 'markers'
if (Test-Path -LiteralPath $markers) {
  New-Item -ItemType Directory -Force -Path $mDst | Out-Null
  Copy-Item -Path (Join-Path $markers '*') -Destination $mDst -Force -ErrorAction SilentlyContinue
}
Write-Output ("STAGE day={0} -> {1}" -f $Day, $dst)
Get-ChildItem -LiteralPath $dst -File -ErrorAction SilentlyContinue |
  ForEach-Object { Write-Output ("  {0} {1}" -f $_.Length, $_.Name) }
if (Test-Path -LiteralPath $mDst) {
  Get-ChildItem -LiteralPath $mDst -File -ErrorAction SilentlyContinue |
    ForEach-Object { Write-Output ("  markers/{0} {1}" -f $_.Name, $_.Length) }
}
