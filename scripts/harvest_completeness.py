#!/usr/bin/env python3
"""Compare Windows qualified candidates vs Mac landed mp4 for one day.

Exit: 0 complete · 1 incomplete · 2 unknown
No invent. No publish. Does not create media.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RETURNS = Path.home() / "Movies" / "WoW-Broll-Workflow" / "Returns"
LATEST = RETURNS / "SOFT_POLL_LATEST.json"
LIVE = RETURNS / "LIVE.json"


def mac_mp4_n(day: str) -> int:
    cand = RETURNS / f"returner-daily-{day}" / "candidates"
    if not cand.is_dir():
        return 0
    return sum(1 for p in cand.glob("*.mp4") if p.is_file())


def windows_cand_n(day: str) -> int | None:
    if not LATEST.is_file():
        return None
    try:
        data = json.loads(LATEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    for row in data.get("days") or []:
        if row.get("day") == day:
            for key in ("candidates_qualified_n", "candidates_n"):
                if row.get(key) is not None:
                    try:
                        return int(row[key])
                    except (TypeError, ValueError):
                        return None
    return None


def review_pack_ok(day: str) -> bool:
    pack = RETURNS / f"returner-daily-{day}" / "review-pack"
    return (pack / "index.html").is_file() and (pack / "SHORTLIST.md").is_file()


def armed(day: str) -> bool:
    di = (
        Path.home()
        / "Library"
        / "Application Support"
        / "UAH"
        / "butler"
        / "control-plane"
        / "delivery-independence"
        / "packages"
    )
    if not di.is_dir():
        return False
    for p in di.glob(f"*{day}*"):
        name = p.name.upper()
        if "NOT_ARMED" in name:
            continue
        if name.endswith(".ARMED.JSON") or ".ARMED." in name:
            return True
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("may_publish") is True:
            return True
        if str(data.get("status") or "").upper() == "ARMED":
            return True
    return False


def completeness(day: str) -> tuple[str, int, int | None]:
    mac_n = mac_mp4_n(day)
    win_n = windows_cand_n(day)
    if win_n is None:
        return "unknown", mac_n, win_n
    if mac_n >= win_n and mac_n > 0:
        return "complete", mac_n, win_n
    return "incomplete", mac_n, win_n


def write_live(day: str) -> Path:
    status, mac_n, win_n = completeness(day)
    payload = {
        "schema": "gcs_vibecast_live/v1",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "day": day,
        "mac_mp4_n": mac_n,
        "windows_cand_n": win_n,
        "harvest_complete": status == "complete",
        "harvest_status": status,
        "review_pack": review_pack_ok(day),
        "armed": armed(day),
        "movies_day_dir": str(RETURNS / f"returner-daily-{day}"),
        "law": "no invent FOOTAGE · no silent publish · boards read this file",
    }
    LIVE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return LIVE


def main() -> int:
    ap = argparse.ArgumentParser(description="Harvest completeness vs Windows poll")
    ap.add_argument("--day", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--write-live", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    status, mac_n, win_n = completeness(args.day)
    if args.write_live:
        write_live(args.day)
    if not args.quiet:
        print(
            f"harvest_completeness day={args.day} status={status} "
            f"mac_mp4_n={mac_n} windows_cand_n={win_n}"
        )
    if status == "complete":
        return 0
    if status == "incomplete":
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
