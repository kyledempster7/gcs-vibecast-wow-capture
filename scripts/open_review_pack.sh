#!/usr/bin/env bash
# M6: One command — inject one-tap + ensure the loopback feedback service.
# No foreground browser control. No publish. Kyle only KEEP/REJECT.
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
LABEL="com.kyle.gcs.vibecast-review-feedback"
DOMAIN="gui/$(id -u)"
if ! launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; then
  bash "$SCRIPTS/install_review_feedback_launchagent.sh"
else
  launchctl kickstart -k "$DOMAIN/$LABEL"
fi
sleep 1
curl --fail --silent --show-error "http://127.0.0.1:8765/healthz"
echo
echo "REVIEW_READY day=$DAY url=http://127.0.0.1:8765/index.html no_foreground_control=true"
