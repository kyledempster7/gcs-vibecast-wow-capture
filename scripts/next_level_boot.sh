#!/usr/bin/env bash
# Cold start for next agent after compact — status + gaps, no publish.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
WOW="$(cd "$ROOT/../.." && pwd)"
INDEX="$WOW/00-Index"
cd "$ROOT"

echo "======== GCS / VibeCast next_level_boot ========"
echo "vault: $WOW"
echo "time:  $(date -Iseconds)"
echo

echo "---- gaps register (head) ----"
if [[ -f "$INDEX/GAPS_AND_NEXT_LEVEL.md" ]]; then
  head -n 40 "$INDEX/GAPS_AND_NEXT_LEVEL.md"
else
  echo "MISSING GAPS_AND_NEXT_LEVEL.md"
fi
echo

echo "---- Kyle open tally ----"
python3 "$ROOT/walk_with_kyle.py" --tally || true
echo

echo "---- GCS status ----"
python3 "$ROOT/gcs_citadel_status.py" || true
echo

echo "---- Windows reachability (Tailscale fast) ----"
python3 "$ROOT/windows_reachability.py" || true
echo

echo "---- package / daily board truth ----"
python3 "$ROOT/harvest_completeness.py" --write-live || true
python3 "$ROOT/returner_daily_board.py" || true
python3 "$ROOT/skip_day_receipt.py" || true
echo

echo "---- engine health (local + media HOLD rule) ----"
python3 "$ROOT/wow_engine_health.py" || true
echo

if [[ "${SSH_TASKS:-}" == "1" ]]; then
  echo "---- engine health SSH tasks (skips hang if TS offline) ----"
  python3 "$ROOT/wow_engine_health.py" --ssh-tasks || true
fi

echo "---- last night recap ----"
python3 "$ROOT/last_night_recap.py" || true
echo

echo "Read next: $INDEX/COMPACT_MASTER_HANDOFF_2026-08-09.md"
echo "Kyle door: $INDEX/TOMORROW_SESSION.md"
echo "Gaps full: $INDEX/GAPS_AND_NEXT_LEVEL.md"
echo "Board:     $INDEX/RETURNER_DAILY_BOARD.md"
echo "Win reach: $INDEX/WINDOWS_REACHABILITY_latest.md"
echo "Graph:     $WOW/.understand-anything/product_graph.html"
echo "======== boot done ========"
