#!/usr/bin/env bash
# Exactly-once-ish: soft_poll READY → harvest_mac. No invent. No publish.
# Exit: 0 harvested OR already-locked (idempotent), 1 not ready, 2 fail
set -euo pipefail
DAY="${1:-$(date +%F)}"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
RECEIPTS="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/wow"
mkdir -p "$RECEIPTS"
LOCK="${HOME}/Movies/WoW-Broll-Workflow/Returns/returner-daily-${DAY}/.harvest_once"

echo "== harvest_if_ready day=$DAY =="

# Idempotent: already harvested once → success (cron-safe)
if [[ -f "$LOCK" ]]; then
  echo "SKIP already harvested once for $DAY (lock $LOCK) exit=0"
  exit 0
fi

set +e
# Single-day force so multi-day soft_poll default does not mark ready via another day
bash "$SCRIPTS/soft_poll_windows.sh" "$DAY" "$DAY"
POLL_RC=$?
set -e
if [[ "$POLL_RC" -eq 2 ]]; then
  echo "soft_poll transport fail" >&2
  exit 2
fi
if [[ "$POLL_RC" -ne 0 ]]; then
  echo "SKIP not READY (exit=1)"
  cat > "${RECEIPTS}/HARVEST_SKIP_${DAY//-/}.md" <<EOF
# Harvest skip — $DAY
reason: soft_poll not READY
poll_rc: $POLL_RC
EOF
  exit 1
fi

bash "$SCRIPTS/harvest_mac.sh" "$DAY"
mkdir -p "$(dirname "$LOCK")"
date -u +%Y-%m-%dT%H:%M:%SZ > "$LOCK"
echo "HARVEST_OK day=$DAY"
exit 0
