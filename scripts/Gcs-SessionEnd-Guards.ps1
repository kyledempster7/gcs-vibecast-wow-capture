<#
.SYNOPSIS
  Shared guards for Session-End / Auto-Session-End / Move masters (Codex W0).
.DESCRIPTION
  Mutex · OBS-not-growing · stable file size · today master predicate (mtime primary).
  Dot-source from other scripts. No invent. No publish.
#>

function Get-GcsSessionMutexName {
  return 'Global\GCS_VibeCast_SessionEnd_Ship'
}

function Enter-GcsSessionMutex {
  param([int]$TimeoutMs = 500)
  $name = Get-GcsSessionMutexName
  $created = $false
  $mutex = New-Object System.Threading.Mutex($false, $name, [ref]$created)
  $ok = $false
  try {
    $ok = $mutex.WaitOne($TimeoutMs)
  } catch {
    $ok = $false
  }
  if (-not $ok) {
    try { $mutex.Dispose() } catch {}
    return $null
  }
  return $mutex
}

function Exit-GcsSessionMutex {
  param($Mutex)
  if ($null -eq $Mutex) { return }
  try { $Mutex.ReleaseMutex() | Out-Null } catch {}
  try { $Mutex.Dispose() } catch {}
}

function Test-GcsFileStable {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [int]$SettleMs = 1500,
    [int]$Rounds = 2
  )
  if (-not (Test-Path -LiteralPath $Path)) { return $false }
  $prev = -1L
  for ($i = 0; $i -lt $Rounds; $i++) {
    try {
      $len = (Get-Item -LiteralPath $Path).Length
    } catch {
      return $false
    }
    # Exclusive open probe — active OBS write often fails share
    try {
      $fs = [System.IO.File]::Open($Path, 'Open', 'Read', 'None')
      $fs.Close()
    } catch {
      return $false
    }
    if ($prev -ge 0 -and $len -ne $prev) { return $false }
    $prev = $len
    if ($i -lt ($Rounds - 1)) { Start-Sleep -Milliseconds $SettleMs }
  }
  return $true
}

function Test-GcsTodayMasterStrict {
  <#
    mtime within day is sufficient.
    Name stamp alone is NOT enough if mtime is outside the day (Codex gap 34).
  #>
  param(
    [Parameter(Mandatory = $true)][System.IO.FileInfo]$File,
    [Parameter(Mandatory = $true)][datetime]$DayStart,
    [Parameter(Mandatory = $true)][datetime]$DayEnd
  )
  return ($File.LastWriteTime -ge $DayStart -and $File.LastWriteTime -lt $DayEnd)
}

function Test-GcsAnyGrowingMaster {
  param(
    [string[]]$Paths,
    [int]$ProbeMs = 1200
  )
  $sizes = @{}
  foreach ($p in $Paths) {
    if (-not (Test-Path -LiteralPath $p)) { continue }
    try { $sizes[$p] = (Get-Item -LiteralPath $p).Length } catch { return $true }
  }
  Start-Sleep -Milliseconds $ProbeMs
  foreach ($p in $sizes.Keys) {
    try {
      $n = (Get-Item -LiteralPath $p).Length
      if ($n -ne $sizes[$p]) { return $true }
      if (-not (Test-GcsFileStable -Path $p -SettleMs 400 -Rounds 2)) { return $true }
    } catch {
      return $true
    }
  }
  return $false
}
