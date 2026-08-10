#!/usr/bin/env bash
# M5: After HARVEST_OK — write REVIEW_READY + optional macOS notification.
set -euo pipefail
DAY="${1:-$(date +%F)}"
RETURNS="$HOME/Movies/WoW-Broll-Workflow/Returns"
DAY_DIR="$RETURNS/returner-daily-${DAY}"
RECEIPTS="$HOME/Library/Application Support/UAH/butler/control-plane/receipts/wow"
mkdir -p "$RECEIPTS" "$DAY_DIR"
PACK="$DAY_DIR/review-pack/index.html"
SHORT="$DAY_DIR/review-pack/SHORTLIST.md"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
NOTE="$DAY_DIR/REVIEW_READY.md"
cat > "$NOTE" <<EOF
# Review ready — $DAY
**When (UTC):** $TS
**Board:** \`$PACK\`
**Shortlist:** \`$SHORT\`
**Open:** \`bash wow-roster-tracker/scripts/open_review_pack.sh $DAY\`
**Law:** no publish · KEEP wins · ≤60s
EOF
cp "$NOTE" "$RECEIPTS/REVIEW_READY_${DAY//-/}.md"
# brief pointer
if [[ -f "$DAY_DIR/NEXT_NIGHT_BRIEF.md" ]]; then
  if ! grep -q 'REVIEW_READY' "$DAY_DIR/NEXT_NIGHT_BRIEF.md" 2>/dev/null; then
    printf '\n## Review ready\n\n- Open: `open_review_pack.sh %s`\n' "$DAY" >> "$DAY_DIR/NEXT_NIGHT_BRIEF.md"
  fi
fi
if command -v osascript >/dev/null 2>&1; then
  osascript -e "display notification \"Returner Daily $DAY shortlist ready — open_review_pack\" with title \"GCS VibeCast\"" 2>/dev/null || true
fi
echo "REVIEW_READY day=$DAY note=$NOTE"
