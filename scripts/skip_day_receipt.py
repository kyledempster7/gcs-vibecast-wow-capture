#!/usr/bin/env python3
"""
Honest skip / empty-night receipt (initiative 45).

When video+still empty: write SKIP_DAY.md so agents never fake product green.
Does not invent media. Does not close K*. Exit 0 always if receipt written.
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
DAILY = WOW / "04-Story-and-Capture" / "returner-daily"


def path_for_role(sources: str, role: str) -> str | None:
    m = re.search(rf"\|\s*{re.escape(role)}\s*\|\s*`([^`]+)`", sources, re.I)
    if not m:
        return None
    val = m.group(1).strip()
    if val in ("—", "-", "", "none", "–"):
        return None
    return val


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    ap.add_argument("--reason", default="no real media paths yet")
    ap.add_argument("--force", action="store_true", help="write even if media present")
    args = ap.parse_args()
    day = args.day or datetime.now().strftime("%Y-%m-%d")
    day_dir = DAILY / day
    day_dir.mkdir(parents=True, exist_ok=True)

    video = still = None
    if (day_dir / "SOURCES.md").is_file():
        src = (day_dir / "SOURCES.md").read_text(encoding="utf-8")
        video = path_for_role(src, "video")
        still = path_for_role(src, "still")

    has_media = bool(video or still)
    if has_media and not args.force:
        print(f"skip_day: media present day={day} video={bool(video)} still={bool(still)} — no SKIP receipt")
        # clear stale skip if media arrived
        stale = day_dir / "SKIP_DAY.md"
        if stale.is_file():
            stale.unlink()
            print(f"removed stale {stale}")
        return 0

    body = [
        f"# Skip / empty night — {day}",
        "",
        f"**Status:** HONEST_EMPTY",
        f"**Reason:** {args.reason}",
        f"**When:** {datetime.now().isoformat(timespec='seconds')}",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| video | `{video or '—'}` |",
        f"| still | `{still or '—'}` |",
        f"| package product_ready | false |",
        "",
        "## Rules",
        "",
        "- This is **not** a failed system — it is an empty content night.",
        "- Do **not** invent FOOTAGE or peaks timestamps to fill this.",
        "- Do **not** arm or publish.",
        "- Close K2 only when real path + session proof exist.",
        "",
        "Related: [[GAPS_AND_NEXT_LEVEL]] · attach via `attach_media_to_day.py` after play.",
        "",
    ]
    out = day_dir / "SKIP_DAY.md"
    out.write_text("\n".join(body), encoding="utf-8")
    print(f"skip_day -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
