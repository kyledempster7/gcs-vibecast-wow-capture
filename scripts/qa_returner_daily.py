#!/usr/bin/env python3
"""QA a Returner Daily day folder. Exit 0; report PASS/FAIL/SKIP."""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
ROOT = WOW / "04-Story-and-Capture" / "returner-daily"


def path_for_role(sources: str, role: str) -> str | None:
    m = re.search(rf"\|\s*{re.escape(role)}\s*\|\s*`([^`]+)`", sources, re.I)
    if not m:
        return None
    val = m.group(1).strip()
    if val in ("—", "-", "", "none", "–"):
        return None
    return val


def check_day(day_dir: Path) -> list[str]:
    rows: list[str] = []
    if not day_dir.is_dir():
        return [f"FAIL missing dir {day_dir}"]
    for name in ("README.md", "caption.md", "SOURCES.md"):
        p = day_dir / name
        rows.append(f"{'PASS' if p.is_file() else 'FAIL'} {name}")
    sources = ""
    if (day_dir / "SOURCES.md").is_file():
        sources = (day_dir / "SOURCES.md").read_text(encoding="utf-8")
    video = path_for_role(sources, "video")
    still = path_for_role(sources, "still")
    rows.append(f"{'PASS' if video else 'SKIP'} video path set" + (f" ({video})" if video else ""))
    rows.append(f"{'PASS' if still else 'SKIP'} still path set" + (f" ({still})" if still else ""))
    cap = ""
    if (day_dir / "caption.md").is_file():
        cap = (day_dir / "caption.md").read_text(encoding="utf-8")
    filled = "[one line what happened]" not in cap and len(cap.strip()) > 80
    rows.append(f"{'PASS' if filled else 'SKIP'} caption filled beyond scaffold")
    if video and still:
        rows.append("READY_FOR_HUMAN_GO draft has both paths")
    else:
        rows.append("HOLD need real media paths before publish consideration")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    args = ap.parse_args()
    day = args.day or datetime.now().strftime("%Y-%m-%d")
    day_dir = ROOT / day
    ROOT.mkdir(parents=True, exist_ok=True)
    rows = check_day(day_dir)
    out = day_dir / "QA.md" if day_dir.is_dir() else ROOT / f"QA_{day}.md"
    if day_dir.is_dir():
        body = [
            f"# Returner Daily QA — {day}",
            "",
            f"Generated {datetime.now().isoformat(timespec='seconds')}",
            "",
            *[f"- {r}" for r in rows],
            "",
            "Publish still requires **Kyle go**. PASS paths ≠ approved post.",
            "",
        ]
        out.write_text("\n".join(body), encoding="utf-8")
    else:
        out.write_text(f"# QA {day}\n\nNo day folder.\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"qa -> {out}")
    for r in rows:
        print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
