#!/usr/bin/env bash
# Mirror wow control-plane receipts → Drive backup-code (unwired #10).
set -euo pipefail
SRC="${HOME}/Library/Application Support/UAH/butler/control-plane/receipts/wow"
DEST=""
# Prefer CloudStorage Google Drive (spaces in path — use find, not unquoted globs)
while IFS= read -r d; do
  DEST="${d}/backup-code/receipts-wow"
  break
done < <(find "${HOME}/Library/CloudStorage" -maxdepth 4 -type d -name 'GCS-VibeCast-Offload' 2>/dev/null || true)

if [[ -z "$DEST" ]]; then
  while IFS= read -r d; do
    DEST="${d}/backup-code/receipts-wow"
    break
  done < <(find "/Volumes" -maxdepth 5 -type d -name 'GCS-VibeCast-Offload' 2>/dev/null || true)
fi

if [[ -z "$DEST" ]]; then
  echo "DRIVE_MIRROR_SKIP no GCS-VibeCast-Offload tree" >&2
  exit 1
fi
mkdir -p "$DEST"
rsync -a --delete --exclude '.DS_Store' "$SRC/" "$DEST/"
count=$(find "$DEST" -type f | wc -l | tr -d ' ')
echo "DRIVE_RECEIPTS_MIRROR ok dest=$DEST files=$count"
exit 0
