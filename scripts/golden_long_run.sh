#!/usr/bin/env bash
# Golden long run — agent-green durable loop for VibeCast Mac seat.
# Fence → single watch → operator/auto-session → harvest when ready_today → residual.
# Fail-closed: no invent FOOTAGE · no publish · no Factory thrash · no dual watches.
# Exit 0 on clean end/timeout of budget; lockdir single-instance.
set -uo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY="${1:-$(date +%F)}"
MAX_HOURS="${MAX_HOURS:-10}"
TICK_SEC="${TICK_SEC:-180}"
# Residual cadence (ticks): health every tick via operator; heavy every N
HEAVY_EVERY="${HEAVY_EVERY:-20}"   # ~60m at 180s
BACKUP_EVERY="${BACKUP_EVERY:-40}" # ~2h
GAUNTLET_EVERY="${GAUNTLET_EVERY:-40}"
# Watch budget when we (re)start one
export MAX_MIN="${MAX_MIN:-720}"

LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
RECEIPTS="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/wow"
OUT="${HOME}/Movies/WoW-Broll-Workflow/Returns"
STATUS_JSON="${OUT}/GOLDEN_LONG_RUN_STATUS.json"
STATUS_MD="${HOME}/Kyles_Vault/kyles_corner/Games/WoW/00-Index/GOLDEN_LONG_RUN_BOARD.md"
mkdir -p "$LOGDIR" "$RECEIPTS" "$OUT"

LOCKDIR="$LOGDIR/golden_long_run.lockdir"
PIDFILE="$LOCKDIR/pid"
LOG="$LOGDIR/golden_long_run.log"
SELF=$$

release() {
  rm -f "$PIDFILE" 2>/dev/null || true
  rmdir "$LOCKDIR" 2>/dev/null || true
}
if ! mkdir "$LOCKDIR" 2>/dev/null; then
  old=$(cat "$PIDFILE" 2>/dev/null || true)
  if [[ -n "$old" ]] && kill -0 "$old" 2>/dev/null; then
    if ps -p "$old" -o command= 2>/dev/null | grep -q 'golden_long_run\.sh'; then
      echo "FAILED golden already running pid=$old"
      exit 1
    fi
  fi
  release
  if ! mkdir "$LOCKDIR" 2>/dev/null; then
    echo "FAILED golden lock busy"
    exit 1
  fi
fi
echo "$SELF" >"$PIDFILE"
trap 'release' EXIT

python3 "$SCRIPTS/assert_vibecast_write_fence.py" || exit 2

END=$(( $(date +%s) + MAX_HOURS * 3600 ))
START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
tick=0
last_state="BOOT"
harvested_today=0

write_status() {
  local state="$1"
  local note="${2:-}"
  last_state="$state"
  local utc now_ready
  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  now_ready_py="False"
  if [[ -f "$OUT/SOFT_POLL_LATEST.json" ]]; then
    now_ready_py=$(python3 - "$OUT/SOFT_POLL_LATEST.json" "$DAY" <<'PY' || true
import json, sys
from pathlib import Path
p, day = Path(sys.argv[1]), sys.argv[2]
d = json.loads(p.read_text()) if p.is_file() else {}
rt = d.get("ready_today")
if rt is None:
    for row in d.get("days") or []:
        if row.get("day") == day:
            rt = bool(row.get("ready")); break
print("True" if rt else "False")
PY
)
    [[ -z "${now_ready_py}" ]] && now_ready_py="False"
  fi
  local watch_pid=""
  if [[ -f "$LOGDIR/watch_ready_harvest.lockdir/pid" ]]; then
    watch_pid=$(cat "$LOGDIR/watch_ready_harvest.lockdir/pid" 2>/dev/null || true)
  fi
  # Safe note for Python string (no newlines)
  note_safe=$(printf '%s' "$note" | tr '\n' ' ' | sed "s/'//g")
  python3 - "$STATUS_JSON" "$STATUS_MD" "$state" "$note_safe" "$watch_pid" <<PY
import json, sys
from pathlib import Path
status_path = Path(sys.argv[1])
md_path = Path(sys.argv[2])
state = sys.argv[3]
note = sys.argv[4]
watch_pid = sys.argv[5]
doc = {
  "schema": "gcs_golden_long_run/v1",
  "day": "$DAY",
  "pid": $SELF,
  "started_utc": "$START_UTC",
  "updated_utc": "$utc",
  "max_hours": $MAX_HOURS,
  "tick": $tick,
  "state": state,
  "note": note,
  "ready_today": $now_ready_py,
  "harvested_today": bool($harvested_today),
  "watch_pid": watch_pid,
  "law": "no invent FOOTAGE · no silent publish · agent-green waiting is green",
  "log": "$LOG",
}
status_path.write_text(json.dumps(doc, indent=2) + "\n")
md = f"""---
type: golden-long-run-board
status: active
updated: {doc['updated_utc']}
day: {doc['day']}
---

# Golden long run board

| Field | Value |
|-------|-------|
| **State** | \`{doc['state']}\` |
| **Day** | {doc['day']} |
| **PID** | {doc['pid']} |
| **Tick** | {doc['tick']} |
| **ready_today** | {doc['ready_today']} |
| **harvested_today** | {doc['harvested_today']} |
| **Watch pid** | {doc['watch_pid'] or '—'} |
| **Budget** | {doc['max_hours']}h from {doc['started_utc']} |
| **Note** | {doc['note'] or '—'} |

**Law:** no invent · no publish · single watch · agent-green waiting = success while masters absent.

**Log:** \`{doc['log']}\`
**JSON:** \`{status_path}\`
"""
md_path.write_text(md)
print(f"status {state} ready_today={doc['ready_today']} tick={doc['tick']}")
PY
}

log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >>"$LOG"; }

log "==== GOLDEN START day=$DAY max_h=$MAX_HOURS tick=${TICK_SEC}s pid=$SELF ===="
write_status "RUNNING" "boot"

# Optional deploy at start (skip if SKIP_DEPLOY=1 — default run deploys once, soft-fail)
if [[ "${SKIP_DEPLOY:-0}" != "1" ]] && [[ -f "$SCRIPTS/deploy_windows_scripts.sh" ]]; then
  log "deploy start"
  bash "$SCRIPTS/deploy_windows_scripts.sh" >>"$LOG" 2>&1 || log "deploy_warn"
  log "deploy done"
fi

while [[ $(date +%s) -lt $END ]]; do
  tick=$((tick + 1))
  log "---- tick=$tick ----"

  # Day roll: if local date changed mid-run, follow wall clock day
  NEWDAY=$(date +%F)
  if [[ "$NEWDAY" != "$DAY" ]]; then
    log "day_roll $DAY -> $NEWDAY"
    DAY="$NEWDAY"
    harvested_today=0
  fi

  python3 "$SCRIPTS/assert_vibecast_write_fence.py" >>"$LOG" 2>&1 || {
    log "FENCE_FAIL"
    write_status "FENCE_FAIL" "assert fence"
    sleep "$TICK_SEC"
    continue
  }

  bash "$SCRIPTS/ensure_single_watch.sh" "$DAY" >>"$LOG" 2>&1 || log "ensure_watch_warn"

  # Operator: soft_poll (rate-limited) + Auto-Session-End + harvest if ready
  # NEVER enable set -e here — operator/not-ready exit 1 is normal agent-green.
  set +e
  bash "$SCRIPTS/mac_vibecast_operator.sh" "$DAY" >>"$LOG" 2>&1
  ORC=$?
  log "operator_rc=$ORC"

  # Detect ready_today / harvest lock
  TODAY_READY=1
  python3 - "$OUT/SOFT_POLL_LATEST.json" "$DAY" <<'PY' >>"$LOG" 2>&1
import json, sys
from pathlib import Path
p, day = Path(sys.argv[1]), sys.argv[2]
if not p.is_file():
    sys.exit(1)
d = json.loads(p.read_text())
for row in d.get("days") or []:
    if row.get("day") == day and row.get("ready"):
        sys.exit(0)
sys.exit(1)
PY
  TODAY_READY=$?

  if [[ "$TODAY_READY" -eq 0 ]]; then
    if [[ -f "$OUT/returner-daily-${DAY}/.harvest_once" ]] || [[ -d "$OUT/returner-daily-${DAY}/candidates" ]]; then
      harvested_today=1
      if [[ -f "$OUT/returner-daily-${DAY}/analysis/human_verdicts.json" ]]; then
        if grep -q '"KEEP"' "$OUT/returner-daily-${DAY}/analysis/human_verdicts.json" 2>/dev/null; then
          python3 "$SCRIPTS/write_weight_row.py" --day-dir "$OUT/returner-daily-${DAY}" --note "golden residual" >>"$LOG" 2>&1
          python3 "$SCRIPTS/draft_daily_personality_package.py" --day-dir "$OUT/returner-daily-${DAY}" --force >>"$LOG" 2>&1
        fi
      fi
      write_status "HARVESTED_OR_READY" "ready_today true; review open_review_pack"
    else
      log "ready but no harvest lock — post_play_harvest"
      bash "$SCRIPTS/post_play_harvest.sh" "$DAY" >>"$LOG" 2>&1
      write_status "HARVESTING" "post_play attempted"
    fi
  else
    write_status "WAITING_WINDOWS_MASTERS" "markers/export pending agent-green waiting"
  fi

  # Heavy residual (agent-green only)
  if (( tick % HEAVY_EVERY == 0 )); then
    log "heavy residual"
    python3 "$SCRIPTS/gcs_pipeline_health.py" >>"$LOG" 2>&1
    python3 "$SCRIPTS/write_waiting_board.py" >>"$LOG" 2>&1
    if [[ -d "$OUT/returner-daily-2026-08-09" ]]; then
      python3 "$SCRIPTS/draft_daily_personality_package.py" --day-dir "$OUT/returner-daily-2026-08-09" >>"$LOG" 2>&1
    fi
  fi
  if (( tick % BACKUP_EVERY == 0 )) && [[ -f "$SCRIPTS/mac_backup_vibecast.sh" ]]; then
    log "backup tick"
    bash "$SCRIPTS/mac_backup_vibecast.sh" >>"$LOG" 2>&1
  fi
  if (( tick % GAUNTLET_EVERY == 0 )) && [[ -f "$SCRIPTS/gcs_vibecast_gauntlet.py" ]]; then
    log "gauntlet tick"
    python3 "$SCRIPTS/gcs_vibecast_gauntlet.py" >>"$LOG" 2>&1
  fi

  # Receipt pulse (overwrite latest)
  cat > "${RECEIPTS}/GOLDEN_LONG_RUN_LATEST.md" <<EOF
# Golden long run
**day:** $DAY
**utc:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**pid:** $SELF
**tick:** $tick
**state:** $last_state
**ready_today:** $([[ $TODAY_READY -eq 0 ]] && echo true || echo false)
**harvested_today:** $harvested_today
**log:** $LOG
**board:** $STATUS_MD
**law:** no invent · no publish · agent-green waiting OK
EOF
  set +e

  sleep "$TICK_SEC"
done

log "==== GOLDEN BUDGET END day=$DAY ticks=$tick ===="
write_status "BUDGET_END" "max_hours=$MAX_HOURS reached; LaunchAgent+ensure_watch remain"
exit 0
