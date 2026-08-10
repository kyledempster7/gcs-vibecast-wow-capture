#!/usr/bin/env python3
"""One green/red healthboard: Windows · audio · markers · candidates · arm. No publish."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
WOW = SCRIPTS.parents[1]
INDEX = WOW / "00-Index"
STORY = WOW / "04-Story-and-Capture"
BROLL = Path.home() / "Movies" / "WoW-Broll-Workflow" / "Returns"
AUDIO = STORY / "AUDIO_GREEN_STAMP.md"
DI = (
    Path.home()
    / "Library"
    / "Application Support"
    / "UAH"
    / "butler"
    / "control-plane"
    / "delivery-independence"
)


def latest_return() -> Path | None:
    """Prefer newest returner day that has candidates/*.mp4; else newest folder."""
    if not BROLL.is_dir():
        return None
    days = sorted(
        [p for p in BROLL.iterdir() if p.is_dir() and "returner" in p.name],
        key=lambda p: p.name,
        reverse=True,
    )
    for d in days:
        cand = d / "candidates"
        if cand.is_dir() and any(cand.glob("*.mp4")):
            return d
    return days[0] if days else None


def win_online() -> tuple[str, str]:
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "windows_reachability.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    data = None
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if line.startswith("{") and "verdict" in line:
            try:
                data = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
    if not data:
        return "🔴", "reachability parse fail"
    verdict = str(data.get("verdict") or "")
    # ONLINE_SSH = full SCH-readable; ONLINE_TS = Tailscale only (tasks unproven)
    if verdict == "ONLINE_SSH":
        return "🟢", f"verdict={verdict}"
    if verdict.startswith("ONLINE"):
        return "🟡", f"verdict={verdict} (TS ok; SCH unproven until ONLINE_SSH)"
    return "🔴", f"verdict={verdict}"


def audio() -> tuple[str, str]:
    if not AUDIO.is_file():
        return "🔴", "missing AUDIO_GREEN_STAMP"
    t = AUDIO.read_text(encoding="utf-8")
    # Frontmatter first --- block only (avoid body mentions)
    parts = t.split("---", 2)
    fm = parts[1] if len(parts) >= 3 else t[:200]
    if "status: GREEN" in fm:
        return "🟢", "GREEN stamp"
    if "status: OPEN" in fm:
        return "🟡", "OPEN (not GREEN)"
    return "🟡", "stamp present, status unclear"


def day_signals(day: Path | None) -> dict:
    if not day:
        return {
            "markers": "🔴 none",
            "candidates": "🔴 none",
            "vertical": "🔴",
            "speech": "—",
            "shortlist": "🔴",
            "day": "none",
            "fresh_icon": "🔴",
            "fresh_note": "no return day",
        }
    markers = day / "markers" / "SESSION.jsonl"
    cand = day / "candidates"
    n_mp4 = len(list(cand.glob("*.mp4"))) if cand.is_dir() else 0
    vert = day / "candidates" / "pride" / "vertical"
    n_vert = len(list(vert.glob("*.mp4"))) if vert.is_dir() else 0
    speech = day / "analysis" / "SPEECH_PEAKS.json"
    sp = "—"
    if speech.is_file():
        sp = json.loads(speech.read_text(encoding="utf-8")).get("status", "?")
    short = day / "review-pack" / "SHORTLIST.md"
    today = datetime.now().strftime("%Y-%m-%d")
    day_id = day.name.replace("returner-daily-", "")
    prior = day_id != today
    # Age from harvest lock / MANIFEST — not folder mtime (REVIEW_READY writes reset mtime)
    lock = day / ".harvest_once"
    man = day / "MANIFEST.json" if (day / "MANIFEST.json").is_file() else day / "candidates" / "MANIFEST.json"
    age_src = lock if lock.is_file() else (man if man.is_file() else day)
    mtime = age_src.stat().st_mtime
    age_h = (datetime.now().timestamp() - mtime) / 3600.0
    cal_h = age_h
    try:
        d0 = datetime.strptime(day_id, "%Y-%m-%d")
        cal_h = (datetime.now() - d0).total_seconds() / 3600.0
    except ValueError:
        pass
    if day_id == today and n_mp4:
        fresh_icon, fresh_note = "🟢", f"today · harvest {age_h:.0f}h age"
    elif prior:
        stale = cal_h > 36
        fresh_icon = "🟡"
        tag = "STALE prior day" if stale else "prior harvest — not tonight"
        fresh_note = f"`{day.name}` · day ~{cal_h:.0f}h old · {tag}"
    elif age_h <= 36:
        fresh_icon, fresh_note = "🟡", f"`{day.name}` · {age_h:.0f}h ago · waiting media"
    else:
        fresh_icon, fresh_note = "🟡", f"`{day.name}` · {age_h:.0f}h ago · STALE (>36h)"
    cand_note = f"{n_mp4} mp4"
    if prior and n_mp4:
        cand_note += " (prior day — not tonight)"
    return {
        "markers": "🟢" if markers.is_file() and markers.stat().st_size > 10 else "🟡 empty/missing",
        "candidates": f"{'🟢' if n_mp4 and not prior else ('🟡' if n_mp4 else '🔴')} {cand_note}",
        "vertical": f"{'🟢' if n_vert and not prior else ('🟡' if n_vert else '🟡')} {n_vert} vertical",
        "speech": sp,
        "shortlist": "🟢" if short.is_file() and not prior else ("🟡" if short.is_file() else "🔴"),
        "day": day.name,
        "fresh_icon": fresh_icon,
        "fresh_note": fresh_note,
    }


def soft_poll_line() -> tuple[str, str]:
    """Honest multi-day READY: green only if *today* is ready (not yesterday-only)."""
    p = BROLL / "SOFT_POLL_LATEST.json"
    if not p.is_file():
        return "🟡", "no SOFT_POLL_LATEST.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "🔴", "SOFT_POLL parse fail"
    days = data.get("days") or []
    reasons = ", ".join(
        f"{d.get('day')}:{d.get('reason')}" for d in days[:3] if isinstance(d, dict)
    )
    today = datetime.now().strftime("%Y-%m-%d")
    today_row = next(
        (d for d in days if isinstance(d, dict) and d.get("day") == today),
        None,
    )
    ready_today = data.get("ready_today")
    if ready_today is None and today_row is not None:
        ready_today = bool(today_row.get("ready"))
    elif ready_today is None:
        ready_today = bool(data.get("ready"))
    ready_any = data.get("ready_any")
    if ready_any is None:
        ready_any = any(bool(d.get("ready")) for d in days if isinstance(d, dict)) or bool(
            data.get("ready")
        )
    if ready_today:
        return "🟢", f"ready_today=true · {reasons or today}"
    if ready_any:
        return "🟡", f"ready_today=false · stale other-day READY still staged · {reasons}"
    return "🟡", f"ready_today=false · {reasons or 'no days'}"


def arm_state(day: Path | None) -> tuple[str, str]:
    # Prefer day ARM_STATE.json contract
    if day:
        ap = day / "ARM_STATE.json"
        if ap.is_file():
            try:
                arm = json.loads(ap.read_text(encoding="utf-8"))
                if arm.get("armed"):
                    return "🟡", f"ARM_STATE armed day={arm.get('day')} — verify go hash"
                return "🟢", f"ARM_STATE default deny (armed=false) · {ap.name}"
            except json.JSONDecodeError:
                return "🔴", "ARM_STATE parse fail"
    pkgs = list((DI / "packages").glob("*.json")) if (DI / "packages").is_dir() else []
    truly_armed = []
    not_armed = []
    for p in pkgs:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        if data.get("may_publish") is True:
            truly_armed.append(p.name)
            continue
        arm = str(data.get("arm") or data.get("status") or p.name).upper()
        if "NOT_ARMED" in arm or "NOT_ARMED" in p.name.upper():
            not_armed.append(p.name)
        elif "ARMED" in arm or (p.name.upper().endswith(".ARMED.JSON") and "NOT_" not in p.name.upper()):
            truly_armed.append(p.name)
        else:
            not_armed.append(p.name)
    if truly_armed:
        return "🟡", f"ARMED/may_publish files: {', '.join(truly_armed[:3])} — verify go"
    return "🟢", f"{len(not_armed)} package(s) NOT_ARMED or none · default deny"


def main() -> int:
    day = latest_return()
    w_icon, w_note = win_online()
    a_icon, a_note = audio()
    d = day_signals(day)
    arm_icon, arm_note = arm_state(day)
    sp_icon, sp_note = soft_poll_line()
    lines = [
        f"# GCS pipeline health — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Check | State | Note |",
        "|-------|-------|------|",
        f"| Windows online | {w_icon} | {w_note} |",
        f"| Soft-poll READY | {sp_icon} | {sp_note} |",
        f"| Harvest freshness | {d.get('fresh_icon', '—')} | {d.get('fresh_note', '')} |",
        f"| Audio stamp | {a_icon} | {a_note} |",
        f"| Latest return day | — | `{d.get('day', 'none')}` |",
        f"| Markers SESSION.jsonl | {d['markers']} | |",
        f"| Candidates | {d['candidates']} | |",
        f"| Pride vertical | {d['vertical']} | |",
        f"| Speech peaks | — | `{d['speech']}` |",
        f"| Review SHORTLIST | {d['shortlist']} | |",
        f"| Publish arm | {arm_icon} | {arm_note} |",
        "",
        "## Next",
        "",
        "- Phase A play night: Deck multi-act + AUDIO_GREEN + export → `post_play_harvest.sh`.",
        "- LaunchAgent quiet morning 03–11; active 12:00–02:59 so afternoon export is harvested. No invent FOOTAGE.",
        "",
        f"Spec: `04-Story-and-Capture/PRODUCT_SYSTEM_SPEC.md`",
        "",
    ]
    out = INDEX / "GCS_PIPELINE_HEALTH.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    # also story
    (STORY / "GCS_PIPELINE_HEALTH_LATEST.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
