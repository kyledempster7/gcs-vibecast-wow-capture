# SCH-3 — list B-roll files into vault capture-inbox (paths only)
# Prefer D: storage (trusted). C:\Users\...\Videos can hit WinError 448 untrusted mount.
$ErrorActionPreference = "Continue"
$tracker = "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\wow-roster-tracker"
$candidates = @(
  "D:\WoW B-Roll Storage",
  "D:\Codex Review Queue\B-Roll Candidates",
  "C:\Users\kyled\Videos\WoW B-Roll"
)
$inbox = $null
foreach ($c in $candidates) {
  try {
    if (Test-Path -LiteralPath $c) { $inbox = $c; break }
  } catch { }
}
if (-not $inbox) { $inbox = "D:\WoW B-Roll Storage" }
$vaultOut = "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\04-Story-and-Capture\capture-inbox"
$log = Join-Path $tracker "output\capture_inbox_last.log"
Set-Location $tracker
try {
  if (-not (Test-Path -LiteralPath $inbox)) {
    New-Item -ItemType Directory -Path $inbox -Force | Out-Null
  }
} catch { }
try {
  # Direct & python (Start-Process was exit=2 with empty/stale lists)
  $out = & python "scripts\list_capture_inbox.py" `
    --inbox $inbox `
    --vault-out $vaultOut `
    --host "windows-3900x" `
    --max-files 80 2>&1
  $code = $LASTEXITCODE
  $out | Out-File -FilePath $log -Encoding utf8
  "exit=$code inbox=$inbox time=$(Get-Date -Format o)" | Out-File -Append $log -Encoding utf8
} catch {
  $_ | Out-File -Append "$log.err" -Encoding utf8
}
