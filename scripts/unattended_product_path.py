#!/usr/bin/env python3
"""One autonomous GCS VibeCast product-path run — no chat proceed thrash.

Branch A (ready_today): harvest_if_ready only (harvest_mac already enhance+review).
Branch B (not ready): ensure golden+watch single, refresh board, write ONE
BLOCKED_ON_MASTERS_ARMED receipt, exit 0 (legal wait).

Laws: no invent FOOTAGE · no re-harvest residual day as today · no silent ARM/publish.
Codex eval 20260810: no duplicate enhance/review; day-bind + freshness on poll.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
RETURNS = Path.home() / "Movies/WoW-Broll-Workflow/Returns"
SOFT_POLL = RETURNS / "SOFT_POLL_LATEST.json"
GOLDEN = RETURNS / "GOLDEN_LONG_RUN_STATUS.json"
CP_RECEIPTS = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast"
)
WOW_RECEIPTS = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/wow"
)
# Soft poll older than this is fail-closed (do not admit Branch A from stale JSON).
SOFT_POLL_MAX_AGE_S = 600


def poll_age_seconds(path: Path = SOFT_POLL) -> int | None:
    try:
        return int(datetime.now().timestamp() - path.stat().st_mtime)
    except OSError:
        return None


def poll_is_fresh(path: Path = SOFT_POLL, max_age_s: int = SOFT_POLL_MAX_AGE_S) -> bool:
    age = poll_age_seconds(path)
    return age is not None and age <= max_age_s


def ready_today_from_poll(
    data: dict[str, Any],
    day: str,
    *,
    require_fresh: bool = False,
    poll_path: Path = SOFT_POLL,
    max_age_s: int = SOFT_POLL_MAX_AGE_S,
) -> bool:
    """Admit only when the *requested day row* is ready.

    Top-level ready_today alone is insufficient (day-bind). When require_fresh,
    SOFT_POLL file mtime must be within max_age_s.
    """
    if require_fresh and not poll_is_fresh(poll_path, max_age_s=max_age_s):
        return False
    row = today_row(data, day)
    if not row:
        return False
    row_ready = bool(row.get("ready"))
    # If top-level present, it must agree with the day row (stale top-level lie → deny).
    if "ready_today" in data and data["ready_today"] is not None:
        top = bool(data["ready_today"])
        if top != row_ready:
            return False
        return top and row_ready
    return row_ready


def today_row(data: dict[str, Any], day: str) -> dict[str, Any]:
    for row in data.get("days") or []:
        if row.get("day") == day:
            return dict(row)
    return {}


def decide_branch(
    data: dict[str, Any],
    day: str,
    *,
    require_fresh: bool = False,
    poll_path: Path = SOFT_POLL,
) -> str:
    """A = product harvest chain; B = armed wait. Never harvest residual-as-today."""
    return (
        "A"
        if ready_today_from_poll(
            data, day, require_fresh=require_fresh, poll_path=poll_path
        )
        else "B"
    )


def residual_ready_non_today(data: dict[str, Any], day: str) -> list[str]:
    """Days that are ready but are NOT today (must not be harvested as today)."""
    out: list[str] = []
    for row in data.get("days") or []:
        d = row.get("day")
        if d and d != day and row.get("ready"):
            out.append(str(d))
    return out


def branch_a_steps() -> list[str]:
    """Canonical Branch A command order (no duplicate enhance/review).

    harvest_if_ready → harvest_mac → enhance_returner_day → build_review_pack.
    Unattended driver only invokes harvest_if_ready; post-check verifies pack.
    """
    return ["harvest_if_ready.sh"]


def run_cmd(argv: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    e = os.environ.copy()
    if env:
        e.update(env)
    return subprocess.run(
        argv,
        cwd=str(SCRIPTS),
        capture_output=True,
        text=True,
        check=False,
        env=e,
    )


def write_terminal_receipt(
    *,
    branch: str,
    day: str,
    ready_today: bool,
    soft: dict[str, Any],
    golden: dict[str, Any] | None,
    harvest_rc: int | None,
    note: str,
    extra: dict[str, Any] | None = None,
) -> Path:
    CP_RECEIPTS.mkdir(parents=True, exist_ok=True)
    WOW_RECEIPTS.mkdir(parents=True, exist_ok=True)
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    status = (
        "PRODUCT_PROGRESS"
        if branch == "A" and harvest_rc == 0
        else "BLOCKED_ON_MASTERS_ARMED"
        if branch == "B"
        else "PRODUCT_ATTEMPTED"
    )
    body: dict[str, Any] = {
        "schema": "gcs_unattended_product_path/v1",
        "status": status,
        "branch": branch,
        "day": day,
        "utc": utc,
        "ready_today": ready_today,
        "ready_any": soft.get("ready_any"),
        "today_reason": today_row(soft, day).get("reason"),
        "today_raw_mp4_n": today_row(soft, day).get("raw_mp4_n"),
        "today_candidates_n": today_row(soft, day).get("candidates_n"),
        "residual_ready_non_today": residual_ready_non_today(soft, day),
        "golden_pid": (golden or {}).get("pid"),
        "watch_pid": (golden or {}).get("watch_pid"),
        "golden_state": (golden or {}).get("state"),
        "harvest_rc": harvest_rc,
        "branch_a_steps": branch_a_steps(),
        "note": note,
        "law": (
            "no invent FOOTAGE; no residual-as-today; no silent ARM/publish; "
            "further chat check-ins not required for wait cadence (golden+watch own it)"
        ),
        "checkins_required": False,
    }
    if extra:
        body.update(extra)
    path = CP_RECEIPTS / f"UNATTENDED_PRODUCT_PATH_{stamp}_{status}.json"
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    latest = CP_RECEIPTS / "UNATTENDED_PRODUCT_PATH_LATEST.json"
    latest.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    md = CP_RECEIPTS / f"UNATTENDED_PRODUCT_PATH_{stamp}_{status}.md"
    md.write_text(
        f"# {status}\n"
        f"**branch:** {branch} · **day:** {day} · **utc:** {utc}\n"
        f"**ready_today:** {ready_today} · **harvest_rc:** {harvest_rc}\n"
        f"**golden_pid:** {body['golden_pid']} · **watch_pid:** {body['watch_pid']}\n"
        f"**checkins_required:** false — wait cadence is golden+watch, not chat proceed thrash\n"
        f"**note:** {note}\n",
        encoding="utf-8",
    )
    wow_latest = WOW_RECEIPTS / "UNATTENDED_PRODUCT_PATH_LATEST.json"
    wow_latest.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return path


def pulse(day: str) -> tuple[dict[str, Any], dict[str, int]]:
    """One soft_poll + ensure golden + ensure watch. No thrash loop.

    Returns (soft_poll_data, rcs). soft_poll non-zero does not invent READY.
    """
    rcs: dict[str, int] = {}
    rcs["soft_poll"] = run_cmd(["bash", str(SCRIPTS / "soft_poll_windows.sh")]).returncode
    rcs["obs"] = run_cmd(["bash", str(SCRIPTS / "mac_probe_obs_windows.sh")]).returncode
    rcs["golden"] = run_cmd(
        ["bash", str(SCRIPTS / "ensure_golden_long_run.sh"), day]
    ).returncode
    rcs["watch"] = run_cmd(
        ["bash", str(SCRIPTS / "ensure_single_watch.sh"), day]
    ).returncode
    if not SOFT_POLL.is_file():
        return {}, rcs
    try:
        data = json.loads(SOFT_POLL.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}, rcs
    return data, rcs


def load_golden() -> dict[str, Any]:
    if not GOLDEN.is_file():
        return {}
    try:
        return json.loads(GOLDEN.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def review_pack_present(day: str) -> bool:
    """True if harvest/enhance left a review artifact for the day (no invent)."""
    day_dir = RETURNS / f"returner-daily-{day}"
    if not day_dir.is_dir():
        alt = RETURNS / day
        day_dir = alt if alt.is_dir() else day_dir
    markers = [
        day_dir / "analysis" / "review_pack.html",
        day_dir / "analysis" / "REVIEW_PACK.html",
        day_dir / "review_pack" / "index.html",
        day_dir / "analysis" / "REJECT_PROBE.json",
    ]
    return any(p.is_file() for p in markers)


def branch_a_harvest_chain(day: str) -> tuple[int, dict[str, Any]]:
    """Harvest admit only — no second enhance/review (Codex I fix).

    harvest_mac already runs enhance_returner_day + build_review_pack.
    We only re-run enhance if harvest ok AND candidates exist AND pack missing.
    """
    meta: dict[str, Any] = {
        "branch_a_steps": branch_a_steps(),
        "duplicate_enhance": False,
        "enhance_rc": None,
        "review_pack_present": False,
    }
    r = run_cmd(
        ["bash", str(SCRIPTS / "harvest_if_ready.sh"), day],
        env={"HARVEST_FORCE_POLL": "0"},
    )
    print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, end="", file=sys.stderr)
    hrc = r.returncode
    meta["harvest_stdout_tail"] = (r.stdout or "")[-400:]
    if hrc != 0:
        return hrc, meta

    day_dir = RETURNS / f"returner-daily-{day}"
    cand = day_dir / "candidates"
    has_media = cand.is_dir() and any(cand.glob("*.mp4"))
    pack_ok = review_pack_present(day)
    meta["review_pack_present"] = pack_ok
    meta["has_same_day_media"] = has_media

    if has_media and not pack_ok:
        # Repair only: harvest claimed success but enhance/review missing
        e = run_cmd(["bash", str(SCRIPTS / "enhance_returner_day.sh"), day])
        print(e.stdout, end="")
        meta["enhance_rc"] = e.returncode
        meta["duplicate_enhance"] = False
        meta["repair_enhance"] = True
        if e.returncode != 0:
            return e.returncode, meta
        meta["review_pack_present"] = review_pack_present(day)
    elif has_media and pack_ok:
        print("BRANCH_A pack already present after harvest_if_ready — skip re-enhance")
        meta["skip_re_enhance"] = True
    return hrc, meta


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    day = args[0] if args else datetime.now().strftime("%Y-%m-%d")
    fence = run_cmd([sys.executable, str(SCRIPTS / "assert_vibecast_write_fence.py")])
    if fence.returncode != 0:
        print(fence.stdout + fence.stderr, file=sys.stderr)
        print("FAIL fence", file=sys.stderr)
        return 2

    soft, pulse_rcs = pulse(day)
    if not soft:
        print("FAIL no SOFT_POLL_LATEST after pulse", file=sys.stderr)
        return 2
    print(f"PULSE_RCS {pulse_rcs}")

    # Day-bound + freshness for live admission
    rt = ready_today_from_poll(soft, day, require_fresh=True)
    branch = "A" if rt else "B"
    age = poll_age_seconds()
    print(
        f"UNATTENDED branch={branch} day={day} ready_today={rt} "
        f"poll_age_s={age} row={today_row(soft, day).get('reason')}"
    )

    if not rt and residual_ready_non_today(soft, day):
        print(
            f"FAIL_CLOSED residual_ready_non_today={residual_ready_non_today(soft, day)} "
            "— will NOT harvest as today"
        )

    harvest_rc: int | None = None
    if branch == "A":
        harvest_rc, a_meta = branch_a_harvest_chain(day)
        golden = load_golden()
        run_cmd([sys.executable, str(SCRIPTS / "write_waiting_board.py")])
        path = write_terminal_receipt(
            branch="A",
            day=day,
            ready_today=True,
            soft=soft,
            golden=golden,
            harvest_rc=harvest_rc,
            note="ready_today harvest_if_ready only (no duplicate enhance); no silent ARM",
            extra={"branch_a_meta": a_meta, "pulse_rcs": pulse_rcs, "poll_age_s": age},
        )
        print(f"RECEIPT {path} harvest_rc={harvest_rc} a_meta={a_meta}")
        # Codex: harvest rc=1 is not-ready / admit fail — never convert to overall 0
        # on Branch A. Only harvest_rc==0 is PRODUCT_PROGRESS success exit.
        if harvest_rc == 0:
            return 0
        return harvest_rc if harvest_rc is not None else 2

    # Branch B: prove harvest SKIP, one armed receipt
    h = run_cmd(
        ["bash", str(SCRIPTS / "harvest_if_ready.sh"), day],
        env={"HARVEST_FORCE_POLL": "0"},
    )
    print(h.stdout, end="")
    harvest_rc = h.returncode
    if harvest_rc not in (0, 1):
        print(f"WARN unexpected harvest_rc={harvest_rc}", file=sys.stderr)
    if harvest_rc == 0 and "already harvested" not in (h.stdout + h.stderr).lower():
        if "not READY" not in h.stdout and "SKIP" not in h.stdout:
            print("FAIL harvested without ready_today", file=sys.stderr)
            return 2
    run_cmd([sys.executable, str(SCRIPTS / "write_waiting_board.py")])
    golden = load_golden()
    path = write_terminal_receipt(
        branch="B",
        day=day,
        ready_today=False,
        soft=soft,
        golden=golden,
        harvest_rc=harvest_rc,
        note=(
            f"BLOCKED_ON_MASTERS_ARMED; harvest_rc={harvest_rc}; "
            "checkins_required=false; golden+watch own wait cadence"
        ),
        extra={"pulse_rcs": pulse_rcs, "poll_age_s": age},
    )
    print(f"RECEIPT {path} status=BLOCKED_ON_MASTERS_ARMED harvest_rc={harvest_rc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
