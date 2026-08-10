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
# Codex P0-4: heartbeat TTL (seconds). Beyond this, report stalled even if pid lives.
WATCH_HB_TTL_S = 600  # watch soft_poll every ~120s; 10m stall is real
GOLDEN_HB_TTL_S = 900  # golden tick ~3m; 15m stall is real


def pid_cmd_match(pid: str, needle: str) -> bool:
    """Alive only if kill(0) OK *and* command line still matches needle (Codex gap 30/95)."""
    import os
    import subprocess

    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError):
        return False
    try:
        out = subprocess.check_output(
            ["ps", "-p", str(pid), "-o", "command="],
            text=True,
            errors="replace",
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return needle in out


def file_age_s(path: Path) -> int | None:
    try:
        return int(datetime.now().timestamp() - path.stat().st_mtime)
    except OSError:
        return None


def hb_label(age: int | None, ttl: int) -> str:
    if age is None:
        return "hb=missing"
    if age > ttl:
        return f"hb={age}s STALLED(>{ttl}s)"
    return f"hb={age}s ok"


def main() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    soft = BROLL / "SOFT_POLL_LATEST.json"
    ready_today = False
    days_lines = []
    soft_age = "no file"
    if soft.is_file():
        age_s = file_age_s(soft)
        soft_age = f"{age_s}s" if age_s is not None else "?"
        d = json.loads(soft.read_text(encoding="utf-8"))
        ready_today = bool(d.get("ready_today"))
        for row in d.get("days") or []:
            days_lines.append(
                f"| {row.get('day')} | {row.get('ready')} | {row.get('reason')} | "
                f"cand={row.get('candidates_n')} raw={row.get('raw_mp4_n')} |"
            )
    watch_pid = None
    watch_alive = False
    watch_day = ""
    watch_lockdir = LOGDIR / "watch_ready_harvest.lockdir"
    # Prefer lockdir/pid (atomic single-instance); fall back to classic .lock
    for lock in (
        watch_lockdir / "pid",
        LOGDIR / "watch_ready_harvest.lock",
    ):
        if not lock.is_file():
            continue
        raw = lock.read_text(encoding="utf-8").strip()
        if not raw.isdigit():
            continue
        watch_pid = raw
        watch_alive = pid_cmd_match(raw, "watch_ready_harvest_once.sh")
        break
    day_f = watch_lockdir / "day"
    if day_f.is_file():
        watch_day = day_f.read_text(encoding="utf-8").strip()
    # Heartbeat: lockdir/heartbeat preferred; else detail log mtime
    whb = file_age_s(watch_lockdir / "heartbeat")
    if whb is None:
        whb = file_age_s(LOGDIR / "watch_ready_harvest.log")
    whb_s = hb_label(whb, WATCH_HB_TTL_S)
    if watch_alive and whb is not None and whb > WATCH_HB_TTL_S:
        watch_status = f"cmd_ok but {whb_s}"
    elif watch_alive:
        watch_status = f"cmd_ok · {whb_s}"
    else:
        watch_status = "stale/dead/mismatch"
    day_note = f" · day={watch_day}" if watch_day else ""
    if watch_day and watch_day != today:
        day_note += " DAY_MISMATCH"
    watch_cell = (
        f"pid `{watch_pid}` · {watch_status}{day_note}"
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
                g_alive = pid_cmd_match(raw, "golden_long_run.sh")
            break
    ghb = file_age_s(g_status)
    if g_status.is_file():
        try:
            gs = json.loads(g_status.read_text(encoding="utf-8"))
            g_state = str(gs.get("state") or "")
            if not g_pid and gs.get("pid"):
                g_pid = str(gs.get("pid"))
                g_alive = pid_cmd_match(g_pid, "golden_long_run.sh")
        except Exception:
            pass
    ghb_s = hb_label(ghb, GOLDEN_HB_TTL_S)
    if g_pid:
        if g_alive and ghb is not None and ghb > GOLDEN_HB_TTL_S:
            g_status_s = f"cmd_ok but {ghb_s}"
        elif g_alive:
            g_status_s = f"cmd_ok · {ghb_s}"
        else:
            g_status_s = "stale/mismatch"
        golden_cell = f"pid `{g_pid}` · {g_status_s} · {g_state or '—'}"
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
| LaunchAgent | interval loaded · quiet 03–11 · **defers soft_poll if golden owns cadence** |
| Soft-poll freshness | age `{soft_age}` (do not treat board as product-green) |
| Gauntlet | `python3 scripts/gcs_vibecast_gauntlet.py` (~29 checks — not 100 behavioral) |
| Verdict | RUNTIME_PARTIAL_E2E_UNPROVEN until serialize + same-day masters path |

## What unblocks (honest)

1. Agent P0 residual: serialize export/harvest gates (not “play alone”) — [[RELIABILITY_RESIDUAL_SERIALIZE_20260810]]  
2. Windows: OBS Record → stop → Session-End with recording-stopped/stable-size  
3. Mac harvest → KEEP → draft NOT_ARMED  

## Agent rule

If `WAITING_WINDOWS_MASTERS`: do **not** invent candidates. agent-green waiting ≠ PRODUCT_GREEN. Prefer reliability residual, fence, backup — not dual thrash.

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
