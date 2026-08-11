#!/usr/bin/env python3
"""Decide whether an operator pulse may reuse a fresh non-ready soft poll."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def decide(path: Path, day: str, max_age_s: int = 90, now: float | None = None) -> str:
    if not path.is_file():
        return "POLL"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "POLL"
    age = (time.time() if now is None else now) - path.stat().st_mtime
    row = next(
        (
            item
            for item in data.get("days") or []
            if isinstance(item, dict) and item.get("day") == day
        ),
        None,
    )
    ready = bool(row.get("ready")) if row is not None else bool(data.get("ready_today"))
    if ready or row is None:
        return "POLL"
    return "SKIP" if 0 <= age < max_age_s else "POLL"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--latest", type=Path, required=True)
    ap.add_argument("--day", required=True)
    ap.add_argument("--max-age", type=int, default=90)
    args = ap.parse_args()
    print(decide(args.latest, args.day, args.max_age))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
