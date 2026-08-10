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
    watch_alive = False
    # Prefer lockdir/pid (atomic single-instance); fall back to classic .lock
    for lock in (
        LOGDIR / "watch_ready_harvest.lockdir" / "pid",
        LOGDIR / "watch_ready_harvest.lock",
    ):
        if not lock.is_file():
            continue
        raw = lock.read_text(encoding="utf-8").strip()
        if not raw.isdigit():
            continue
        watch_pid = raw
        try:
            import os

            os.kill(int(raw), 0)
            watch_alive = True
        except OSError:
            watch_alive = False
        break
    watch_cell = (
        f"pid `{watch_pid}` · {'alive' if watch_alive else 'stale/dead'}"
        if watch_pid
        else "pid `none`"
    )
    # Golden long-run status (agent-green durable loop)
    golden_cell = "pid `none`"
    g_status = BROLL / "GOLDEN_LONG_RUN_STATUS.json"
    g_pid = None
    g_alive = False
    g_state = ""
    for glock in (
        LOGDIR / "golden_long_run.lockdir" / "pid",
    ):
        if glock.is_file():
            raw = glock.read_text(encoding="utf-8").strip()
            if raw.isdigit():
                g_pid = raw
                try:
                    import os

                    os.kill(int(raw), 0)
                    g_alive = True
                except OSError:
                    g_alive = False
            break
    if g_status.is_file():
        try:
            gs = json.loads(g_status.read_text(encoding="utf-8"))
            g_state = str(gs.get("state") or "")
            if not g_pid and gs.get("pid"):
                g_pid = str(gs.get("pid"))
        except Exception:
            pass
    if g_pid:
        golden_cell = (
            f"pid `{g_pid}` · {'alive' if g_alive else 'stale'} · {g_state or '—'}"
        )
    # Optional OBS probe (read-only JSON from mac_probe_obs_windows)
    obs_cell = "—"
    obs_path = BROLL / "OBS_PATH_PROBE_LATEST.json"
    if obs_path.is_file():
        try:
            od = json.loads(obs_path.read_text(encoding="utf-8"))
            obs_cell = (
                f"running={od.get('obs_running')} path_ok={od.get('product_path_ok')} "
                f"tracks={od.get('rec_tracks')} today_masters={od.get('has_today_masters')}"
            )
        except Exception:
            obs_cell = "probe unreadable"
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
| Watch ready-harvest | {watch_cell} |
| Golden long run | {golden_cell} |
| OBS probe | {obs_cell} |
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
