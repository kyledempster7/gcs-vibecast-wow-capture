# Windows cold boot for agents (Codex/Grok) — no AIOS registry required.
# Usage (on 3900x):
#   powershell -NoProfile -ExecutionPolicy Bypass -File "...\Windows-Agent-Boot.ps1"
$ErrorActionPreference = "Continue"
$vault = "D:\KyleData\KnownFolders\Documents\kyles_corner"
$wow = Join-Path $vault "Games\WoW"
$tracker = Join-Path $wow "wow-roster-tracker"
$index = Join-Path $wow "00-Index"
$map = Join-Path $index "ROLE_PATH_MAP.json"
$hello = Join-Path $index "WINDOWS_HELLO.md"
$conn = Join-Path $index "CONNECTIVITY_BOARD.md"
$log = Join-Path $tracker "output\windows_agent_boot_last.log"

function Stamp($msg) {
  $line = "$(Get-Date -Format o) $msg"
  Write-Output $line
  Add-Content -LiteralPath $log -Value $line -ErrorAction SilentlyContinue
}

"BOOT_START $(Get-Date -Format o)" | Out-File -FilePath $log -Encoding utf8
Stamp "vault=$vault"

$checks = @(
  @{ Name = "vault_root"; Path = $vault },
  @{ Name = "wow_home"; Path = $wow },
  @{ Name = "WINDOWS_HELLO"; Path = $hello },
  @{ Name = "CONNECTIVITY_BOARD"; Path = $conn },
  @{ Name = "ROLE_PATH_MAP"; Path = $map },
  @{ Name = "media_roots"; Path = (Join-Path $index "media_roots.json") },
  @{ Name = "broll_D"; Path = "D:\WoW B-Roll Storage" },
  @{ Name = "tracker"; Path = $tracker }
)

$fail = 0
foreach ($c in $checks) {
  if (Test-Path -LiteralPath $c.Path) {
    Stamp ("OK " + $c.Name + " " + $c.Path)
  } else {
    Stamp ("MISS " + $c.Name + " " + $c.Path)
    $fail++
  }
}

# Wrong-vault trap
$wrong = "D:\KyleData\KnownFolders\Documents\Claudes_Corner\Games\WoW"
if (Test-Path -LiteralPath $wrong) {
  Stamp "WARN Claudes_Corner Games/WoW also exists — do NOT use for this lane; use kyles_corner"
}

if (Test-Path -LiteralPath (Join-Path $tracker "scripts\resolve_wow_door.py")) {
  Set-Location $tracker
  try {
    & python "scripts\resolve_wow_door.py" --role windows_hello
    Stamp "resolve_wow_door exit=$LASTEXITCODE"
    & python "scripts\resolve_wow_door.py" --probe-all
    Stamp "probe_all exit=$LASTEXITCODE"
  } catch {
    Stamp "resolve_err $_"
  }
} else {
  Stamp "MISS resolve_wow_door.py — open WINDOWS_HELLO.md manually"
}

Stamp "NEXT: Read WINDOWS_HELLO end-to-end. If AIOS named-role fails, use ROLE_PATH_MAP.json + this boot. Do not invent Claudes_Corner paths."
Stamp "BOOT_DONE fail_count=$fail"
if ($fail -gt 0) { exit 1 } else { exit 0 }
