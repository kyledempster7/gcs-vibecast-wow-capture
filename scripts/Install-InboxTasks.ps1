# Register SCH-3 capture + SCH-6 memento daily tasks
$ErrorActionPreference = "Stop"
$base = "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\wow-roster-tracker\scripts"

function Ensure-Task {
  param([string]$Name, [string]$Ps1, [string]$At)
  $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Ps1`""
  $trigger = New-ScheduledTaskTrigger -Daily -At $At
  $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
  $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
  if (Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $Name -Confirm:$false
  }
  Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
  Write-Output "REGISTERED $Name at $At"
}

Ensure-Task -Name "WoW Capture Inbox Daily" -Ps1 (Join-Path $base "Run-CaptureInbox.ps1") -At "4:00AM"
Ensure-Task -Name "WoW Memento Inbox Daily" -Ps1 (Join-Path $base "Run-MementoInbox.ps1") -At "4:05AM"
Get-ScheduledTask -TaskName "WoW Capture Inbox Daily","WoW Memento Inbox Daily","WoW CareSix Live Roster Nightly" -ErrorAction SilentlyContinue |
  Format-Table TaskName, State -AutoSize
