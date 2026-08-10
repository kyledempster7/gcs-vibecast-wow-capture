#!/usr/bin/env bash
# Ensure exactly one watch_ready_harvest_once for DAY. Collapse thrash; start if zero.
# No invent. No publish.
set -uo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY="${1:-$(date +%F)}"
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
mkdir -p "$LOGDIR"
LOCKDIR="$LOGDIR/watch_ready_harvest.lockdir"
PIDFILE="$LOCKDIR/pid"
CLASSIC="$LOGDIR/watch_ready_harvest.lock"
DETAIL="$LOGDIR/watch_ready_harvest.log"
OUT="${2:-}"

report() {
  echo "$1"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $1" >>"$DETAIL"
  [[ -n "${OUT:-}" ]] && echo "$1" >>"$OUT"
}

# Real watches: bash/sh [flags] *watch_ready_harvest_once.sh
list_real() {
  python3 <<'PY'
import re, subprocess
ps = subprocess.check_output(["ps", "-ax", "-o", "pid=,command="], text=True, errors="replace")
pat = re.compile(
    r"^\s*(\d+)\s+((?:/bin/|/usr/bin/)?(?:bash|sh))"
    r"(?:\s+-[a-zA-Z]+)*\s+(\S*watch_ready_harvest_once\.sh)(?:\s|$)"
)
for line in ps.splitlines():
    if "GROK_AGENT" in line or "builtin eval" in line or "zsh -c" in line:
        continue
    m = pat.match(line)
    if m:
        print(m.group(1))
PY
}

pids=()
while read -r p; do
  [[ -n "$p" ]] && pids+=("$p")
done < <(list_real | sort -u)
n=${#pids[@]}

if [[ "$n" -gt 1 ]]; then
  keep=""
  oldest=9999999999
  for pid in "${pids[@]}"; do
    ls=$(ps -p "$pid" -o lstart= 2>/dev/null | sed 's/^ *//')
    ep=$(date -j -f "%a %b %d %T %Y" "$ls" "+%s" 2>/dev/null || echo 9999999999)
    if [[ "$ep" -lt "$oldest" ]]; then oldest=$ep; keep=$pid; fi
  done
  for pid in "${pids[@]}"; do
    if [[ "$pid" != "$keep" ]]; then
      kill "$pid" 2>/dev/null || true
      report "KILLED_THRASH pid=$pid kept=$keep"
    fi
  done
  sleep 1
  rm -rf "$LOCKDIR"
  mkdir "$LOCKDIR"
  echo "$keep" >"$PIDFILE"
  echo "$keep" >"$CLASSIC"
  report "SINGLE_WATCH pid=$keep day=$DAY after_collapse n_was=$n"
  exit 0
fi

if [[ "$n" -eq 1 ]]; then
  only="${pids[0]}"
  rm -rf "$LOCKDIR"
  mkdir "$LOCKDIR"
  echo "$only" >"$PIDFILE"
  echo "$only" >"$CLASSIC"
  report "SINGLE_WATCH pid=$only day=$DAY already_one"
  exit 0
fi

# n==0: clear stale locks and start one
rm -rf "$LOCKDIR"
rm -f "$CLASSIC"
nohup /bin/bash "$SCRIPTS/watch_ready_harvest_once.sh" "$DAY" \
  >>"$LOGDIR/watch_ready_harvest_stdout.log" 2>&1 &
sleep 3
pids=()
while read -r p; do
  [[ -n "$p" ]] && pids+=("$p")
done < <(list_real | sort -u)
if [[ ${#pids[@]} -eq 1 ]]; then
  report "SINGLE_WATCH pid=${pids[0]} day=$DAY started"
  exit 0
fi
# Fallback: trust classic pid file if process still alive
if [[ -f "$CLASSIC" ]]; then
  cpid=$(cat "$CLASSIC" 2>/dev/null || true)
  if [[ -n "$cpid" ]] && kill -0 "$cpid" 2>/dev/null; then
    report "SINGLE_WATCH pid=$cpid day=$DAY started_via_lockfile"
    exit 0
  fi
fi
report "FAILED watch_count=${#pids[@]} after_start"
exit 1
