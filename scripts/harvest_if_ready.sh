#!/usr/bin/env bash
# Exactly-once-ish: READY → harvest_mac. No invent. No publish.
# Exit: 0 harvested OR already-locked, 1 not ready, 2 fail
# Right-size: read SOFT_POLL_LATEST for *today* first — no nested soft_poll when not ready.
# Set HARVEST_FORCE_POLL=1 to always soft_poll before decide.
set -euo pipefail
DAY="${1:-$(date +%F)}"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
RECEIPTS="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/wow"
OUT_DIR="${HOME}/Movies/WoW-Broll-Workflow/Returns"
LATEST="${OUT_DIR}/SOFT_POLL_LATEST.json"
mkdir -p "$RECEIPTS"
LOCK="${OUT_DIR}/returner-daily-${DAY}/.harvest_once"

echo "== harvest_if_ready day=$DAY =="

if [[ -f "$LOCK" ]]; then
  echo "SKIP already harvested once for $DAY (lock $LOCK) exit=0"
  exit 0
fi

today_ready_from_latest() {
  python3 - "$LATEST" "$DAY" <<'PY'
import json, sys
from pathlib import Path
p, day = Path(sys.argv[1]), sys.argv[2]
if not p.is_file():
    sys.exit(3)  # missing
try:
    data = json.loads(p.read_text(encoding="utf-8"))
except Exception:
    sys.exit(3)
for d in data.get("days") or []:
    if d.get("day") == day:
        sys.exit(0 if d.get("ready") else 1)
# no today row
sys.exit(3)
PY
}

set +e
if [[ "${HARVEST_FORCE_POLL:-0}" == "1" ]]; then
  NEED_POLL=1
else
  today_ready_from_latest
  TR=$?
  if [[ "$TR" -eq 1 ]]; then
    echo "SKIP not READY (from SOFT_POLL_LATEST today=$DAY) exit=1"
    cat > "${RECEIPTS}/HARVEST_SKIP_${DAY//-/}.md" <<EOF
# Harvest skip — $DAY
reason: SOFT_POLL_LATEST today not ready (no nested poll)
EOF
    exit 1
  fi
  # TR=0 ready → harvest without extra poll; TR=3 missing → poll once
  if [[ "$TR" -eq 0 ]]; then
    NEED_POLL=0
  else
    NEED_POLL=1
  fi
fi

if [[ "${NEED_POLL}" -eq 1 ]]; then
  # one multi-day poll (honest board); then require *today* ready
  bash "$SCRIPTS/soft_poll_windows.sh"
  POLL_RC=$?
  if [[ "$POLL_RC" -eq 2 ]]; then
    echo "soft_poll transport fail" >&2
    exit 2
  fi
  today_ready_from_latest
  TR=$?
  if [[ "$TR" -ne 0 ]]; then
    echo "SKIP not READY after poll (exit=1)"
    cat > "${RECEIPTS}/HARVEST_SKIP_${DAY//-/}.md" <<EOF
# Harvest skip — $DAY
reason: soft_poll today not READY
poll_rc: $POLL_RC
today_row_rc: $TR
EOF
    exit 1
  fi
fi
set -e

bash "$SCRIPTS/harvest_mac.sh" "$DAY"
mkdir -p "$(dirname "$LOCK")"
date -u +%Y-%m-%dT%H:%M:%SZ > "$LOCK"
# post-harvest catalog only (not idle loop)
if [[ -f "$SCRIPTS/catalog_query.py" ]]; then
  python3 "$SCRIPTS/catalog_query.py" --rebuild || true
fi
echo "HARVEST_OK day=$DAY"
exit 0
