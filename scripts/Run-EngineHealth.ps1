$tracker = "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\wow-roster-tracker"
$log = Join-Path $tracker "output\engine_health_last.log"
Set-Location $tracker
$p = Start-Process -FilePath "python" -ArgumentList "scripts\wow_engine_health.py" -Wait -PassThru -NoNewWindow `
  -RedirectStandardOutput $log -RedirectStandardError "$log.err"
"exit=$($p.ExitCode) time=$(Get-Date -Format o)" | Out-File -Append $log
