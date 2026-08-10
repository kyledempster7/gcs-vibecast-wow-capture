#!/usr/bin/env python3
"""
One-shot pulse for streamer ease + agents.

Prints: walls · next human mode · latest drafts · package/outbox · episode board
Writes: 00-Index/STREAMER_NOW.md (+ optional ENGINE_HEALTH via --health)

No publish. No invent media paths.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
INDEX = WOW / "00-Index"
STORY = WOW / "04-Story-and-Capture"
DAILY = STORY / "returner-daily"
REG = STORY / "EPISODE_REGISTRY.json"
AUDIO_STAMP = STORY / "AUDIO_GREEN_STAMP.md"
DI = (
    Path.home()
    / "Library"
    / "Application Support"
    / "UAH"
    / "butler"
    / "control-plane"
    / "delivery-independence"
)
OUTBOX_DB = DI / "data" / "outbox.sqlite"
PKG_DIR = DI / "packages"


def latest_day_dir() -> Path | None:
    if not DAILY.is_dir():
        return None
    days = sorted(
        [p for p in DAILY.iterdir() if p.is_dir() and p.name[:4].isdigit()],
        key=lambda p: p.name,
        reverse=True,
    )
    return days[0] if days else None


def outbox_summary() -> str:
    if not OUTBOX_DB.is_file():
        return "no outbox db"
    try:
        con = sqlite3.connect(str(OUTBOX_DB))
        rows = con.execute(
            "SELECT status, COUNT(*) FROM outbox GROUP BY status"
        ).fetchall()
        con.close()
        if not rows:
            return "empty"
        return ", ".join(f"{s}={n}" for s, n in rows)
    except Exception as e:
        return f"read err: {e}"


def audio_is_green() -> bool:
    if not AUDIO_STAMP.is_file():
        return False
    parts = AUDIO_STAMP.read_text(encoding="utf-8").split("---", 2)
    fm = parts[1] if len(parts) >= 3 else ""
    return "status: GREEN" in fm


def package_line(day: str | None) -> str:
    if not day:
        return "no day"
    p = PKG_DIR / f"returner_daily_{day}.NOT_ARMED.json"
    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            n = len(data.get("media") or [])
            pr = data.get("product_ready")
            if n == 0 or pr is False:
                return f"HOLD media={n} product_ready=false · {p.name} (NOT product ready)"
            return f"media={n} product_ready={pr} · {p.name} (still NOT_ARMED)"
        except Exception:
            return f"present unreadable {p.name}"
    # also day folder copy
    d = DAILY / day / "zernio_package.json"
    if d.is_file():
        return f"day copy present ({d})"
    return "missing package"


def episode_lines() -> list[str]:
    if not REG.is_file():
        return ["registry missing"]
    data = json.loads(REG.read_text(encoding="utf-8"))
    lines = []
    for ep in data.get("episodes", []):
        rec = "REC" if ep.get("recorded") else "—"
        lines.append(f"| {ep['id']} | {ep.get('title','')} | {ep.get('status','')} | {rec} |")
    return lines


def calendar_seed() -> list[str]:
    """Real dates D+0..D+13 from today."""
    today = date.today()
    rows = []
    for i in range(14):
        d = today + timedelta(days=i)
        rows.append(f"| {d.isoformat()} |  |  |  |  |  |")
    return rows


def write_calendar_if_stale() -> None:
    cal = INDEX / "CONTENT_CALENDAR_14D.md"
    body = "\n".join(
        [
            "# Content calendar — next 14 days",
            "",
            f"**Seeded:** {date.today().isoformat()} · fill modes when real plans land. Empty slots are honest.",
            "",
            "| Day | Play? | Record mode | EP / Daily | Publish go? | Notes |",
            "|-----|-------|-------------|------------|-------------|-------|",
            *calendar_seed(),
            "",
            "Modes: play · clean · muddy · duo · deck · skip  ",
            "Related: [[KYLE_OS]] · [[RECORD_NIGHT_ONE_SHEET]] · [[STREAMER_NOW]]",
            "",
        ]
    )
    # rewrite when missing real ISO dates (legacy D+0 form)
    old = cal.read_text(encoding="utf-8") if cal.is_file() else ""
    if "D+0" in old or date.today().isoformat() not in old:
        cal.write_text(body, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--health", action="store_true", help="also run wow_engine_health.py")
    ap.add_argument("--ssh-tasks", action="store_true")
    args = ap.parse_args()

    if args.health:
        cmd = [sys.executable, str(Path(__file__).parent / "wow_engine_health.py")]
        if args.ssh_tasks:
            cmd.append("--ssh-tasks")
        subprocess.run(cmd, check=False)

    write_calendar_if_stale()

    day_dir = latest_day_dir()
    day = day_dir.name if day_dir else None
    audio_green = audio_is_green()
    skill = Path.home() / ".grok" / "skills" / "kyle-os" / "SKILL.md"

    lines = [
        f"# Streamer NOW — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "**Citadel:** [[GCS_CITADEL]] · **Start:** [[SIMPLE_START]] · play [[KYLE_OS]] · vibe wing [[VIBECAST_OS]]",
        "",
        "## If you are Kyle (pick one)",
        "",
        "1. Play only — logout  ",
        "2. **Vibe-cast** muddy — play + talk (default content)  ",
        "3. **Vibe-podcast** clean — flight topics  ",
        "4. Deck Layer A Agony  ",
        "5. Duo Agony×Goat  ",
        "",
        "## Walls (not agent-fakeable)",
        "",
        f"| Wall | Status |",
        f"|------|--------|",
        f"| Game audio 10s | {'🟢 stamped GREEN' if audio_green else '🔴 open — GAME_AUDIO_RESETUP + stamp'} |",
        f"| EP series recorded | see episode board below |",
        f"| Deck Locked binds | open until Layer A proof |",
        f"| Publish go | always human |",
        "",
        "## Latest Returner Daily",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Day folder | `{day or 'none'}` |",
        f"| Package | {package_line(day)} |",
        f"| Outbox jobs | {outbox_summary()} |",
        f"| Kyle OS skill | {'🟢' if skill.is_file() else '🔴'} |",
        "",
        "## Episode board",
        "",
        "| ID | Title | Status | Recorded |",
        "|----|-------|--------|----------|",
        *episode_lines(),
        "",
        "## Agent next (no Kyle homework)",
        "",
        "1. `python3 scripts/vibecast_status.py`",
        "2. After play night: `bash scripts/post_night_mac.sh` (logs vibe session + stitch + pulse)",
        "3. `python3 scripts/log_vibe_session.py --mode muddy|clean`",
        "4. Delivery P2 live draft **only with Kyle go**",
        "5. Do **not** install Titan/ElvUI unless named",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    out = INDEX / "STREAMER_NOW.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))
    print(f"pulse -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
