#!/usr/bin/env bash
# Mac LaunchAgent: one soft_poll → harvest_if_ready (no nested poll thrash) → health.
# Quiet: 03:00–11:59 local (dead morning). Active: 12:00–02:59 so afternoon export is seen.
# Exit always 0 for launchd. No invent. No publish. No catalog rebuild on idle.
# ONE soft_poll per tick when active — no triple-poll thrash.
set -uo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/soft_poll_harvest_loop.log"
DAY="$(date +%F)"
HOUR="$(date +%H)"
HOUR=$((10#$HOUR))

{
  echo "==== $(date -u +%Y-%m-%dT%H:%M:%SZ) day=$DAY hour_local=$HOUR ===="

  # Dead morning only — afternoon play/export must still be discovered (2026-08-10 product fix)
  if [[ "$HOUR" -ge 3 && "$HOUR" -lt 12 ]]; then
    echo "quiet_morning skip (active 12:00-02:59 local for export discovery)"
    echo "loop_done quiet"
    exit 0
  fi

  # ONE multi-day soft_poll per tick
  bash "$SCRIPTS/soft_poll_windows.sh" || echo "soft_poll_rc=$?"
  # harvest reads LATEST for today — no second/third poll when not ready
  bash "$SCRIPTS/harvest_if_ready.sh" "$DAY" || echo "harvest_rc=$?"
  python3 "$SCRIPTS/gcs_pipeline_health.py" || echo "health_rc=$?"
  echo "loop_done"
} >>"$LOG" 2>&1
exit 0
