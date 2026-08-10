#!/usr/bin/env python3
"""
Attach real media paths to a Returner Daily day folder, then re-stitch package.

Fail-closed:
  - Paths must exist as files (or --allow-missing for Windows paths Mac cannot see)
  - Never invent basenames
  - Does not arm or publish
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
DAILY = WOW / "04-Story-and-Capture" / "returner-daily"


def update_sources(day_dir: Path, video: str | None, still: str | None, note: str) -> None:
    path = day_dir / "SOURCES.md"
    if path.is_file():
        text = path.read_text(encoding="utf-8")
    else:
        text = f"# Sources — {day_dir.name}\n\n| Role | Path |\n|------|------|\n| video | `—` |\n| still | `—` |\n"

    def set_role(t: str, role: str, val: str) -> str:
        # Manual replace — re.sub replacement treats \U \1 etc as escapes (Windows paths break)
        pat = re.compile(rf"(\|\s*{role}\s*\|\s*`)([^`]*)(`)", re.I)
        m = pat.search(t)
        if m:
            return t[: m.start()] + m.group(1) + val + m.group(3) + t[m.end() :]
        return t + f"\n| {role} | `{val}` |\n"

    if video:
        text = set_role(text, "video", video)
    if still:
        text = set_role(text, "still", still)
    if note:
        if "**Note:**" in text:
            text = re.sub(r"\*\*Note:\*\*.*", f"**Note:** {note}", text, count=1)
        else:
            text = text.replace(
                f"# Sources — {day_dir.name}",
                f"# Sources — {day_dir.name}\n\n**Note:** {note}",
                1,
            )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Attach real media to Returner Daily day")
    ap.add_argument("--day", default=None)
    ap.add_argument("--video", default=None)
    ap.add_argument("--still", default=None)
    ap.add_argument("--note", default="")
    ap.add_argument(
        "--allow-missing",
        action="store_true",
        help="Allow Windows paths that are not visible on this Mac",
    )
    ap.add_argument("--no-stitch", action="store_true")
    args = ap.parse_args()

    day = args.day or datetime.now().strftime("%Y-%m-%d")
    day_dir = DAILY / day
    if not day_dir.is_dir():
        print(f"ERROR: missing day folder {day_dir} — run draft_returner_daily first", file=sys.stderr)
        return 1
    if not args.video and not args.still:
        print("ERROR: pass --video and/or --still", file=sys.stderr)
        return 2

    for label, p in (("video", args.video), ("still", args.still)):
        if not p:
            continue
        fp = Path(p)
        if not args.allow_missing and not fp.is_file():
            # Windows-style paths often invisible on Mac
            if re.match(r"^[A-Za-z]:\\", p) or p.startswith("\\\\"):
                print(
                    f"WARN: {label} looks like Windows path not visible here; "
                    f"re-run with --allow-missing if intentional: {p}"
                )
                print("ERROR: refusing missing path without --allow-missing", file=sys.stderr)
                return 3
            print(f"ERROR: {label} not a file: {p}", file=sys.stderr)
            return 3

    update_sources(day_dir, args.video, args.still, args.note or "attach_media_to_day")
    print(f"updated SOURCES -> {day_dir / 'SOURCES.md'}")

    if not args.no_stitch:
        r = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).parent / "stitch_returner_package.py"),
                "--day",
                day,
            ],
            check=False,
        )
        return r.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
