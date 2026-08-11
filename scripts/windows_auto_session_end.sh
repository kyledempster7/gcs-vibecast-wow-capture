#!/usr/bin/env bash
# Mac → Windows: if masters exist and candidates empty, run Session-End-Ship.
# No invent. Exit 0 ok/exported, 1 nothing to do, 2 fail.
set -uo pipefail
DAY="${1:-$(date +%F)}"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
HOST="${WINDOWS_SSH_HOST:-$(python3 "$SCRIPTS/resolve_windows_host.py" --ssh)}"

# Ensure resident script
scp -o BatchMode=yes -o ConnectTimeout=15 \
  "$SCRIPTS/Auto-Session-End-If-Masters.ps1" \
  "$SCRIPTS/Session-End-Ship.ps1" \
  "$SCRIPTS/Move-TodayMastersToDayRoot.ps1" \
  "$SCRIPTS/Export-ShipCandidates.ps1" \
  "${HOST}:D:/WoW B-Roll Storage/_scripts/" >/dev/null 2>&1 || true

set +e
OUT=$(ssh -o BatchMode=yes -o ConnectTimeout=45 "$HOST" \
  "powershell -NoProfile -ExecutionPolicy Bypass -File \"D:\\WoW B-Roll Storage\\_scripts\\Auto-Session-End-If-Masters.ps1\" -Day $DAY" 2>&1)
RC=$?
set -e
printf '%s\n' "$OUT"
if echo "$OUT" | grep -q 'NO_MASTERS'; then
  exit 1
fi
if echo "$OUT" | grep -qE 'SESSION_END_DONE|ALREADY_CANDIDATES'; then
  exit 0
fi
exit "$RC"
