<#
.SYNOPSIS
  Move OBS masters from D:\WoW B-Roll Storage root into <day>\raw\ (today-only).
.DESCRIPTION
  OBS FilePath is the base folder; product SoR is day root. Run after record stop.
  Only files modified on -Day (local date) OR whose name contains the day stamp.
  No invent. No publish. Does not thrash historical masters into today.
#>
[CmdletBinding()]
param(
  [string]$Base = 'D:\WoW B-Roll Storage',
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd')
)

$ErrorActionPreference = 'Stop'
$raw = Join-Path (Join-Path $Base $Day) 'raw'
New-Item -ItemType Directory -Force -Path $raw | Out-Null

$dayStart = [DateTime]::ParseExact($Day, 'yyyy-MM-dd', $null).Date
$dayEnd = $dayStart.AddDays(1)
$stampA = $Day
$stampB = $Day.Replace('-', '')
$stampC = $Day.Replace('-', ' ')

$moved = @()
Get-ChildItem -LiteralPath $Base -File -ErrorAction SilentlyContinue |
  Where-Object {
    $_.Extension -match '\.(mp4|mkv|mov|m4v)$' -and (
      ($_.LastWriteTime -ge $dayStart -and $_.LastWriteTime -lt $dayEnd) -or
      $_.Name.Contains($stampA) -or
      $_.Name.Contains($stampB) -or
      $_.Name.Contains($stampC)
    )
  } |
  ForEach-Object {
    $dest = Join-Path $raw $_.Name
    if (Test-Path -LiteralPath $dest) {
      $dest = Join-Path $raw ($_.BaseName + '_' + (Get-Date -Format 'HHmmss') + $_.Extension)
    }
    Move-Item -LiteralPath $_.FullName -Destination $dest -Force
    $moved += $dest
  }

Write-Output ("MOVED n={0} day={1}" -f $moved.Count, $Day)
$moved | ForEach-Object { Write-Output $_ }
exit 0
