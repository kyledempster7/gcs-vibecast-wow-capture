#!/usr/bin/env bash
# Dual-SoT deploy: Mac vault scripts → Windows D:\WoW B-Roll Storage\_scripts
# No invent. No publish. Idempotent scp.
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
HOST="${WINDOWS_SSH_HOST:-$(python3 "$SCRIPTS/resolve_windows_host.py" --ssh)}"
REMOTE="D:/WoW B-Roll Storage/_scripts"
RECEIPTS="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/wow"
mkdir -p "$RECEIPTS"

FILES=(
  Append-StreamDeckMarker.ps1
  Export-ShipCandidates.ps1
  Stage-ShipCandidates.ps1
  soft_poll_windows.ps1
  Install-InboxTasks.ps1
  Install-RemainingTasks.ps1
  Install-GCS-ShipTasks.ps1
  Install-LayerC-DeckMarkers.ps1
  Configure-WoW-BRoll-OBS.ps1
  Move-TodayMastersToDayRoot.ps1
  Session-End-Ship.ps1
  Auto-Session-End-If-Masters.ps1
  Gcs-SessionEnd-Guards.ps1
  Windows-Preflight.ps1
  Windows-Resume-Readiness.ps1
  Run-NightlyInboxes.ps1
  Run-CaptureInbox.ps1
  Run-MementoInbox.ps1
  Run-EngineHealth.ps1
  check_disk_headroom.ps1
  Windows-Agent-Boot.ps1
  Configure-VibeCast-AutoHideUI.ps1
  Test-VibeCast-Windows-Behavior.ps1
  DECK_OPEN_COMMANDS.txt
)

echo "== deploy_windows_scripts host=$HOST =="
ssh -o BatchMode=yes -o ConnectTimeout=20 "$HOST" \
  "powershell -NoProfile -Command \"New-Item -ItemType Directory -Force -Path 'D:\\WoW B-Roll Storage\\_scripts' | Out-Null\"" \
  || { echo "SSH fail"; exit 2; }

ok=0
miss=0
for f in "${FILES[@]}"; do
  src="$SCRIPTS/$f"
  if [[ ! -f "$src" ]]; then
    echo "SKIP missing local $f"
    miss=$((miss + 1))
    continue
  fi
  if scp -o BatchMode=yes -o ConnectTimeout=30 "$src" "${HOST}:${REMOTE}/"; then
    echo "OK $f"
    ok=$((ok + 1))
  else
    echo "FAIL $f" >&2
    exit 2
  fi
done

# short card files for Deck + today session
for f in DECK_BUTTON_MAP.md DECK_MULTI_ACTION_INSTALL.md; do
  src2="$(cd "$SCRIPTS/../.." && pwd)/04-Story-and-Capture/$f"
  if [[ -f "$src2" ]]; then
    scp -o BatchMode=yes -o ConnectTimeout=20 "$src2" "${HOST}:${REMOTE}/" && echo "OK doc $f" || true
  fi
done
if [[ -f "$SCRIPTS/TODAY_SESSION.md" ]]; then
  scp -o BatchMode=yes -o ConnectTimeout=20 "$SCRIPTS/TODAY_SESSION.md" "${HOST}:${REMOTE}/" && echo "OK doc TODAY_SESSION.md" || true
fi
# UI product tickets for Windows seat (minimap-only gather B-roll)
# Investigation / product tickets for Windows seat (Mac SoT → D:\_scripts)
for f in \
  WINDOWS_SEAT_INVESTIGATION_PACKET.md \
  WINDOWS_FUTURE_GOALS_PACKET.md \
  CAPTURE_LEAGUE_PITCH_TONIGHT.md \
  WINDOWS_TODAY_MARKERS_ONLY_NOTE.md \
  WINDOWS_RESUME_TODAY.md \
  Probe-OBS-ProductPath.ps1 \
  MINIMAP_ONLY_GATHER_BROLL.md \
  GATHERING_BROLL_MODE.md \
  CINEMATIC_ORBIT_UI_MODE.md \
  FIELD_NOTES_SCRIPT_TODAY.md \
  FIELD_NOTES_EXPLORERS_LEAGUE.md \
  AUDACITY_FIELD_NOTES_WINDOWS.md \
  PROFESSION_MESH_GLANCE.md
do
  if [[ -f "$SCRIPTS/$f" ]]; then
    scp -o BatchMode=yes -o ConnectTimeout=20 "$SCRIPTS/$f" "${HOST}:${REMOTE}/" && echo "OK doc $f" || true
  fi
done

ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cat > "${RECEIPTS}/DEPLOY_WINDOWS_SCRIPTS_LATEST.md" <<EOF
# Deploy Windows scripts
**When (UTC):** $ts
**Host:** $HOST
**Remote:** D:\\WoW B-Roll Storage\\_scripts
**ok:** $ok **local_miss:** $miss
**Law:** dual SoT — Mac vault is source; scp after every Windows-facing edit
EOF
echo "DEPLOY_OK ok=$ok miss=$miss"
if [[ "$miss" -ne 0 ]]; then
  echo "DEPLOY_INCOMPLETE missing_local=$miss" >&2
  exit 2
fi
WINDOWS_SSH_HOST="$HOST" python3 "$SCRIPTS/verify_windows_script_hash_parity.py"
exit 0
