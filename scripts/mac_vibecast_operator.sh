#!/usr/bin/env bash
# Mac operator pulse: fence → soft_poll → harvest if today READY → health → optional backup.
# No invent FOOTAGE. No publish. Safe while Windows play is in the void.
set -uo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY="${1:-$(date +%F)}"
RECEIPTS="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/wow"
OUT="${HOME}/Movies/WoW-Broll-Workflow/Returns"
mkdir -p "$RECEIPTS"

python3 "$SCRIPTS/assert_vibecast_write_fence.py" || exit 2

echo "==== mac_vibecast_operator day=$DAY $(date -u +%Y-%m-%dT%H:%M:%SZ) ===="
bash "$SCRIPTS/soft_poll_windows.sh"
POLL=$?

python3 - "$OUT/SOFT_POLL_LATEST.json" "$DAY" <<'PY'
import json, sys
from pathlib import Path
p, day = Path(sys.argv[1]), sys.argv[2]
ready = False
if p.is_file():
    d = json.loads(p.read_text(encoding="utf-8"))
    print("ready_today=", d.get("ready_today"), "ready_any=", d.get("ready_any"))
    for row in d.get("days") or []:
        print(" ", row.get("day"), "ready=", row.get("ready"), row.get("reason"),
              "cand=", row.get("candidates_n"), "raw=", row.get("raw_mp4_n"))
        if row.get("day") == day:
            ready = bool(row.get("ready"))
sys.exit(0 if ready else 1)
PY
TODAY_READY=$?

HRC=1
if [[ "$TODAY_READY" -eq 0 ]]; then
  export HARVEST_FORCE_POLL=0
  bash "$SCRIPTS/harvest_if_ready.sh" "$DAY"
  HRC=$?
  if [[ "$HRC" -eq 0 ]]; then
    bash "$SCRIPTS/notify_review_ready.sh" "$DAY" || true
    echo "OPERATOR: harvest ok — open_review_pack.sh $DAY"
  fi
else
  echo "OPERATOR: waiting Windows export (Session-End-Ship) — no invent"
  HRC=1
fi

python3 "$SCRIPTS/gcs_pipeline_health.py" || true

# Always refresh offsite lightly when asked via BACKUP=1
if [[ "${BACKUP:-0}" == "1" ]]; then
  bash "$SCRIPTS/mac_backup_vibecast.sh" || true
fi

cat > "${RECEIPTS}/MAC_OPERATOR_LATEST.md" <<EOF
# Mac VibeCast operator
**day:** $DAY
**utc:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**soft_poll_rc:** $POLL
**today_ready:** $([[ $TODAY_READY -eq 0 ]] && echo true || echo false)
**harvest_rc:** $HRC
**review:** open_review_pack.sh $DAY
**law:** no invent; fence; arm deny
EOF

if [[ "$TODAY_READY" -eq 0 && "$HRC" -eq 0 ]]; then
  exit 0
fi
exit 1
