#!/usr/bin/env bash
# Rotate GCS VibeCast logs (gauntlet #85). Keep last N compressed. bash3-safe.
set -euo pipefail
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
KEEP="${KEEP_LOGS:-8}"
MAX_BYTES="${MAX_LOG_BYTES:-2000000}"
mkdir -p "$LOGDIR"
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
  echo "ROTATED $(basename "$f") size=$sz"
done
# prune oldest gz beyond KEEP (bash3: no mapfile)
n=0
ls -1t "$LOGDIR"/*.log.*.gz 2>/dev/null | while read -r old; do
  n=$((n + 1))
  if [ "$n" -gt "$KEEP" ]; then
    rm -f -- "$old"
    echo "PRUNE $old"
  fi
done
echo "LOG_ROTATE_OK dir=$LOGDIR keep=$KEEP"
exit 0
