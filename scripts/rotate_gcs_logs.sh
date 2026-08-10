#!/usr/bin/env bash
# Rotate GCS VibeCast logs (gauntlet #85). Keep last N compressed.
set -euo pipefail
LOGDIR="${HOME}/Library/Logs/gcs-vibecast-wow"
KEEP="${KEEP_LOGS:-8}"
MAX_BYTES="${MAX_LOG_BYTES:-2000000}"
mkdir -p "$LOGDIR"
shopt -s nullglob
for f in "$LOGDIR"/*.log; do
  [[ -f "$f" ]] || continue
  sz=$(wc -c <"$f" | tr -d ' ')
  if [[ "$sz" -lt "$MAX_BYTES" ]]; then
    continue
  fi
  ts=$(date -u +%Y%m%dT%H%M%SZ)
  dest="${f}.${ts}"
  mv "$f" "$dest"
  if command -v gzip >/dev/null 2>&1; then
    gzip -f "$dest" || true
  fi
  : >"$f"
  echo "ROTATED $(basename "$f") size=$sz"
done
# prune oldest gz beyond KEEP
mapfile -t gz < <(ls -1t "$LOGDIR"/*.log.*.gz 2>/dev/null || true)
if ((${#gz[@]} > KEEP)); then
  for ((i = KEEP; i < ${#gz[@]}; i++)); do
    rm -f -- "${gz[i]}"
    echo "PRUNE ${gz[i]}"
  done
fi
echo "LOG_ROTATE_OK dir=$LOGDIR keep=$KEEP"
exit 0
