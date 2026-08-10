#!/usr/bin/env bash
# M6: One command — inject one-tap + start local feedback server + open browser.
# No publish. Kyle only KEEP/REJECT.
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY="${1:-}"
RETURNS="$HOME/Movies/WoW-Broll-Workflow/Returns"
if [[ -z "$DAY" ]]; then
  # latest returner-daily-* with review-pack
  DAY=$(ls -1d "$RETURNS"/returner-daily-* 2>/dev/null | sort | tail -1 | xargs -I{} basename {} | sed 's/returner-daily-//')
fi
DAY_DIR="$RETURNS/returner-daily-${DAY}"
if [[ ! -d "$DAY_DIR/review-pack" ]]; then
  echo "missing review-pack: $DAY_DIR/review-pack" >&2
  exit 2
fi
python3 "$SCRIPTS/assert_vibecast_write_fence.py"
python3 "$SCRIPTS/review_pack_feedback_server.py" --day-dir "$DAY_DIR" --inject-only
# open static index first; server for one-tap in background
open "$DAY_DIR/review-pack/index.html" 2>/dev/null || true
# start server if not already
if ! lsof -iTCP:8765 -sTCP:LISTEN >/dev/null 2>&1; then
  nohup python3 "$SCRIPTS/review_pack_feedback_server.py" --day-dir "$DAY_DIR" --port 8765 \
    >"$HOME/Library/Logs/gcs-vibecast-wow/review_server.log" 2>&1 &
  echo "REVIEW_SERVER http://127.0.0.1:8765/index.html pid=$!"
  sleep 0.5
  open "http://127.0.0.1:8765/index.html" 2>/dev/null || true
else
  echo "REVIEW_SERVER already on 8765"
  open "http://127.0.0.1:8765/index.html" 2>/dev/null || true
fi
echo "REVIEW_OPEN day=$DAY path=$DAY_DIR/review-pack"
