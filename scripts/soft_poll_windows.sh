#!/usr/bin/env bash
# Mac → Windows soft-poll with READY schema. No invent, no publish.
# Exit: 0=any day ready, 1=not ready, 2=ssh/transport fail
# Default: DAY1=today + DAY2=yesterday (multi-day SOFT_POLL_LATEST).
set -uo pipefail
HOST="${WINDOWS_SSH_HOST:-kyled@100.92.159.73}"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY1="${1:-$(date +%F)}"
if [[ -n "${2:-}" ]]; then
  DAY2="$2"
else
  # previous calendar day (macOS/BSD date)
  DAY2=$(date -j -v-1d -f "%Y-%m-%d" "$DAY1" "+%Y-%m-%d" 2>/dev/null \
    || python3 -c "from datetime import date,timedelta; d=date.fromisoformat('$DAY1'); print(d-timedelta(days=1))")
fi
# Allow single-day force: bash soft_poll_windows.sh DAY sameDAY
REMOTE="C:/Users/kyled/AppData/Local/Temp/soft_poll_windows.ps1"
OUT_DIR="${HOME}/Movies/WoW-Broll-Workflow/Returns"
mkdir -p "$OUT_DIR"

if ! scp -o BatchMode=yes -o ConnectTimeout=15 \
  "$SCRIPTS/soft_poll_windows.ps1" "${HOST}:${REMOTE}"; then
  echo "SOFT_POLL_TRANSPORT_FAIL scp" >&2
  exit 2
fi

set +e
# -File cannot parse @('d1','d2') array from ssh; use -Command + -Days d1,d2
if [[ "$DAY1" == "$DAY2" ]]; then
  RAW=$(ssh -o BatchMode=yes -o ConnectTimeout=45 "$HOST" \
    "powershell -NoProfile -ExecutionPolicy Bypass -Command \"& 'C:\\Users\\kyled\\AppData\\Local\\Temp\\soft_poll_windows.ps1' -Days '${DAY1}'\"" 2>&1)
else
  RAW=$(ssh -o BatchMode=yes -o ConnectTimeout=45 "$HOST" \
    "powershell -NoProfile -ExecutionPolicy Bypass -Command \"& 'C:\\Users\\kyled\\AppData\\Local\\Temp\\soft_poll_windows.ps1' -Days '${DAY1}','${DAY2}'\"" 2>&1)
fi
SSH_RC=$?
set -e

printf '%s\n' "$RAW"

JSON_LINE=$(printf '%s\n' "$RAW" | grep '^READY_JSON:' | tail -1 || true)
if [[ -z "$JSON_LINE" ]]; then
  echo "SOFT_POLL_NO_READY_JSON ssh_rc=$SSH_RC" >&2
  exit 2
fi
JSON="${JSON_LINE#READY_JSON:}"
RECEIPT="${OUT_DIR}/SOFT_POLL_LATEST.json"
printf '%s\n' "$JSON" > "$RECEIPT"

# Per-day SOFT_POLL.json for every day in the READY_JSON payload
python3 - "$RECEIPT" "$OUT_DIR" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
data = json.loads(p.read_text(encoding="utf-8"))
ready = bool(data.get("ready"))
print(f"soft_poll ready={ready} days={len(data.get('days') or [])} -> {p}")
for d in data.get("days") or []:
    day = d.get("day") or "unknown"
    day_dir = out_dir / f"returner-daily-{day}" / "analysis"
    day_dir.mkdir(parents=True, exist_ok=True)
    # single-day slice for that day's analysis folder
    slice_doc = {
        "schema": data.get("schema"),
        "generated_at_utc": data.get("generated_at_utc"),
        "host": data.get("host"),
        "ready": bool(d.get("ready")),
        "days": [d],
        "law": data.get("law"),
    }
    (day_dir / "SOFT_POLL.json").write_text(json.dumps(slice_doc, indent=2) + "\n", encoding="utf-8")
    print(
        f"  day={day} ready={d.get('ready')} reason={d.get('reason')} "
        f"cand={d.get('candidates_n')} stage={d.get('stage_mp4_n')}"
    )
sys.exit(0 if ready else 1)
PY
