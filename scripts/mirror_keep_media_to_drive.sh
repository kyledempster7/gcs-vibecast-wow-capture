#!/usr/bin/env bash
# M2: Ensure KEEP Moments trees exist on Drive archive-broll (media, not just index).
set -euo pipefail
MEDIA="$HOME/Movies/WoW-Broll-Workflow/Moments-Library"
DRIVE=""
while IFS= read -r d; do DRIVE="$d"; break
done < <(find "$HOME/Library/CloudStorage" -maxdepth 4 -type d -name 'GCS-VibeCast-Offload' 2>/dev/null || true)
if [[ -z "$DRIVE" || ! -d "$MEDIA" ]]; then
  echo "MIRROR_KEEP_SKIP missing drive or media" >&2
  exit 1
fi
DEST="$DRIVE/archive-broll"
mkdir -p "$DEST"
n=0
# Prefer folders that have ARCHIVE.json or clips/ with KEEP provenance
for dir in "$MEDIA"/*/; do
  [[ -d "$dir" ]] || continue
  base=$(basename "$dir")
  [[ "$base" == .* ]] && continue
  if [[ -f "${dir}ARCHIVE.json" ]] || [[ -d "${dir}clips" ]]; then
    rsync -a --exclude '.DS_Store' "$dir" "$DEST/$base/"
    n=$((n + 1))
    echo "MIRRORED $base"
  fi
done
# indexes
mkdir -p "$DRIVE/backup-code/moments-index"
for f in CATALOG.json KEEP_ONLY_INDEX.json KEEP_ONLY_INDEX.md; do
  [[ -f "$MEDIA/$f" ]] && cp "$MEDIA/$f" "$DRIVE/backup-code/moments-index/" || true
done
echo "MIRROR_KEEP_OK folders=$n dest=$DEST"
exit 0
