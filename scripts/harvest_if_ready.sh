#!/usr/bin/env bash
# READY → harvest_mac. Lock means claimed, not "never pull again".
# If windows_cand_n > mac_mp4_n, harvest again even when .harvest_once exists.
# Exit: 0 harvested OR already-complete, 1 not ready, 2 fail, 3 claim held by other
# Codex P0-3: atomic harvest CLAIM before any analysis / soft-fail work.
# Set HARVEST_FORCE_POLL=1 to always soft_poll before decide (after claim).
set -euo pipefail
DAY="${1:-$(date +%F)}"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
RECEIPTS="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/wow"
OUT_DIR="${HOME}/Movies/WoW-Broll-Workflow/Returns"
DAY_DIR="${OUT_DIR}/returner-daily-${DAY}"
LATEST="${OUT_DIR}/SOFT_POLL_LATEST.json"
mkdir -p "$RECEIPTS" "$DAY_DIR"
LOCK="${DAY_DIR}/.harvest_once"
CLAIMDIR="${DAY_DIR}/.harvest_claim.lockdir"
CLAIMPID="${CLAIMDIR}/pid"
CLAIMHB="${CLAIMDIR}/heartbeat"
SELF=$$

python3 "$SCRIPTS/assert_vibecast_write_fence.py" || exit 2

echo "== harvest_if_ready day=$DAY =="

release_claim() {
  rm -f "$CLAIMPID" "$CLAIMHB" 2>/dev/null || true
  rmdir "$CLAIMDIR" 2>/dev/null || true
}

# --- Atomic claim BEFORE ready checks / analysis (Codex gap 27/50) ---
if ! mkdir "$CLAIMDIR" 2>/dev/null; then
  opid=""
  [[ -f "$CLAIMPID" ]] && opid=$(cat "$CLAIMPID" 2>/dev/null || true)
  # Live pid in claim = held (only harvest writers create this dir). Dead pid = stale reclaim.
  if [[ -n "$opid" ]] && kill -0 "$opid" 2>/dev/null; then
    echo "SKIP harvest claim held by pid=$opid exit=3"
    exit 3
  fi
  # stale claim
  release_claim
  if ! mkdir "$CLAIMDIR" 2>/dev/null; then
    echo "FAIL claimdir busy exit=2" >&2
    exit 2
  fi
fi
printf '%s\n' "$SELF" >"$CLAIMPID"
date -u +%Y-%m-%dT%H:%M:%SZ >"$CLAIMHB"
trap 'release_claim' EXIT

# Lock + completeness: skip only when Mac already has >= Windows qualified count.
if [[ -f "$LOCK" ]]; then
  set +e
  python3 "$SCRIPTS/harvest_completeness.py" --day "$DAY"
  COMP_RC=$?
  set -e
  if [[ "$COMP_RC" -eq 0 ]]; then
    echo "SKIP already complete for $DAY (lock $LOCK) exit=0"
    python3 "$SCRIPTS/harvest_completeness.py" --day "$DAY" --write-live --quiet || true
    exit 0
  fi
  echo "INCOMPLETE after lock — re-harvest mac_n<win_n day=$DAY"
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
reason: SOFT_POLL_LATEST today not ready (claim held then released)
claim: pre-analysis
EOF
    exit 1
  fi
  if [[ "$TR" -eq 0 ]]; then
    NEED_POLL=0
  else
    NEED_POLL=1
  fi
fi

if [[ "${NEED_POLL}" -eq 1 ]]; then
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
claim: pre-analysis
EOF
    exit 1
  fi
fi
set -e

# Still claimed — run harvest
date -u +%Y-%m-%dT%H:%M:%SZ >"$CLAIMHB"
bash "$SCRIPTS/harvest_mac.sh" "$DAY"
date -u +%Y-%m-%dT%H:%M:%SZ > "$LOCK"
# post-harvest catalog only (not idle loop)
if [[ -f "$SCRIPTS/catalog_query.py" ]]; then
  python3 "$SCRIPTS/catalog_query.py" --rebuild || true
fi
python3 "$SCRIPTS/harvest_completeness.py" --day "$DAY" --write-live || true
echo "HARVEST_OK day=$DAY"
if [[ -f "$SCRIPTS/notify_review_ready.sh" ]]; then
  bash "$SCRIPTS/notify_review_ready.sh" "$DAY" || true
fi
exit 0
