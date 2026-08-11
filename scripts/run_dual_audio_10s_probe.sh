#!/usr/bin/env bash
# Controlled 10s dual-audio probe (T3). Never invent GREEN. No publish.
# Usage: run_dual_audio_10s_probe.sh /abs/path/to/test.mp4 [--write-stamp]
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
FILE="${1:-}"
shift || true
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "usage: $0 /abs/path/to/test.mp4 [--write-stamp]" >&2
  echo "see: $SCRIPTS/dual_audio_10s_path.md" >&2
  exit 2
fi
OUT="${HOME}/Movies/WoW-Broll-Workflow/Returns/AUDIO_GREEN_PROBE_LATEST.json"
mkdir -p "$(dirname "$OUT")"
ARGS=(--file "$FILE" --out-json "$OUT")
for a in "$@"; do
  if [[ "$a" == "--write-stamp" ]]; then
    ARGS+=(--write-stamp)
  fi
done
python3 "$SCRIPTS/audio_green_probe.py" "${ARGS[@]}"
echo "PROBE_JSON=$OUT"
if [[ -f "$OUT" ]]; then
  python3 -c "import json;d=json.load(open('''$OUT'''));print('status',d.get('status'));print('audio_streams',d.get('audio_stream_count'));print('stamp',d.get('stamp_written'))"
fi
