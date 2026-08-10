#!/usr/bin/env bash
# Mac LaunchAgent entry: soft_poll multi-day → harvest_if_ready today → healthboard.
# Exit always 0 for launchd (log failures). No invent. No publish.
set -uo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
RECEIPTS="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/wow"
mkdir -p "$LOGDIR" "$RECEIPTS"
LOG="$LOGDIR/soft_poll_harvest_loop.log"
DAY="$(date +%F)"
{
  echo "==== $(date -u +%Y-%m-%dT%H:%M:%SZ) day=$DAY ===="
  bash "$SCRIPTS/soft_poll_windows.sh" || echo "soft_poll_rc=$?"
  # harvest only today (single-day force inside harvest_if_ready — rewrites LATEST)
  bash "$SCRIPTS/harvest_if_ready.sh" "$DAY" || echo "harvest_rc=$?"
  # restore multi-day LATEST after single-day harvest poll
  bash "$SCRIPTS/soft_poll_windows.sh" || echo "soft_poll_restore_rc=$?"
  python3 "$SCRIPTS/gcs_pipeline_health.py" || echo "health_rc=$?"
  # rebuild catalog if Moments exist (cheap)
  if [[ -f "$SCRIPTS/catalog_query.py" ]]; then
    python3 "$SCRIPTS/catalog_query.py" --rebuild || true
  fi
  echo "loop_done"
} >>"$LOG" 2>&1
exit 0
