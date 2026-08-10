#!/usr/bin/env bash
# Rotate GCS VibeCast logs (gauntlet #85). Keep last N compressed.
set -euo pipefail
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
KEEP="${KEEP_LOGS:-8}"
MAX_BYTES="${MAX_LOG_BYTES:-2000000}"
mkdir -p "$LOGDIR"
shopt -s nullglob
for f in "$LOGDIR"/*.log; do
  base=$(basename "$f")
  sz=$(wc -c <"$f" | tr -d ' ')
  if [[ "$sz" -lt "$MAX_BYTES" ]]; then
    continue
  fi
  ts=$(date -u +%Y%m%dT%H%M%SZ)
  dest="${f}.${ts}"
  mv "$f" "$dest"
  gzip -f "$dest" 2>/dev/null || true
  : >"$f"
  echo "ROTATED $base size=$sz"
done
# prune old gz
ls -1t "$LOGDIR"/*.log.*.gz 2>/dev/null | tail -n +"$((KEEP + 1))" | while read -r old; do
  rm -f "$old"
  echo "PRUNE $old"
done
echo "LOG_ROTATE_OK dir=$LOGDIR keep=$KEEP"
exit 0
