# Wire remaining scheduled tasks: nightly inbox chain + weekly health
$ErrorActionPreference = "Stop"
# Prefer D:\_scripts (dual-SoT deploy target); fall back to Documents tree
$base = "D:\WoW B-Roll Storage\_scripts"
if (-not (Test-Path (Join-Path $base "Run-NightlyInboxes.ps1"))) {
  $alt = "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\wow-roster-tracker\scripts"
  if (Test-Path (Join-Path $alt "Run-NightlyInboxes.ps1")) { $base = $alt }
}

function Ensure-Task {
  param([string]$Name, [string]$Ps1, [string]$At, [string]$TriggerType = "Daily")
  $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Ps1`""
  if ($TriggerType -eq "Weekly") {
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $At
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

# Combined chain after CareSix (03:15) and individual 04:00/04:05 — light re-run 12:30 for play-day capture
Ensure-Task -Name "WoW Nightly Inbox Chain" -Ps1 (Join-Path $base "Run-NightlyInboxes.ps1") -At "4:15AM"
Ensure-Task -Name "WoW Engine Health Weekly" -Ps1 (Join-Path $base "Run-EngineHealth.ps1") -At "10:00AM" -TriggerType "Weekly"

Get-ScheduledTask -TaskName "WoW*","Thrall*" -ErrorAction SilentlyContinue |
  Where-Object { $_.TaskName -match "WoW|Thrall" } |
  Format-Table TaskName, State -AutoSize
