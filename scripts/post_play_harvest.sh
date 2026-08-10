#!/usr/bin/env bash
# VibeCast fence: no Factory writes
# One-shot after a real play/record night (or agent kickstart outside quiet hours).
# soft_poll → harvest_if_ready → health. No invent. No publish.
# NOT the same as post_night_mac.sh (legacy vibe pulse) — this is B-roll harvest spine.
set -uo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY="${1:-$(date +%F)}"
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
RECEIPTS="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/wow"
mkdir -p "$LOGDIR" "$RECEIPTS"
LOG="$LOGDIR/post_play_harvest.log"
python3 "$SCRIPTS/assert_vibecast_write_fence.py" || exit 2

exec > >(tee -a "$LOG") 2>&1

echo "==== post_play_harvest $(date -u +%Y-%m-%dT%H:%M:%SZ) day=$DAY ===="
export HARVEST_FORCE_POLL=1
bash "$SCRIPTS/soft_poll_windows.sh" || echo "soft_poll_rc=$?"
set +e
bash "$SCRIPTS/harvest_if_ready.sh" "$DAY"
HRC=$?
set -e
echo "harvest_if_ready_rc=$HRC"
python3 "$SCRIPTS/gcs_pipeline_health.py" || true
if [[ "$HRC" -eq 0 ]]; then
  echo "POST_PLAY_HARVEST_OK day=$DAY"
elif [[ "$HRC" -eq 1 ]]; then
  echo "POST_PLAY_NOT_READY day=$DAY — export/stage candidates on Windows first"
else
  echo "POST_PLAY_FAIL day=$DAY rc=$HRC"
fi
cat > "${RECEIPTS}/POST_PLAY_HARVEST_LATEST.md" <<EOF
# post_play_harvest
**day:** $DAY
**utc:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**harvest_rc:** $HRC
**log:** $LOG
**law:** no invent FOOTAGE; no publish
EOF
exit "$HRC"
