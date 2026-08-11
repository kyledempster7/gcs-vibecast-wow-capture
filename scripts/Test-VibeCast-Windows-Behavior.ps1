<#
.SYNOPSIS
  Fixture-only Windows behavioral regression for VibeCast configuration paths.
.DESCRIPTION
  Uses a unique temporary directory, never touches real media, and removes the
  fixture before returning its JSON result.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Join-Path $env:TEMP ('gcs-vibecast-windows-test-' + [guid]::NewGuid().ToString('N'))
$checks = [ordered]@{}

try {
  $autoHide = Join-Path $PSScriptRoot 'Configure-VibeCast-AutoHideUI.ps1'
  $autoOut = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $autoHide -SelfTest 2>&1
  $autoRc = $LASTEXITCODE
  $autoBody = ($autoOut -join "`n") | ConvertFrom-Json
  $checks['AUTOHIDE_TRANSFORM_SELFTEST'] = ($autoRc -eq 0 -and $autoBody.status -eq 'PASS')

  $day = Get-Date -Format 'yyyy-MM-dd'
  $scripts = Join-Path $root '_scripts'
  $raw = Join-Path (Join-Path $root $day) 'raw'
  New-Item -ItemType Directory -Force -Path $scripts, $raw | Out-Null
  $sentinel = Join-Path $root 'session-end-called.json'
  $env:GCS_TEST_SESSION_END_SENTINEL = $sentinel
  @'
param([string]$Day)
[ordered]@{ day = $Day; called = $true } | ConvertTo-Json | Set-Content -LiteralPath $env:GCS_TEST_SESSION_END_SENTINEL -Encoding utf8
exit 0
'@ | Set-Content -LiteralPath (Join-Path $scripts 'Session-End-Ship.ps1') -Encoding utf8

  $master = Join-Path $root 'fixture-master.mp4'
  [IO.File]::WriteAllBytes($master, [byte[]](0, 1, 2, 3))
  (Get-Item -LiteralPath $master).LastWriteTime = (Get-Date).Date.AddHours(12)
  $autoSession = Join-Path $PSScriptRoot 'Auto-Session-End-If-Masters.ps1'
  $dispatchOut = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $autoSession -Day $day -Base $root 2>&1
  $dispatchRc = $LASTEXITCODE
  $checks['AUTO_SESSION_END_DISPATCH_ON_TODAY_MASTER'] = (
    $dispatchRc -eq 0 -and
    (Test-Path -LiteralPath $sentinel) -and
    (($dispatchOut -join "`n") -match 'FOUND_TODAY_MASTERS')
  )

  Remove-Item -LiteralPath $master, $sentinel -Force -ErrorAction SilentlyContinue
  $skipOut = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $autoSession -Day $day -Base $root 2>&1
  $skipRc = $LASTEXITCODE
  $checks['AUTO_SESSION_END_SKIP_WITHOUT_MASTER'] = (
    $skipRc -eq 1 -and
    -not (Test-Path -LiteralPath $sentinel) -and
    (($skipOut -join "`n") -match 'NO_MASTERS')
  )

  $ok = -not ($checks.Values -contains $false)
  [ordered]@{
    schema = 'gcs_windows_behavior_regression/v1'
    generated_at_local = (Get-Date).ToString('o')
    status = if ($ok) { 'PASS' } else { 'FAIL' }
    checks = $checks
    fixture_only = $true
    real_media_touched = $false
    may_publish = $false
    provider_effects = $false
  } | ConvertTo-Json -Depth 5
  exit $(if ($ok) { 0 } else { 2 })
} finally {
  Remove-Item Env:\GCS_TEST_SESSION_END_SENTINEL -ErrorAction SilentlyContinue
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
