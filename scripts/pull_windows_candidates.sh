#!/usr/bin/env bash
# Pull GCS VibeCast ship candidates Windows → Mac (Tailscale preferred).
# Law: candidates only — never demand full raw masters.
# Law: PowerShell lives in Stage-ShipCandidates.ps1 (bash eats $ in ssh -Command).
set -euo pipefail

DAY="${1:-$(date +%F)}"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
HOST="${WINDOWS_SSH_HOST:-$(python3 "$SCRIPTS/resolve_windows_host.py" --ssh)}"
WIN_STAGE="C:/Users/kyled/AppData/Local/Temp/gcs_cand_${DAY}"
MAC_ROOT="${HOME}/Movies/WoW-Broll-Workflow/Returns/returner-daily-${DAY}"
MAC_DEST="${MAC_ROOT}/candidates"
DRIVE_FALLBACK="$(python3 "$SCRIPTS/resolve_windows_host.py" --drive-offload)/${DAY}"
REMOTE_SCRIPTS="D:/WoW B-Roll Storage/_scripts"

mkdir -p "$MAC_DEST" "${MAC_ROOT}/analysis" "${MAC_ROOT}/markers"

echo "== pull_windows_candidates day=$DAY =="
ssh -o BatchMode=yes -o ConnectTimeout=20 "$HOST" \
  "powershell -NoProfile -Command \"New-Item -ItemType Directory -Force -Path 'D:\\WoW B-Roll Storage\\_scripts' | Out-Null\"" || true
scp -o BatchMode=yes -o ConnectTimeout=20 \
  "$SCRIPTS/Stage-ShipCandidates.ps1" \
  "${HOST}:${REMOTE_SCRIPTS}/" || true

if ssh -o BatchMode=yes -o ConnectTimeout=60 "$HOST" \
  "powershell -NoProfile -ExecutionPolicy Bypass -File \"D:\\WoW B-Roll Storage\\_scripts\\Stage-ShipCandidates.ps1\" -Day ${DAY}"; then
  scp -o BatchMode=yes -o ConnectTimeout=300 \
    "${HOST}:${WIN_STAGE}/"* \
    "$MAC_DEST/" || true
  scp -o BatchMode=yes -o ConnectTimeout=30 \
    "${HOST}:${WIN_STAGE}/markers/"* \
    "${MAC_ROOT}/markers/" 2>/dev/null || true
fi

# Drive fallback if Tailscale left nothing
if ! ls "$MAC_DEST"/*.mp4 >/dev/null 2>&1; then
  echo "Tailscale empty — trying Drive fallback: $DRIVE_FALLBACK"
  if [[ -d "$DRIVE_FALLBACK/candidates" ]]; then
    cp -f "$DRIVE_FALLBACK/candidates/"* "$MAC_DEST/" 2>/dev/null || true
    [[ -f "$DRIVE_FALLBACK/MANIFEST.json" ]] && cp -f "$DRIVE_FALLBACK/MANIFEST.json" "$MAC_DEST/"
  else
    echo "Drive fallback missing (not synced yet?)"
  fi
fi

echo "landed -> $MAC_DEST"
ls -la "$MAC_DEST" || true

if [[ -f "$MAC_DEST/MANIFEST.json" ]]; then
  python3 - <<PY
import json, hashlib
from pathlib import Path
d = Path("$MAC_DEST")
man = json.loads((d/"MANIFEST.json").read_text())
for c in man.get("candidates") or []:
    if not isinstance(c, dict):
        continue
    fn = c.get("filename")
    if not fn:
        continue
    p = d / fn
    if not p.is_file():
        print("MISSING", fn); continue
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    print(fn, "sha_ok", h == c.get("sha256"), "bytes", p.stat().st_size)
PY
fi
echo "DONE"
