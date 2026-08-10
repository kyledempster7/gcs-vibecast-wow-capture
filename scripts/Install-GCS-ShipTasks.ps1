# Schedule ship-side helpers on Windows (Stage + disk headroom).
# Source of truth after deploy: D:\WoW B-Roll Storage\_scripts
# No invent FOOTAGE. Stage only copies when candidates exist.
$ErrorActionPreference = "Stop"
$base = "D:\WoW B-Roll Storage\_scripts"

function Ensure-Task {
  param(
    [string]$Name,
    [string]$Ps1,
    [string]$ExtraArgs,
    [string]$At,
    [string]$TriggerType = "Daily"
  )
  $arg = "-NoProfile -ExecutionPolicy Bypass -File `"$Ps1`""
  if ($ExtraArgs) { $arg = "$arg $ExtraArgs" }
  $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg
  if ($TriggerType -eq "OnceRepeat2h") {
    $trigger = New-ScheduledTaskTrigger -Once -At $At -RepetitionInterval (New-TimeSpan -Hours 2) -RepetitionDuration (New-TimeSpan -Days 365)
  } else {
    $trigger = New-ScheduledTaskTrigger -Daily -At $At
  }
  $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
  $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
  if (Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $Name -Confirm:$false
  }
  Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
  Write-Output "REGISTERED $Name"
}

$stage = Join-Path $base "Stage-ShipCandidates.ps1"
if (-not (Test-Path $stage)) {
  throw "Missing $stage - run deploy_windows_scripts.sh first"
}

# Nightly stage after typical play window
Ensure-Task -Name "GCS Stage Ship Candidates Nightly" -Ps1 $stage -ExtraArgs "" -At "11:30PM"

$disk = Join-Path $base "check_disk_headroom.ps1"
if (Test-Path $disk) {
  Ensure-Task -Name "GCS Disk Headroom Daily" -Ps1 $disk -ExtraArgs "" -At "9:30AM"
}

Get-ScheduledTask | Where-Object { $_.TaskName -match 'GCS|WoW Nightly|WoW Capture|WoW Memento|WoW Engine' } |
  Select-Object TaskName, State | Format-Table -AutoSize
Write-Output "DONE Install-GCS-ShipTasks"
