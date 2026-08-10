<#
.SYNOPSIS
  Move OBS masters from D:\WoW B-Roll Storage root into <day>\raw\ (today-only).
.DESCRIPTION
  OBS FilePath is the base folder; product SoR is day root. Run after record stop.
  Only files with LastWriteTime on -Day (strict). Stable size required before move.
  No invent. No publish. Does not thrash historical masters into today.
#>
[CmdletBinding()]
param(
  [string]$Base = 'D:\WoW B-Roll Storage',
  [string]$Day = (Get-Date -Format 'yyyy-MM-dd'),
  [switch]$SkipStableCheck
)

$ErrorActionPreference = 'Stop'
$scripts = Join-Path $Base '_scripts'
$guards = Join-Path $scripts 'Gcs-SessionEnd-Guards.ps1'
if (Test-Path -LiteralPath $guards) {
  . $guards
} else {
  # Mac-side path during authoring (deploy later)
  $local = Join-Path $PSScriptRoot 'Gcs-SessionEnd-Guards.ps1'
  if (Test-Path -LiteralPath $local) { . $local }
}

$raw = Join-Path (Join-Path $Base $Day) 'raw'
New-Item -ItemType Directory -Force -Path $raw | Out-Null

$dayStart = [DateTime]::ParseExact($Day, 'yyyy-MM-dd', $null).Date
$dayEnd = $dayStart.AddDays(1)

$moved = @()
$skipped = @()
Get-ChildItem -LiteralPath $Base -File -ErrorAction SilentlyContinue |
  Where-Object {
    if ($_.Extension -notmatch '\.(mp4|mkv|mov|m4v)$') { return $false }
    if (Get-Command Test-GcsTodayMasterStrict -ErrorAction SilentlyContinue) {
      return (Test-GcsTodayMasterStrict -File $_ -DayStart $dayStart -DayEnd $dayEnd)
    }
    return ($_.LastWriteTime -ge $dayStart -and $_.LastWriteTime -lt $dayEnd)
  } |
  ForEach-Object {
    if (-not $SkipStableCheck) {
      if (Get-Command Test-GcsFileStable -ErrorAction SilentlyContinue) {
        if (-not (Test-GcsFileStable -Path $_.FullName)) {
          $skipped += ("UNSTABLE_OR_LOCKED {0}" -f $_.FullName)
          return
        }
      }
    }
    $dest = Join-Path $raw $_.Name
    if (Test-Path -LiteralPath $dest) {
      $dest = Join-Path $raw ($_.BaseName + '_' + (Get-Date -Format 'HHmmss') + $_.Extension)
    }
    Move-Item -LiteralPath $_.FullName -Destination $dest -Force
    $moved += $dest
  }

Write-Output ("MOVED n={0} day={1}" -f $moved.Count, $Day)
$moved | ForEach-Object { Write-Output $_ }
if ($skipped.Count -gt 0) {
  Write-Output ("SKIPPED_UNSTABLE n={0}" -f $skipped.Count)
  $skipped | ForEach-Object { Write-Output $_ }
}
exit 0
