#!/usr/bin/env python3
"""Prefill CREATOR_WEEKLY_REVIEW.md facts from disk. Kyle fills feel later. No invent publish counts."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
INDEX = WOW / "00-Index"
STORY = WOW / "04-Story-and-Capture"
DAILY = STORY / "returner-daily"
AUDIO_STAMP = STORY / "AUDIO_GREEN_STAMP.md"
OUT = INDEX / "CREATOR_WEEKLY_REVIEW.md"


def count_days() -> int:
    if not DAILY.is_dir():
        return 0
    return sum(1 for p in DAILY.iterdir() if p.is_dir() and p.name[:4].isdigit())


def audio_status() -> str:
    if not AUDIO_STAMP.is_file():
        return "no stamp file"
    parts = AUDIO_STAMP.read_text(encoding="utf-8").split("---", 2)
    fm = parts[1] if len(parts) >= 3 else ""
    if "status: GREEN" in fm:
        return "GREEN"
    return "OPEN"


def main() -> int:
    n_days = count_days()
    audio = audio_status()
    body = "\n".join(
        [
            "# Creator weekly review",
            "",
            f"**Prefill:** {datetime.now().strftime('%Y-%m-%d %H:%M')} (facts only · Kyle fills feel)",
            "",
            "| Metric | This week | Notes |",
            "|--------|-----------|-------|",
            f"| Nights played |  | Kyle |",
            f"| VO / essay minutes |  | Kyle |",
            f"| Muddy record nights |  | Kyle |",
            f"| Returner Daily day folders (total on disk) | **{n_days}** | agent prefill |",
            f"| Published (go count) | 0 unless Kyle says | never invent |",
            f"| Game audio green? | **{audio}** | AUDIO_GREEN_STAMP |",
            f"| Memento stills used |  | after FOOTAGE map |",
            f"| One listener/viewer note |  | Kyle |",
            "",
            "## Keep / kill",
            "",
            "| Keep | Kill / pause |",
            "|------|----------------|",
            "|  |  |",
            "",
            "## Next week one goal",
            "",
            "- ",
            "",
            "Related: [[CONTENT_ENGINE_20_IMPROVEMENTS]] · [[ENGINE_HEALTH_latest]] · [[STREAMER_NOW]]",
            "",
        ]
    )
    OUT.write_text(body, encoding="utf-8")
    print(f"weekly -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
