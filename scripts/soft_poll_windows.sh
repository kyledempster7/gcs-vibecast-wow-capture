#!/usr/bin/env bash
# Mac → Windows soft-poll with READY schema. No invent, no publish.
# Exit: 0=any day ready, 1=not ready, 2=ssh/transport fail
# Default: DAY1=today + DAY2=yesterday (multi-day SOFT_POLL_LATEST).
# Right-size: prefer resident D:\_scripts (no scp thrash). Set SOFT_POLL_FORCE_SCP=1 to redeploy.
set -uo pipefail
HOST="${WINDOWS_SSH_HOST:-kyled@100.92.159.73}"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY1="${1:-$(date +%F)}"
if [[ -n "${2:-}" ]]; then
  DAY2="$2"
else
  DAY2=$(date -j -v-1d -f "%Y-%m-%d" "$DAY1" "+%Y-%m-%d" 2>/dev/null \
    || python3 -c "from datetime import date,timedelta; d=date.fromisoformat('$DAY1'); print(d-timedelta(days=1))")
fi
OUT_DIR="${HOME}/Movies/WoW-Broll-Workflow/Returns"
mkdir -p "$OUT_DIR"

# Prefer dual-SoT resident path; temp only if force-scp or resident missing
RESIDENT="D:\\WoW B-Roll Storage\\_scripts\\soft_poll_windows.ps1"
TEMP_REMOTE="C:/Users/kyled/AppData/Local/Temp/soft_poll_windows.ps1"
PS1_PATH="$RESIDENT"

if [[ "${SOFT_POLL_FORCE_SCP:-0}" == "1" ]]; then
  if ! scp -o BatchMode=yes -o ConnectTimeout=15 \
    "$SCRIPTS/soft_poll_windows.ps1" "${HOST}:${TEMP_REMOTE}"; then
    echo "SOFT_POLL_TRANSPORT_FAIL scp" >&2
    exit 2
  fi
  PS1_PATH="C:\\Users\\kyled\\AppData\\Local\\Temp\\soft_poll_windows.ps1"
fi

set +e
if [[ "$DAY1" == "$DAY2" ]]; then
  RAW=$(ssh -o BatchMode=yes -o ConnectTimeout=45 "$HOST" \
    "powershell -NoProfile -ExecutionPolicy Bypass -Command \"& '${PS1_PATH}' -Days '${DAY1}'\"" 2>&1)
else
  RAW=$(ssh -o BatchMode=yes -o ConnectTimeout=45 "$HOST" \
    "powershell -NoProfile -ExecutionPolicy Bypass -Command \"& '${PS1_PATH}' -Days '${DAY1}','${DAY2}'\"" 2>&1)
fi
SSH_RC=$?
set -e

# Resident missing → one-time scp + retry
if [[ "$SSH_RC" -ne 0 ]] || ! printf '%s\n' "$RAW" | grep -q '^READY_JSON:'; then
  if [[ "${SOFT_POLL_FORCE_SCP:-0}" != "1" ]]; then
    if scp -o BatchMode=yes -o ConnectTimeout=15 \
      "$SCRIPTS/soft_poll_windows.ps1" "${HOST}:D:/WoW B-Roll Storage/_scripts/soft_poll_windows.ps1" \
      2>/dev/null; then
      set +e
      if [[ "$DAY1" == "$DAY2" ]]; then
        RAW=$(ssh -o BatchMode=yes -o ConnectTimeout=45 "$HOST" \
          "powershell -NoProfile -ExecutionPolicy Bypass -Command \"& '${RESIDENT}' -Days '${DAY1}'\"" 2>&1)
      else
        RAW=$(ssh -o BatchMode=yes -o ConnectTimeout=45 "$HOST" \
          "powershell -NoProfile -ExecutionPolicy Bypass -Command \"& '${RESIDENT}' -Days '${DAY1}','${DAY2}'\"" 2>&1)
      fi
      SSH_RC=$?
      set -e
    fi
  fi
fi

printf '%s\n' "$RAW"

JSON_LINE=$(printf '%s\n' "$RAW" | grep '^READY_JSON:' | tail -1 || true)
if [[ -z "$JSON_LINE" ]]; then
  echo "SOFT_POLL_NO_READY_JSON ssh_rc=$SSH_RC" >&2
  exit 2
fi
JSON="${JSON_LINE#READY_JSON:}"
RECEIPT="${OUT_DIR}/SOFT_POLL_LATEST.json"
printf '%s\n' "$JSON" > "$RECEIPT"

python3 - "$RECEIPT" "$OUT_DIR" <<'PY'
import json, sys
from datetime import date
from pathlib import Path
p = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
data = json.loads(p.read_text(encoding="utf-8"))
days = data.get("days") or []
ready_any = any(bool(d.get("ready")) for d in days if isinstance(d, dict))
today = date.today().isoformat()
today_row = next((d for d in days if isinstance(d, dict) and d.get("day") == today), None)
ready_today = bool(today_row.get("ready")) if today_row else False
# Preserve Windows ready (any-day) as ready_any; ready = ready_today for ops honesty
data["ready_any"] = ready_any if days else bool(data.get("ready"))
data["ready_today"] = ready_today
data["ready"] = ready_today  # harvest-today truth; multi-day detail stays in days[]
data["schema"] = data.get("schema") or "gcs_soft_poll_ready/v1"
p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(
    f"soft_poll ready_today={ready_today} ready_any={data['ready_any']} "
    f"days={len(days)} -> {p}"
)
for d in days:
    day = d.get("day") or "unknown"
    day_dir = out_dir / f"returner-daily-{day}" / "analysis"
    day_dir.mkdir(parents=True, exist_ok=True)
    slice_doc = {
        "schema": data.get("schema"),
        "generated_at_utc": data.get("generated_at_utc"),
        "host": data.get("host"),
        "ready": bool(d.get("ready")),
        "ready_today": ready_today,
        "days": [d],
        "law": data.get("law"),
    }
    (day_dir / "SOFT_POLL.json").write_text(json.dumps(slice_doc, indent=2) + "\n", encoding="utf-8")
    print(
        f"  day={day} ready={d.get('ready')} reason={d.get('reason')} "
        f"cand={d.get('candidates_n')} stage={d.get('stage_mp4_n')}"
    )
# Exit 0 only if *today* ready (matches harvest_if_ready / post_play)
sys.exit(0 if ready_today else 1)
PY
# Propagate ready_today exit (script has no set -e)
exit $?
