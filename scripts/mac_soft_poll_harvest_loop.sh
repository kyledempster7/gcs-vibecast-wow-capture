#!/usr/bin/env bash
# Mac LaunchAgent: one soft_poll → harvest_if_ready (no nested poll thrash) → health.
# Play-night mode: quiet hours 03:00–19:59 local (Mac clock); active 20:00–02:59.
# Exit always 0 for launchd. No invent. No publish. No catalog rebuild on idle.
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

  # Quiet daytime: no SSH chatter for 1–3 nights/week product
  if [[ "$HOUR" -ge 3 && "$HOUR" -lt 20 ]]; then
    echo "quiet_hours skip (play-night window is 20:00-02:59 local)"
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
