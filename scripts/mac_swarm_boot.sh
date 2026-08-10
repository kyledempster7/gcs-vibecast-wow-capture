#!/usr/bin/env bash
# Mac-side swarm truth — does not wait on Windows Stream Deck work.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
WOW="$(cd "$ROOT/../.." && pwd)"
INDEX="$WOW/00-Index"
cd "$ROOT"

echo "======== mac_swarm_boot ========"
echo "time: $(date -Iseconds)"
echo

echo "---- reachability (fast) ----"
python3 "$ROOT/windows_reachability.py" || true
echo

echo "---- K tally ----"
python3 "$ROOT/walk_with_kyle.py" --tally || true
echo

echo "---- doors resolve (sample) ----"
python3 "$ROOT/resolve_wow_door.py" --role windows_hello || true
python3 "$ROOT/resolve_wow_door.py" --role housing_session || true
python3 "$ROOT/resolve_wow_door.py" --role stream_deck_housing_bridge || true
echo

echo "---- returner board ----"
python3 "$ROOT/returner_daily_board.py" || true
python3 "$ROOT/skip_day_receipt.py" || true
echo

echo "---- health local ----"
python3 "$ROOT/wow_engine_health.py" || true
echo

echo "---- gcs + recap ----"
python3 "$ROOT/gcs_citadel_status.py" || true
python3 "$ROOT/last_night_recap.py" || true
echo

echo "Kyle doors:"
echo "  housing pocket: $INDEX/HOUSING_Y1_POCKET.md"
echo "  layer A pocket: $INDEX/LAYER_A_POCKET.md"
echo "  housing session: $INDEX/HOUSING_DECK_SESSION.md"
echo "  WINDOWS_HELLO:   $INDEX/WINDOWS_HELLO.md"
echo "======== mac_swarm done ========"
