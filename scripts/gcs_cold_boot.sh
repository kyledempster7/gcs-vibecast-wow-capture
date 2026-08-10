#!/usr/bin/env bash
# Cold-agent 5-minute boot: status → shortlist path → next safe act. No publish.
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
WOW="$(cd "$SCRIPTS/../.." && pwd)"
echo "== GCS cold boot =="
echo "Spec: $WOW/04-Story-and-Capture/PRODUCT_SYSTEM_SPEC.md"
echo "Roadmap: $WOW/04-Story-and-Capture/ROADMAP_P0_P2_TOP10.md"
echo "Hostile: $WOW/04-Story-and-Capture/HOSTILE_REVIEW_PRODUCT_SYSTEM_20260810.md"
echo ""
python3 "$SCRIPTS/gcs_pipeline_health.py"
echo ""
DAY="$(python3 - <<'PY'
from pathlib import Path
b=Path.home()/"Movies"/"WoW-Broll-Workflow"/"Returns"
days=sorted([p for p in b.iterdir() if p.is_dir() and "returner" in p.name], key=lambda p:p.name, reverse=True)
for d in days:
  if any((d/"candidates").glob("*.mp4")):
    print(d); break
PY
)"
if [[ -n "${DAY}" ]]; then
  echo "Latest harvest day: $DAY"
  echo "SHORTLIST: $DAY/review-pack/SHORTLIST.md"
  echo "Review HTML: $DAY/review-pack/index.html"
  echo "NEXT brief: $DAY/NEXT_NIGHT_BRIEF.md"
fi
echo ""
echo "Next safe act: first OPEN rank in ROADMAP_P0_P2_TOP10 (Windows: Deck multi-act human night / dual audio; Mac: residual detector ROI)."
echo "Law: no invent FOOTAGE · no silent publish · KEEP wins."
