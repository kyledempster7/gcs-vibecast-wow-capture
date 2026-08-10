# Chain: Capture inbox + Memento inbox + caption seeds + health (no publish)
$ErrorActionPreference = "Continue"
$tracker = "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\wow-roster-tracker"
$log = Join-Path $tracker "output\nightly_inboxes_last.log"
Set-Location $tracker
function Run-Py($args) {
  $p = Start-Process -FilePath "python" -ArgumentList $args -Wait -PassThru -NoNewWindow `
    -RedirectStandardOutput "$log.out" -RedirectStandardError "$log.err"
  "cmd=$($args -join ' ') exit=$($p.ExitCode) time=$(Get-Date -Format o)" | Out-File -Append $log
}
try {
  & "$tracker\scripts\Run-CaptureInbox.ps1"
  & "$tracker\scripts\Run-MementoInbox.ps1"
  Run-Py @("scripts\scorecard_caption_seed.py")
  Run-Py @("scripts\draft_returner_daily.py", "--note", "nightly chain scaffold")
  Run-Py @("scripts\qa_returner_daily.py")
  # stitch package + local outbox enqueue when Mac-side DI available is separate;
  # Windows-only: keep QA. Mac agents run stitch_returner_package.py after Sync/pull.
  Run-Py @("scripts\wow_engine_health.py")
  "CHAIN_OK time=$(Get-Date -Format o)  note=mac_run_stitch_returner_package_after_pull" | Out-File -Append $log
} catch {
  $_ | Out-File -Append "$log.err"
}
