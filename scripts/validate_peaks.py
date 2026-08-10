#!/usr/bin/env python3
"""
Validate vibe-session peaks.md — empty is OK; invented-looking rows without times fail.
Exit 0 = honest empty or well-formed; 2 = bad rows.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
SESS = WOW / "04-Story-and-Capture" / "vibe-sessions"


def check_file(path: Path) -> list[str]:
    errs: list[str] = []
    if not path.is_file():
        return [f"missing {path}"]
    text = path.read_text(encoding="utf-8")
    # table rows: | t_start | t_end | tag | notes |
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip().startswith("|"):
            continue
        if re.search(r"t_start|----", line, re.I):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        t0, t1 = cells[0], cells[1]
        if not t0 and not t1:
            continue  # empty row OK
        if t0 in ("", "—", "-") and t1 in ("", "—", "-"):
            continue
        # must look like timestamp if filled
        ts = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$|^\d+(\.\d+)?s?$")
        if t0 and t0 not in ("—", "-") and not ts.match(t0):
            errs.append(f"{path.name}:{i} bad t_start {t0!r}")
        if t1 and t1 not in ("—", "-") and not ts.match(t1):
            errs.append(f"{path.name}:{i} bad t_end {t1!r}")
        # ban obvious invent words without time
        notes = cells[3] if len(cells) > 3 else ""
        if re.search(r"\b(TBD|TODO invent|fake)\b", notes, re.I):
            errs.append(f"{path.name}:{i} invent marker in notes")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    files: list[Path] = []
    if args.all and SESS.is_dir():
        files = list(SESS.glob("*/peaks.md"))
    else:
        from datetime import datetime

        day = args.day or datetime.now().strftime("%Y-%m-%d")
        files = [SESS / day / "peaks.md"]
    all_errs: list[str] = []
    for f in files:
        if not f.is_file() and not args.all:
            print(f"OK empty-missing {f} (no peaks file yet)")
            continue
        errs = check_file(f)
        if not errs:
            print(f"OK {f}")
        all_errs.extend(errs)
    for e in all_errs:
        print(f"ERR {e}", file=sys.stderr)
    return 2 if all_errs else 0


if __name__ == "__main__":
    raise SystemExit(main())
