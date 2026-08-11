#!/usr/bin/env bash
# Poll until today READY then harvest once. Prints only DONE / FAILED / TIMEOUT for monitors.
# No invent. No publish.
# Single-instance: atomic mkdir lock dir (not lock-file alone; not fragile ps matching).
# Soft_poll ownership (Codex P0-1): if golden_long_run is cmd-validated alive, this watch
# only *reads* SOFT_POLL_LATEST (golden/operator owns poll writers). Else one soft_poll/tick.
set -uo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY="${1:-$(date +%F)}"
MAX_MIN="${MAX_MIN:-480}"
SLEEP_SEC="${SLEEP_SEC:-120}"
END=$(( $(date +%s) + MAX_MIN * 60 ))
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
mkdir -p "$LOGDIR"
DETAIL="$LOGDIR/watch_ready_harvest.log"
LOCKDIR="$LOGDIR/watch_ready_harvest.lockdir"
PIDFILE="$LOCKDIR/pid"
SELF_PID=$$
DAYFILE="$LOCKDIR/day"
HBFILE="$LOCKDIR/heartbeat"
LATEST="${HOME}/Movies/WoW-Broll-Workflow/Returns/SOFT_POLL_LATEST.json"

release_lock() {
  rm -f "$PIDFILE" "$DAYFILE" "$HBFILE" 2>/dev/null || true
  rmdir "$LOCKDIR" 2>/dev/null || true
}

write_meta() {
  printf '%s\n' "$SELF_PID" >"$PIDFILE"
  printf '%s\n' "$DAY" >"$DAYFILE"
  date -u +%Y-%m-%dT%H:%M:%SZ >"$HBFILE"
  printf '%s\n' "$SELF_PID" >"$LOGDIR/watch_ready_harvest.lock"
}

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
    m = pat.match(line)
    if m:
        print(m.group(1))
        raise SystemExit(0)
raise SystemExit(1)
PY
}

# If lockdir exists with live pid for same day, refuse. Stale or wrong-day → reclaim.
if ! mkdir "$LOCKDIR" 2>/dev/null; then
  oldpid=""
  oldday=""
  if [[ -f "$PIDFILE" ]]; then
    oldpid=$(cat "$PIDFILE" 2>/dev/null || true)
  fi
  if [[ -f "$DAYFILE" ]]; then
    oldday=$(cat "$DAYFILE" 2>/dev/null || true)
  fi
  if [[ -n "$oldpid" ]] && kill -0 "$oldpid" 2>/dev/null; then
    if ps -p "$oldpid" -o command= 2>/dev/null | grep -q 'watch_ready_harvest_once\.sh'; then
      if [[ -z "$oldday" || "$oldday" == "$DAY" ]]; then
        echo "FAILED"
        echo "watch already running pid=$oldpid day=${oldday:-?} (lockdir)" >>"$DETAIL"
        exit 1
      fi
      echo "FAILED"
      echo "watch other_day pid=$oldpid day=$oldday want=$DAY — use ensure_single_watch" >>"$DETAIL"
      exit 1
    fi
  fi
  rm -f "$PIDFILE" "$DAYFILE" "$HBFILE" 2>/dev/null || true
  rmdir "$LOCKDIR" 2>/dev/null || true
  if ! mkdir "$LOCKDIR" 2>/dev/null; then
    echo "FAILED"
    echo "watch lockdir busy after reclaim" >>"$DETAIL"
    exit 1
  fi
fi
write_meta
trap 'rm -f "$LOGDIR/watch_ready_harvest.lock"; release_lock' EXIT

if [[ "${WATCH_TEST_HOLD_SEC:-0}" -gt 0 ]]; then
  sleep "$WATCH_TEST_HOLD_SEC"
fi

while [[ $(date +%s) -lt $END ]]; do
  {
    echo "---- $(date -u +%Y-%m-%dT%H:%M:%SZ) pid=$SELF_PID day=$DAY ----"
    write_meta
    if gpid=$(golden_alive); then
      echo "soft_poll defer_to_golden pid=$gpid — read LATEST only"
      # Auto-Session-End still safe to try (Windows); golden operator also tries
      bash "$SCRIPTS/windows_auto_session_end.sh" "$DAY" || true
    else
      # One soft_poll per tick when watch owns cadence (was dual thrash)
      bash "$SCRIPTS/soft_poll_windows.sh" || true
      bash "$SCRIPTS/windows_auto_session_end.sh" "$DAY" || true
    fi
    write_meta
  } >>"$DETAIL" 2>&1

  python3 - "$LATEST" "$DAY" <<'PY' >>"$DETAIL" 2>&1
import json, sys
from pathlib import Path
p, day = Path(sys.argv[1]), sys.argv[2]
if not p.is_file():
    sys.exit(1)
d = json.loads(p.read_text(encoding="utf-8"))
for row in d.get("days") or []:
    if row.get("day") == day and row.get("ready"):
        sys.exit(0)
sys.exit(1)
PY
  if [[ $? -eq 0 ]]; then
    bash "$SCRIPTS/post_play_harvest.sh" "$DAY" >>"$DETAIL" 2>&1
    HRC=$?
    if [[ "$HRC" -eq 0 ]]; then
      bash "$SCRIPTS/notify_review_ready.sh" "$DAY" >>"$DETAIL" 2>&1 || true
      echo "DONE"
      exit 0
    fi
    echo "FAILED"
    exit 1
  fi
  sleep "$SLEEP_SEC"
done
echo "TIMEOUT"
exit 2
