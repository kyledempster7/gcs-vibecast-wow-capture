#!/usr/bin/env python3
"""
Seed Returner Daily / social caption lines from scorecard "What moved".
Writes 04-Story-and-Capture/returner-daily/caption-seeds/YYYY-MM-DD.md
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
SCORE = WOW / "Characters" / "scorecards" / "latest.md"
OUT_DIR = WOW / "04-Story-and-Capture" / "returner-daily" / "caption-seeds"


def main() -> int:
    if not SCORE.is_file():
        print(f"ERROR: missing {SCORE}", file=sys.stderr)
        return 1
    text = SCORE.read_text(encoding="utf-8")
    day = datetime.now().strftime("%Y-%m-%d")
    # parse "What moved" bullets
    moved: list[str] = []
    in_moved = False
    for line in text.splitlines():
        if line.strip().startswith("## What moved"):
            in_moved = True
            continue
        if in_moved and line.startswith("##"):
            break
        if in_moved and line.strip().startswith("- "):
            moved.append(line.strip()[2:])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{day}.md"
    lines = [
        f"# Caption seeds — {day}",
        "",
        f"**Source:** `Characters/scorecards/latest.md`",
        f"**Generated:** {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## From scorecard",
        "",
    ]
    if not moved or (len(moved) == 1 and "No level/ilvl" in moved[0]):
        lines += [
            "_No level/ilvl deltas — play night still valid; use personality/Memento instead._",
            "",
            "### Soft seeds",
            "- Quiet board night — still a returner login.",
            "- Explorer energy without a ding: that counts.",
            "",
        ]
    else:
        lines.append("### Facts (true)")
        for m in moved:
            lines.append(f"- {m}")
        lines.append("")
        lines.append("### Caption drafts (pick one)")
        for m in moved:
            # light template
            lines.append(f"- Small win: {m}. Wrath brain, modern client.")
            lines.append(f"- Returner notch — {m}. Positive friction optional.")
        lines.append("")

    lines += [
        "## Do not",
        "",
        "- Invent dings not in scorecard",
        "- Auto-publish",
        "",
        "Related: [[../../social/RETURNER_DAILY_SOCIAL|Returner Daily]] · scorecards",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    latest = OUT_DIR / "latest.md"
    latest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"caption-seeds -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
