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

# Retention and status refresh run on every admitted launchd tick, including quiet hours.
bash "$SCRIPTS/rotate_gcs_logs.sh" >>"$LOGDIR/log_rotation.log" 2>&1 || true
python3 "$SCRIPTS/vibecast_status.py" >/dev/null 2>&1 || true
python3 "$SCRIPTS/gcs_citadel_status.py" >/dev/null 2>&1 || true

# Command-validated golden owner (Codex P0: do not third-write soft_poll while golden owns cadence)
golden_alive() {
  python3 <<'PY'
import re, subprocess
ps = subprocess.check_output(["ps", "-ax", "-o", "pid=,command="], text=True, errors="replace")
pat = re.compile(
    r"^\s*(\d+)\s+((?:/bin/|/usr/bin/)?(?:bash|sh))"
    r"(?:\s+-[a-zA-Z]+)*\s+(\S*golden_long_run\.sh)(?:\s|$)"
)
for line in ps.splitlines():
    if "GROK_AGENT" in line or "builtin eval" in line:
        continue
    if pat.match(line):
        print(pat.match(line).group(1))
        raise SystemExit(0)
raise SystemExit(1)
PY
}

{
  echo "==== $(date -u +%Y-%m-%dT%H:%M:%SZ) day=$DAY hour_local=$HOUR ===="

  # Dead morning only — afternoon play/export must still be discovered (2026-08-10 product fix)
  # Quiet hours single source: 03:00–11:59 local (not 03–19)
  if [[ "$HOUR" -ge 3 && "$HOUR" -lt 12 ]]; then
    echo "quiet_morning skip (active 12:00-02:59 local for export discovery)"
    echo "loop_done quiet"
    exit 0
  fi

  if gpid=$(golden_alive); then
    echo "defer_to_golden pid=$gpid — LaunchAgent not a third soft_poll/session-end writer"
    echo "loop_done deferred_golden"
    exit 0
  fi

  # Keep exactly one watch_ready_harvest_once (lockdir single-instance)
  if [[ -f "$SCRIPTS/ensure_single_watch.sh" ]]; then
    bash "$SCRIPTS/ensure_single_watch.sh" "$DAY" || echo "ensure_watch_rc=$?"
  fi

  # ONE multi-day soft_poll per tick (only when golden is not the owner)
  bash "$SCRIPTS/soft_poll_windows.sh" || echo "soft_poll_rc=$?"
  # harvest reads LATEST for today — no second/third poll when not ready
  bash "$SCRIPTS/harvest_if_ready.sh" "$DAY" || echo "harvest_rc=$?"
  python3 "$SCRIPTS/gcs_pipeline_health.py" || echo "health_rc=$?"
  if [[ -f "$SCRIPTS/write_waiting_board.py" ]]; then
    python3 "$SCRIPTS/write_waiting_board.py" || true
  fi
  echo "loop_done"
} >>"$LOG" 2>&1
exit 0
