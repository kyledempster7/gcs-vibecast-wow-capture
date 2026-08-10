#!/usr/bin/env bash
# Mac one-shot after Windows harvest: stage → scp → score → pride → review-pack.
# NEVER publishes. Usage: bash harvest_mac.sh [YYYY-MM-DD]
# Law: PowerShell $vars must live in .ps1 files (bash eats $ inside double-quoted ssh).
set -euo pipefail
DAY="${1:-$(date +%F)}"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
HOST="${WINDOWS_SSH_HOST:-kyled@100.92.159.73}"

if [[ -d "${HOME}/Movies/WoW-Broll-Workflow/Returns/returner-daily-${DAY}" ]]; then
  ROOT="${HOME}/Movies/WoW-Broll-Workflow/Returns/returner-daily-${DAY}"
else
  ROOT="${HOME}/Movies/WoW-Broll-Workflow/Returns/returner-daily-${DAY}"
  mkdir -p "$ROOT/candidates" "$ROOT/analysis"
fi
CAND="${ROOT}/candidates"
ANALYSIS="${ROOT}/analysis"
WIN_STAGE="C:/Users/kyled/AppData/Local/Temp/gcs_cand_${DAY}"
DRIVE="${HOME}/Library/CloudStorage/GoogleDrive-kyledempster7@gmail.com/My Drive/GCS-VibeCast-Offload/${DAY}"
REMOTE_SCRIPTS="D:/WoW B-Roll Storage/_scripts"

mkdir -p "$CAND" "$ANALYSIS" "${ROOT}/markers"

echo "== harvest_mac day=$DAY =="
echo "== deploy stage script =="
ssh -o BatchMode=yes -o ConnectTimeout=20 "$HOST" \
  "powershell -NoProfile -Command \"New-Item -ItemType Directory -Force -Path 'D:\\WoW B-Roll Storage\\_scripts' | Out-Null\"" \
  || echo "SSH mkdir soft-fail"
# Dual-SoT: full ship set (not only stage/soft_poll)
if [[ -x "$SCRIPTS/deploy_windows_scripts.sh" ]] || [[ -f "$SCRIPTS/deploy_windows_scripts.sh" ]]; then
  bash "$SCRIPTS/deploy_windows_scripts.sh" || echo "deploy_windows_scripts soft-fail"
else
  scp -o BatchMode=yes -o ConnectTimeout=30 \
    "$SCRIPTS/Stage-ShipCandidates.ps1" \
    "$SCRIPTS/soft_poll_windows.ps1" \
    "$SCRIPTS/Append-StreamDeckMarker.ps1" \
    "$SCRIPTS/Export-ShipCandidates.ps1" \
    "${HOST}:${REMOTE_SCRIPTS}/" || echo "scp scripts soft-fail"
fi

echo "== stage check + stage for scp =="
ssh -o BatchMode=yes -o ConnectTimeout=60 "$HOST" \
  "powershell -NoProfile -ExecutionPolicy Bypass -File \"D:\\WoW B-Roll Storage\\_scripts\\Stage-ShipCandidates.ps1\" -Day ${DAY}" \
  || echo "SSH stage fail — will try Drive"

echo "== scp candidates =="
# Never local-glob remote paths (host:path/* expands on Mac → empty/fail).
# Use scp -r of directory contents with a quoted remote path (forward-slash Windows form).
SCP_CAND_LOG="${ANALYSIS}/SCP_CANDIDATES.log"
if scp -o BatchMode=yes -o ConnectTimeout=300 -r "${HOST}:${WIN_STAGE}/." "$CAND/" \
  >"$SCP_CAND_LOG" 2>&1; then
  echo "scp candidates ok"
else
  echo "scp candidates failed — Drive fallback (log $SCP_CAND_LOG)"
  if [[ -d "$DRIVE/candidates" ]]; then
    cp -f "$DRIVE/candidates/"* "$CAND/" 2>/dev/null || true
    [[ -f "$DRIVE/MANIFEST.json" ]] && cp -f "$DRIVE/MANIFEST.json" "$CAND/"
  fi
fi
# markers if staged (same no-local-glob rule)
if scp -o BatchMode=yes -o ConnectTimeout=30 -r "${HOST}:${WIN_STAGE}/markers/." "${ROOT}/markers/" \
  >>"$SCP_CAND_LOG" 2>&1; then
  echo "scp markers ok"
else
  if scp -o BatchMode=yes -o ConnectTimeout=30 -r \
    "${HOST}:D:/WoW B-Roll Storage/${DAY}/markers/." "${ROOT}/markers/" \
    >>"$SCP_CAND_LOG" 2>&1; then
    echo "scp markers direct ok"
  else
    echo "no markers on Mac yet"
  fi
fi

n=$(ls "$CAND"/*.mp4 2>/dev/null | wc -l | tr -d ' ')
echo "candidates_mp4=$n"
if [[ "$n" -eq 0 ]]; then
  echo "EMPTY — Windows harvest not ready yet. Re-run when staged."
  exit 2
fi

# human verdicts optional
HUMAN="$ANALYSIS/human_verdicts.json"
[[ -f "$HUMAN" ]] || echo '{}' > "$HUMAN"

echo "== enhance =="
bash "$SCRIPTS/enhance_returner_day.sh" "$DAY" || {
  python3 "$SCRIPTS/score_candidates.py" --dir "$CAND" --human "$HUMAN" --out "$ANALYSIS/REJECT_PROBE.json" || true
  python3 "$SCRIPTS/build_review_pack.py" --day-dir "$ROOT" --score "$ANALYSIS/REJECT_PROBE.json" || true
}

# motion tags on all candidates (tag only)
echo "== motion tags =="
python3 "$SCRIPTS/tag_motion_shot.py" --dir "$CAND" --out "$ANALYSIS/MOTION_TAGS.json" || true

# join markers if present
if [[ -f "${ROOT}/markers/SESSION.jsonl" ]]; then
  echo "== join markers =="
  python3 "$SCRIPTS/join_markers.py" \
    --markers "${ROOT}/markers/SESSION.jsonl" \
    --out "$ANALYSIS/MARKER_JOIN.json" || true
fi

echo "== done harvest_mac =="
echo "Review: $ROOT/review-pack/index.html"
echo "Pride:  $CAND/pride/"
echo "Motion: $ANALYSIS/MOTION_TAGS.json"
echo "NO PUBLISH"
