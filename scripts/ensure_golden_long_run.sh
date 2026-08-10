#!/usr/bin/env bash
# Ensure exactly one golden_long_run.sh. Collapse thrash; start if zero.
set -uo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY="${1:-$(date +%F)}"
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
mkdir -p "$LOGDIR"
LOCKDIR="$LOGDIR/golden_long_run.lockdir"
PIDFILE="$LOCKDIR/pid"
LOG="$LOGDIR/golden_long_run.log"

list_real() {
  python3 <<'PY'
import re, subprocess
ps = subprocess.check_output(["ps", "-ax", "-o", "pid=,command="], text=True, errors="replace")
pat = re.compile(
    r"^\s*(\d+)\s+((?:/bin/|/usr/bin/)?(?:bash|sh))"
    r"(?:\s+-[a-zA-Z]+)*\s+(\S*golden_long_run\.sh)(?:\s|$)"
)
for line in ps.splitlines():
    if "ensure_golden" in line:
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
  keep="${pids[0]}"
  for pid in "${pids[@]:1}"; do
    kill "$pid" 2>/dev/null || true
    echo "KILLED_THRASH golden pid=$pid kept=$keep"
  done
  sleep 1
  echo "SINGLE_GOLDEN pid=$keep day=$DAY after_collapse"
  exit 0
fi

if [[ "$n" -eq 1 ]]; then
  only="${pids[0]}"
  mkdir -p "$LOCKDIR" 2>/dev/null || true
  echo "$only" >"$PIDFILE" 2>/dev/null || true
  echo "SINGLE_GOLDEN pid=$only day=$DAY already_one"
  exit 0
fi

export MAX_HOURS="${MAX_HOURS:-10}"
export TICK_SEC="${TICK_SEC:-180}"
export MAX_MIN="${MAX_MIN:-720}"
nohup /bin/bash "$SCRIPTS/golden_long_run.sh" "$DAY" >>"$LOG" 2>&1 &
sleep 2
pids=()
while read -r p; do
  [[ -n "$p" ]] && pids+=("$p")
done < <(list_real | sort -u)
if [[ ${#pids[@]} -eq 1 ]]; then
  echo "SINGLE_GOLDEN pid=${pids[0]} day=$DAY started max_h=$MAX_HOURS"
  exit 0
fi
echo "FAILED golden_count=${#pids[@]} after_start"
exit 1
