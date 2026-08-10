#!/usr/bin/env bash
# After a play/record night (vibe-cast / vibe-podcast):
#   vibe session log → pull Windows lists → stitch package → pulse + vibecast status
# Fail-closed: no publish. Safe to re-run.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
WOW="$(cd "$ROOT/../.." && pwd)"
cd "$ROOT"

MODE="${VIBE_MODE:-muddy}"
echo "== post_night_mac mode=$MODE $(date -Iseconds) =="

python3 "$ROOT/log_vibe_session.py" --mode "$MODE" --scaffold-daily || echo "WARN: vibe session log non-zero"

if [[ -x "$ROOT/pull_windows_lists.sh" ]]; then
  bash "$ROOT/pull_windows_lists.sh" || echo "WARN: pull_windows_lists non-zero (continuing)"
else
  echo "WARN: pull_windows_lists.sh missing"
fi

python3 "$ROOT/stitch_returner_package.py" || echo "WARN: stitch non-zero"
python3 "$ROOT/merge_caption_seed.py" || true
python3 "$ROOT/validate_peaks.py" || true
python3 "$ROOT/qa_returner_daily.py" || true
python3 "$ROOT/skip_day_receipt.py" || true
python3 "$ROOT/returner_daily_board.py" || true
python3 "$ROOT/windows_reachability.py" || true
python3 "$ROOT/engine_pulse.py" --health ${SSH_TASKS:+--ssh-tasks} || true
python3 "$ROOT/vibecast_status.py" || true
python3 "$ROOT/gcs_citadel_status.py" || true
python3 "$ROOT/last_night_recap.py" || true

echo "DONE post_night_mac — LAST_NIGHT_RECAP · RETURNER_DAILY_BOARD · GCS_STATUS under $WOW/00-Index/"
