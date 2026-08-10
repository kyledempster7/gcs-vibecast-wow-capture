#!/usr/bin/env bash
# Mac-only: score → pride cuts from KEEP → review-pack. NEVER publishes.
set -euo pipefail
DAY="${1:-2026-08-09}"
# Accept either Returns/YYYY-MM-DD or Returns/returner-daily-YYYY-MM-DD
if [[ -d "${HOME}/Movies/WoW-Broll-Workflow/Returns/returner-daily-${DAY}/candidates" ]]; then
  ROOT="${HOME}/Movies/WoW-Broll-Workflow/Returns/returner-daily-${DAY}"
elif [[ -d "${HOME}/Movies/WoW-Broll-Workflow/Returns/${DAY}/candidates" ]]; then
  ROOT="${HOME}/Movies/WoW-Broll-Workflow/Returns/${DAY}"
else
  echo "missing Returns folder for day=$DAY" >&2
  exit 1
fi
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
CAND="${ROOT}/candidates"
ANALYSIS="${ROOT}/analysis"
HUMAN="${ANALYSIS}/human_verdicts.json"

if [[ ! -d "$CAND" ]]; then
  echo "missing $CAND" >&2
  exit 1
fi
mkdir -p "$ANALYSIS"

echo "== score =="
python3 "$SCRIPTS/score_candidates.py" --dir "$CAND" --human "$HUMAN" --out "$ANALYSIS/REJECT_PROBE.json"

KEEP_SRC=""
if [[ -f "$CAND/db-${DAY//-/}-c-full-170544.mp4" ]]; then
  KEEP_SRC="$CAND/db-${DAY//-/}-c-full-170544.mp4"
fi
# resolve KEEP from score
KEEP_SRC=$(python3 - <<PY
import json
from pathlib import Path
cand=Path("$CAND")
score=json.loads(Path("$ANALYSIS/REJECT_PROBE.json").read_text())
for r in score.get("candidates") or []:
    if str(r.get("final_verdict","")).upper()=="KEEP":
        p=cand/r["filename"]
        if p.is_file():
            print(p)
            break
PY
)

if [[ -n "$KEEP_SRC" && -f "$KEEP_SRC" ]]; then
  echo "== pride cuts from $KEEP_SRC =="
  python3 "$SCRIPTS/pride_cuts_from_keep.py" --src "$KEEP_SRC" --out-dir "$CAND/pride" --score-json "$ANALYSIS/REJECT_PROBE.json"
else
  echo "no KEEP source — skip pride"
fi

# Optional: gated chat-blur on pride cuts (passthrough if no chat — never always-on)
if [[ -d "$CAND/pride" ]] && [[ -f "$SCRIPTS/apply_chat_blur.py" ]]; then
  echo "== gated chat blur on pride (detect first) =="
  mkdir -p "$CAND/pride/gated"
  for p in "$CAND/pride"/*.mp4; do
    [[ -f "$p" ]] || continue
    bn=$(basename "$p")
    python3 "$SCRIPTS/apply_chat_blur.py" --src "$p" --out "$CAND/pride/gated/$bn" \
      --detect-out "$ANALYSIS/chat_detect_${bn%.mp4}.json" || true
  done
fi

if [[ -d "$CAND/pride" ]] && [[ -f "$SCRIPTS/pride_vertical.py" ]]; then
  echo "== pride 9:16 vertical =="
  python3 "$SCRIPTS/pride_vertical.py" --pride-dir "$CAND/pride" || true
fi

if [[ -f "$SCRIPTS/speech_peaks.py" ]]; then
  echo "== speech peaks (honest skip if ambience) =="
  python3 "$SCRIPTS/speech_peaks.py" --day-dir "$ROOT" || true
fi

if [[ -f "$SCRIPTS/audio_role_stamp.py" ]]; then
  echo "== audio role stamp (mic_cue vs talk) =="
  python3 "$SCRIPTS/audio_role_stamp.py" --day-dir "$ROOT" || true
fi

if [[ -f "$SCRIPTS/zone_label_probe.py" ]]; then
  echo "== zone label probe (Titan when visible; no invent) =="
  python3 "$SCRIPTS/zone_label_probe.py" --day-dir "$ROOT" || true
fi

echo "== review pack =="
python3 "$SCRIPTS/build_review_pack.py" --day-dir "$ROOT" --score "$ANALYSIS/REJECT_PROBE.json"

if [[ -f "$SCRIPTS/next_night_brief.py" ]]; then
  echo "== next night brief =="
  python3 "$SCRIPTS/next_night_brief.py" --day-dir "$ROOT" || true
fi

# KEEP → Moments (+ Drive) when human_verdicts has KEEP — future project library
if [[ -f "$SCRIPTS/archive_keep_to_moments.py" ]] && [[ -f "$ANALYSIS/human_verdicts.json" ]]; then
  if grep -q '"KEEP"' "$ANALYSIS/human_verdicts.json" 2>/dev/null; then
    ZONE="archive"
    # Prefer real zone probe (no invent) when present
    if [[ -f "$ANALYSIS/ZONE_LABEL.json" ]]; then
      ZONE=$(python3 - <<PY
import json
from pathlib import Path
p=Path("$ANALYSIS/ZONE_LABEL.json")
try:
    d=json.loads(p.read_text())
    z=(d.get("zone") or d.get("zone_hint") or d.get("label") or "").strip().lower()
    z="".join(c if c.isalnum() or c in "-_" else "-" for c in z).strip("-") or "archive"
    print(z[:40])
except Exception:
    print("archive")
PY
)
    fi
    echo "== archive KEEP to Moments zone=$ZONE (+ Drive if available) =="
    python3 "$SCRIPTS/archive_keep_to_moments.py" --day-dir "$ROOT" --zone "$ZONE" --drive || true
    # M10: package stub NOT_ARMED (never auto-publish)
    if [[ -f "$SCRIPTS/stitch_returner_package.py" ]]; then
      echo "== package stub NOT_ARMED =="
      python3 "$SCRIPTS/stitch_returner_package.py" --day "$DAY" || true
    fi
  fi
fi

# M5 review ready after enhance (board exists)
if [[ -f "$SCRIPTS/notify_review_ready.sh" ]]; then
  bash "$SCRIPTS/notify_review_ready.sh" "$DAY" || true
fi

# healthboard after enhance
if [[ -f "$SCRIPTS/gcs_pipeline_health.py" ]]; then
  python3 "$SCRIPTS/gcs_pipeline_health.py" || true
fi

echo "== SHORTLIST =="
cat "$ROOT/review-pack/SHORTLIST.md" 2>/dev/null || true
echo "DONE enhance_returner_day day=$DAY (no publish)"
echo "Open: $ROOT/review-pack/index.html"
echo "Or: bash $SCRIPTS/open_review_pack.sh $DAY"
echo "Pride: $CAND/pride/"
echo "Vertical: $CAND/pride/vertical/"
echo "Law: chat blur only if chat_present — see MACHINE_INTELLIGENCE_BROLL.md"
