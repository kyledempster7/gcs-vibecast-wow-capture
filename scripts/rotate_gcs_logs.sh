#!/usr/bin/env bash
# Rotate GCS VibeCast logs (gauntlet #85). Keep last N compressed. bash3-safe.
set -euo pipefail
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
KEEP="${KEEP_LOGS:-8}"
MAX_BYTES="${MAX_LOG_BYTES:-2000000}"
mkdir -p "$LOGDIR"
RECEIPT="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast/LOG_ROTATION_LATEST.json"
rotated=0
pruned=0
# rotate oversized .log files
for f in "$LOGDIR"/*.log; do
  [ -f "$f" ] || continue
  sz=$(wc -c <"$f" | tr -d ' ')
  if [ "$sz" -lt "$MAX_BYTES" ]; then
    continue
  fi
  ts=$(date -u +%Y%m%dT%H%M%SZ)
  dest="${f}.${ts}"
  mv "$f" "$dest"
  gzip -f "$dest" 2>/dev/null || true
  : >"$f"
  rotated=$((rotated + 1))
  echo "ROTATED $(basename "$f") size=$sz"
done
# prune oldest gz beyond KEEP (bash3: no mapfile; tolerate zero gz)
n=0
set +e
while read -r old; do
  [ -n "$old" ] || continue
  n=$((n + 1))
  if [ "$n" -gt "$KEEP" ]; then
    rm -f -- "$old"
    pruned=$((pruned + 1))
    echo "PRUNE $old"
  fi
done < <(ls -1t "$LOGDIR"/*.log.*.gz 2>/dev/null)
set -e
mkdir -p "$(dirname "$RECEIPT")"
python3 - "$RECEIPT" "$LOGDIR" "$KEEP" "$MAX_BYTES" "$rotated" "$pruned" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

out, logdir, keep, max_bytes, rotated, pruned = sys.argv[1:]
body = {
    "schema": "gcs_log_rotation/v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "status": "PASS",
    "logdir": logdir,
    "keep_compressed": int(keep),
    "max_log_bytes": int(max_bytes),
    "rotated": int(rotated),
    "pruned": int(pruned),
    "cadence_owner": "com.kyle.gcs.wow-soft-poll-harvest",
    "may_publish": False,
}
Path(out).write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
PY
echo "LOG_ROTATE_OK dir=$LOGDIR keep=$KEEP"
exit 0
