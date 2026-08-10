#!/usr/bin/env bash
# Ensure exactly one watch_ready_harvest_once for DAY.
# Lock binds day (Codex P0-2). Reclaim without blind wipe of live holder.
# No invent. No publish.
set -uo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY="${1:-$(date +%F)}"
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
mkdir -p "$LOGDIR"
LOCKDIR="$LOGDIR/watch_ready_harvest.lockdir"
PIDFILE="$LOCKDIR/pid"
DAYFILE="$LOCKDIR/day"
CLASSIC="$LOGDIR/watch_ready_harvest.lock"
DETAIL="$LOGDIR/watch_ready_harvest.log"
OUT="${2:-}"

report() {
  echo "$1"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $1" >>"$DETAIL"
  [[ -n "${OUT:-}" ]] && echo "$1" >>"$OUT"
}

write_holder() {
  local pid="$1"
  local day="$2"
  mkdir -p "$LOCKDIR"
  # Atomic-ish: write temps then replace (do not rm -rf live lock first)
  printf '%s\n' "$pid" >"${PIDFILE}.tmp"
  printf '%s\n' "$day" >"${DAYFILE}.tmp"
  mv -f "${PIDFILE}.tmp" "$PIDFILE"
  mv -f "${DAYFILE}.tmp" "$DAYFILE"
  printf '%s\n' "$pid" >"$CLASSIC"
  # heartbeat for board TTL
  date -u +%Y-%m-%dT%H:%M:%SZ >"$LOCKDIR/heartbeat"
}

cmd_is_watch() {
  local pid="$1"
  ps -p "$pid" -o command= 2>/dev/null | grep -q 'watch_ready_harvest_once\.sh'
}

# Parse day arg from a watch process command line (last token if looks like YYYY-MM-DD)
watch_day_of_pid() {
  local pid="$1"
  python3 - "$pid" <<'PY'
import re, subprocess, sys
pid = sys.argv[1]
try:
    cmd = subprocess.check_output(["ps", "-p", pid, "-o", "command="], text=True, errors="replace").strip()
except Exception:
    print("")
    raise SystemExit(0)
# .../watch_ready_harvest_once.sh [DAY]
m = re.search(r"watch_ready_harvest_once\.sh(?:\s+(\d{4}-\d{2}-\d{2}))?", cmd)
if not m:
    print("")
elif m.group(1):
    print(m.group(1))
else:
    print("")  # unknown → treat as mismatch vs requested day
PY
}

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
  # Prefer a watch already bound to requested DAY
  for pid in "${pids[@]}"; do
    wday=$(watch_day_of_pid "$pid")
    if [[ "$wday" == "$DAY" ]]; then
      ls=$(ps -p "$pid" -o lstart= 2>/dev/null | sed 's/^ *//')
      ep=$(date -j -f "%a %b %d %T %Y" "$ls" "+%s" 2>/dev/null || echo 9999999999)
      if [[ "$ep" -lt "$oldest" ]]; then oldest=$ep; keep=$pid; fi
    fi
  done
  if [[ -z "$keep" ]]; then
    oldest=9999999999
    for pid in "${pids[@]}"; do
      ls=$(ps -p "$pid" -o lstart= 2>/dev/null | sed 's/^ *//')
      ep=$(date -j -f "%a %b %d %T %Y" "$ls" "+%s" 2>/dev/null || echo 9999999999)
      if [[ "$ep" -lt "$oldest" ]]; then oldest=$ep; keep=$pid; fi
    done
  fi
  for pid in "${pids[@]}"; do
    if [[ "$pid" != "$keep" ]]; then
      kill "$pid" 2>/dev/null || true
      report "KILLED_THRASH pid=$pid kept=$keep"
    fi
  done
  sleep 1
  keep_day=$(watch_day_of_pid "$keep")
  if [[ -n "$keep_day" && "$keep_day" != "$DAY" ]]; then
    # Holder is wrong day after collapse — restart for requested DAY
    kill "$keep" 2>/dev/null || true
    sleep 1
    report "RESTART_DAY_MISMATCH old_pid=$keep old_day=$keep_day want=$DAY"
    n=0
    pids=()
  else
    write_holder "$keep" "${keep_day:-$DAY}"
    report "SINGLE_WATCH pid=$keep day=${keep_day:-$DAY} after_collapse n_was=$n"
    exit 0
  fi
fi

if [[ "$n" -eq 1 ]]; then
  only="${pids[0]}"
  wday=$(watch_day_of_pid "$only")
  if [[ -n "$wday" && "$wday" != "$DAY" ]]; then
    report "DAY_MISMATCH pid=$only running_day=$wday want=$DAY — restart"
    kill "$only" 2>/dev/null || true
    sleep 1
    n=0
  elif ! cmd_is_watch "$only"; then
    report "CMD_MISMATCH pid=$only — restart"
    n=0
  else
    # Reclaim lock metadata without destroying live holder first
    write_holder "$only" "${wday:-$DAY}"
    report "SINGLE_WATCH pid=$only day=${wday:-$DAY} already_one"
    exit 0
  fi
fi

# n==0 (or forced restart): clear only if no live watch
if list_real | grep -q .; then
  report "RACE live watch appeared — re-run ensure"
  exit 1
fi
# Safe clear of stale lockdir (no live holder)
if [[ -d "$LOCKDIR" ]]; then
  oldpid=""
  [[ -f "$PIDFILE" ]] && oldpid=$(cat "$PIDFILE" 2>/dev/null || true)
  if [[ -n "$oldpid" ]] && kill -0 "$oldpid" 2>/dev/null && cmd_is_watch "$oldpid"; then
    write_holder "$oldpid" "$(watch_day_of_pid "$oldpid" || echo "$DAY")"
    report "SINGLE_WATCH pid=$oldpid day=$DAY reclaim_existing"
    exit 0
  fi
  rm -f "$PIDFILE" "$DAYFILE" "$LOCKDIR/heartbeat" "${PIDFILE}.tmp" "${DAYFILE}.tmp" 2>/dev/null || true
  rmdir "$LOCKDIR" 2>/dev/null || rm -rf "$LOCKDIR"
fi
rm -f "$CLASSIC"

nohup /bin/bash "$SCRIPTS/watch_ready_harvest_once.sh" "$DAY" \
  >>"$LOGDIR/watch_ready_harvest_stdout.log" 2>&1 &
sleep 3
pids=()
while read -r p; do
  [[ -n "$p" ]] && pids+=("$p")
done < <(list_real | sort -u)
if [[ ${#pids[@]} -eq 1 ]]; then
  write_holder "${pids[0]}" "$DAY"
  report "SINGLE_WATCH pid=${pids[0]} day=$DAY started"
  exit 0
fi
if [[ -f "$CLASSIC" ]]; then
  cpid=$(cat "$CLASSIC" 2>/dev/null || true)
  if [[ -n "$cpid" ]] && kill -0 "$cpid" 2>/dev/null && cmd_is_watch "$cpid"; then
    write_holder "$cpid" "$DAY"
    report "SINGLE_WATCH pid=$cpid day=$DAY started_via_lockfile"
    exit 0
  fi
fi
report "FAILED watch_count=${#pids[@]} after_start"
exit 1
