#!/usr/bin/env bash
# Poll until today READY then harvest once. Prints only DONE / FAILED / TIMEOUT for monitors.
# No invent. No publish.
set -uo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY="${1:-$(date +%F)}"
MAX_MIN="${MAX_MIN:-180}"
SLEEP_SEC="${SLEEP_SEC:-120}"
END=$(( $(date +%s) + MAX_MIN * 60 ))
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
mkdir -p "$LOGDIR"
DETAIL="$LOGDIR/watch_ready_harvest.log"
LOCK="$LOGDIR/watch_ready_harvest.lock"
# Single-instance: refuse second watch
if [[ -f "$LOCK" ]]; then
  oldpid=$(cat "$LOCK" 2>/dev/null || true)
  if [[ -n "$oldpid" ]] && kill -0 "$oldpid" 2>/dev/null; then
    echo "FAILED"
    echo "watch already running pid=$oldpid" >>"$DETAIL"
    exit 1
  fi
fi
echo $$ >"$LOCK"
trap 'rm -f "$LOCK"' EXIT

while [[ $(date +%s) -lt $END ]]; do
  {
    echo "---- $(date -u +%Y-%m-%dT%H:%M:%SZ) ----"
    bash "$SCRIPTS/soft_poll_windows.sh" || true
    # If masters landed but Kyle forgot Session-End, do it for him
    bash "$SCRIPTS/windows_auto_session_end.sh" "$DAY" || true
    bash "$SCRIPTS/soft_poll_windows.sh" || true
  } >>"$DETAIL" 2>&1

  python3 - "$HOME/Movies/WoW-Broll-Workflow/Returns/SOFT_POLL_LATEST.json" "$DAY" <<'PY' >>"$DETAIL" 2>&1
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
