# Right-size (2026-08-10 swarm): do NOT schedule Stage-ShipCandidates.
# harvest_mac stages when READY; empty nightly Stage with missing -Day was broken thrash.
# Optional: disk headroom only.
$ErrorActionPreference = "Stop"
$base = "D:\WoW B-Roll Storage\_scripts"

# Unregister broken / redundant ship Stage task if present
$dead = @("GCS Stage Ship Candidates Nightly")
foreach ($n in $dead) {
  if (Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $n -Confirm:$false
    Write-Output "UNREGISTERED $n"
  }
}

$disk = Join-Path $base "check_disk_headroom.ps1"
if (Test-Path $disk) {
  $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$disk`""
  $trigger = New-ScheduledTaskTrigger -Daily -At "9:30AM"
  $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
  $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
  if (Get-ScheduledTask -TaskName "GCS Disk Headroom Daily" -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName "GCS Disk Headroom Daily" -Confirm:$false
  }
  Register-ScheduledTask -TaskName "GCS Disk Headroom Daily" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
  Write-Output "REGISTERED GCS Disk Headroom Daily"
}

Get-ScheduledTask | Where-Object { $_.TaskName -match 'GCS|WoW Nightly|WoW Capture|WoW Memento|WoW Engine' } |
  Select-Object TaskName, State | Format-Table -AutoSize
Write-Output "DONE Install-GCS-ShipTasks (Stage SCH demoted - harvest_mac owns stage)"
