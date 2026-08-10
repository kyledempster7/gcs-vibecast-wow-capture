#!/usr/bin/env python3
"""Write a one-screen WAITING board for cold agents (no invent thrash).

Reads SOFT_POLL_LATEST + optional watch lock. No publish.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BROLL = Path.home() / "Movies/WoW-Broll-Workflow/Returns"
WOW = Path(__file__).resolve().parents[2]
INDEX = WOW / "00-Index"
RECEIPTS = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/wow"
)
LOGDIR = Path.home() / "Library/Logs/gcs-vibecast-wow"


def main() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    soft = BROLL / "SOFT_POLL_LATEST.json"
    ready_today = False
    days_lines = []
    if soft.is_file():
        d = json.loads(soft.read_text(encoding="utf-8"))
        ready_today = bool(d.get("ready_today"))
        for row in d.get("days") or []:
            days_lines.append(
                f"| {row.get('day')} | {row.get('ready')} | {row.get('reason')} | "
                f"cand={row.get('candidates_n')} raw={row.get('raw_mp4_n')} |"
            )
    watch_pid = None
    lock = LOGDIR / "watch_ready_harvest.lock"
    if lock.is_file():
        watch_pid = lock.read_text(encoding="utf-8").strip()
    state = "READY_TO_HARVEST" if ready_today else "WAITING_WINDOWS_MASTERS"
    body = f"""---
type: waiting-board
status: {state}
updated: {datetime.now().isoformat(timespec='seconds')}
day: {today}
---

# VibeCast waiting board

**State:** `{state}`  
**Law:** no invent FOOTAGE · no silent publish · ARM deny  

## Soft-poll

| Day | Ready | Reason | Counts |
|-----|-------|--------|--------|
{chr(10).join(days_lines) or '| — | — | no SOFT_POLL | — |'}

## Automation

| Piece | Status |
|-------|--------|
| Watch ready-harvest | pid `{watch_pid or 'none'}` |
| Auto Session-End | runs when **today** masters land on D: base/raw |
| LaunchAgent | active 12:00–02:59 local (quiet 03–11) |
| Gauntlet | `python3 scripts/gcs_vibecast_gauntlet.py` |

## What unblocks

1. Windows: OBS WoW B-Roll record → mp4 on `D:\\WoW B-Roll Storage`  
2. Auto or `Session-End-Ship.ps1` → candidates  
3. Mac harvest → `open_review_pack.sh`  

## Agent rule

If `WAITING_WINDOWS_MASTERS`: do **not** invent candidates. Prefer backup, gauntlet, fence, docs — or wait for watch.

Generated UTC: {datetime.now(timezone.utc).isoformat()}
"""
    INDEX.mkdir(parents=True, exist_ok=True)
    out1 = INDEX / "WAITING_BOARD.md"
    out1.write_text(body, encoding="utf-8")
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    (RECEIPTS / "WAITING_BOARD_LATEST.md").write_text(body, encoding="utf-8")
    print(f"WAITING_BOARD state={state} -> {out1}")
    return 0 if not ready_today else 0


if __name__ == "__main__":
    raise SystemExit(main())
