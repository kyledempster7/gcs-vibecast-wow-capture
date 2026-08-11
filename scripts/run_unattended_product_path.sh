#!/usr/bin/env bash
# One-shot unattended product path — no chat proceed thrash.
# Branch A: harvest→enhance→review when ready_today.
# Branch B: BLOCKED_ON_MASTERS_ARMED + golden/watch armed; exit 0.
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
DAY="${1:-$(date +%F)}"
exec python3 "$SCRIPTS/unattended_product_path.py" "$DAY"
