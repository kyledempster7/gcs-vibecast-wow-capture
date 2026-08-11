#!/usr/bin/env bash
# Pull path-list markdown from Windows vault after nightly jobs (Mac Sync lag fix)
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
HOST="${WOW_SSH_HOST:-${WINDOWS_SSH_HOST:-$(python3 "$SCRIPTS/resolve_windows_host.py" --ssh)}}"
WIN="D:/KyleData/KnownFolders/Documents/kyles_corner/Games/WoW"
MAC="${WOW_VAULT:-/Users/kyle/Kyles_Vault/kyles_corner}/Games/WoW"

mkdir -p "$MAC/04-Story-and-Capture/capture-inbox" \
         "$MAC/04-Story-and-Capture/memento-inbox" \
         "$MAC/Characters/scorecards" \
         "$MAC/wow-roster-tracker/output"

scp -o BatchMode=yes -o ConnectTimeout=15 \
  "$HOST:$WIN/04-Story-and-Capture/capture-inbox/latest.md" \
  "$HOST:$WIN/04-Story-and-Capture/memento-inbox/latest.md" \
  "$MAC/04-Story-and-Capture/capture-inbox/" 2>/dev/null || true
# memento may need separate dest
scp -o BatchMode=yes -o ConnectTimeout=15 \
  "$HOST:$WIN/04-Story-and-Capture/memento-inbox/latest.md" \
  "$MAC/04-Story-and-Capture/memento-inbox/" 2>/dev/null || true
scp -o BatchMode=yes -o ConnectTimeout=15 \
  "$HOST:$WIN/Characters/scorecards/latest.md" \
  "$MAC/Characters/scorecards/" 2>/dev/null || true
scp -o BatchMode=yes -o ConnectTimeout=15 \
  "$HOST:$WIN/wow-roster-tracker/output/latest.md" \
  "$MAC/wow-roster-tracker/output/" 2>/dev/null || true

echo "pull_windows_lists: done -> $MAC"
