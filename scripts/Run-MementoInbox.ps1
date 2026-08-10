# SCH-6 — list new retail Screenshots (Memento) into vault memento-inbox
$ErrorActionPreference = "Continue"
$tracker = "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\wow-roster-tracker"
$inbox = "C:\Program Files (x86)\World of Warcraft\_retail_\Screenshots"
$vaultOut = "D:\KyleData\KnownFolders\Documents\kyles_corner\Games\WoW\04-Story-and-Capture\memento-inbox"
$log = Join-Path $tracker "output\memento_inbox_last.log"
Set-Location $tracker
try {
  # Direct & python (Start-Process was exit=2 with empty/stale lists)
  $out = & python "scripts\list_memento_inbox.py" `
    --inbox $inbox `
    --vault-out $vaultOut `
    --host "windows-3900x" `
    --max-files 40 2>&1
  $code = $LASTEXITCODE
  $out | Out-File -FilePath $log -Encoding utf8
  "exit=$code time=$(Get-Date -Format o)" | Out-File -Append $log -Encoding utf8
} catch {
  $_ | Out-File -Append "$log.err" -Encoding utf8
}
