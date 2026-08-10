#!/usr/bin/env bash
# Mac → Windows: read-only OBS product path probe. No invent. No thrash live OBS.
set -uo pipefail
DAY="${1:-$(date +%F)}"
HOST="${WINDOWS_SSH_HOST:-kyled@100.92.159.73}"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
RECEIPTS="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/wow"
OUT="${HOME}/Movies/WoW-Broll-Workflow/Returns"
mkdir -p "$RECEIPTS" "$OUT"

scp -o BatchMode=yes -o ConnectTimeout=15 \
  "$SCRIPTS/Probe-OBS-ProductPath.ps1" \
  "${HOST}:D:/WoW B-Roll Storage/_scripts/" >/dev/null 2>&1 || true

set +e
RAW=$(ssh -o BatchMode=yes -o ConnectTimeout=45 "$HOST" \
  "powershell -NoProfile -ExecutionPolicy Bypass -File \"D:\\WoW B-Roll Storage\\_scripts\\Probe-OBS-ProductPath.ps1\" -Day $DAY" 2>&1)
RC=$?
set -e
printf '%s\n' "$RAW"

# extract JSON object (first { ... last })
JSON=$(printf '%s\n' "$RAW" | python3 -c 'import sys; t=sys.stdin.read(); i=t.find("{"); j=t.rfind("}");
print(t[i:j+1] if i>=0 and j>i else "")')
if [[ -n "$JSON" ]]; then
  printf '%s\n' "$JSON" > "$OUT/OBS_PATH_PROBE_LATEST.json"
  printf '%s\n' "$JSON" > "${RECEIPTS}/OBS_PATH_PROBE_LATEST.json"
fi

# short MD for boards
python3 - "$OUT/OBS_PATH_PROBE_LATEST.json" "${RECEIPTS}/OBS_PATH_PROBE_LATEST.md" "$DAY" <<'PY' || true
import json, sys
from pathlib import Path
from datetime import datetime, timezone
jp, md, day = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
if not jp.is_file():
    raise SystemExit(0)
d=json.loads(jp.read_text())
md.write_text(f"""# OBS path probe
**day:** {day}
**utc:** {datetime.now(timezone.utc).isoformat()}
**obs_running:** {d.get('obs_running')}
**product_path_ok:** {d.get('product_path_ok')}
**file_path:** `{d.get('file_path_norm') or d.get('file_path')}`
**rec_tracks:** {d.get('rec_tracks')}
**day_raw_mp4:** {d.get('day_raw_mp4')} · **day_cand_mp4:** {d.get('day_cand_mp4')} · **base_today:** {d.get('base_today_masters')}
**has_today_masters:** {d.get('has_today_masters')}
**ready_to_record (profile):** {d.get('ready_to_record')}
**law:** read-only · no invent · do not thrash live OBS
""")
print(f"OBS_PROBE product_path_ok={d.get('product_path_ok')} has_masters={d.get('has_today_masters')} obs_running={d.get('obs_running')}")
PY

# Map Windows exit: 0 profile ready no masters, 2 has masters, 1 bad profile
exit "$RC"
