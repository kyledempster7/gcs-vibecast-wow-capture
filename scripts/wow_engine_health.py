#!/usr/bin/env python3
"""
SCH-5 / weekly health: local vault checks for WoW content engine.

Writes 00-Index/ENGINE_HEALTH_latest.md
Optional: --ssh-tasks probes Windows Task Scheduler via BatchMode SSH.
  Fast path: windows_reachability (Tailscale) — skip SSH hang when offline.
Exit: 0 always if report written (warnings in body)
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
INDEX = WOW / "00-Index"
STORY = WOW / "04-Story-and-Capture"
SCORE = WOW / "Characters" / "scorecards" / "latest.md"
CAPTURE = STORY / "capture-inbox" / "latest.md"
MEMENTO = STORY / "memento-inbox" / "latest.md"
ROSTER = WOW / "wow-roster-tracker" / "output" / "latest.md"
DAILY = STORY / "returner-daily"
AUDIO = STORY / "GAME_AUDIO_RESETUP.md"
AUDIO_STAMP = STORY / "AUDIO_GREEN_STAMP.md"
REGISTRY = STORY / "EPISODE_REGISTRY.json"
STREAMER_NOW = INDEX / "STREAMER_NOW.md"
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
SSH_HOST = "kyled@100.92.159.73"
TASKS = [
    "WoW CareSix Live Roster Nightly",
    "WoW Capture Inbox Daily",
    "WoW Memento Inbox Daily",
    "WoW Nightly Inbox Chain",
    "WoW Engine Health Weekly",
]
SCRIPTS = Path(__file__).resolve().parent


def package_product_line() -> str:
    """NOT_ARMED present ≠ product ready. Flag media=0 as HOLD."""
    pkg_dir = DI / "packages"
    if not pkg_dir.is_dir():
        return "🟡 no packages dir"
    pkgs = sorted(pkg_dir.glob("*.NOT_ARMED.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pkgs:
        return "🟡 none yet"
    p = pkgs[0]
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        n = len(data.get("media") or [])
        brand = data.get("brand") or "?"
        day = data.get("day") or p.name
        if n == 0:
            return f"🟡 HOLD media=0 · {p.name} · brand={brand} · day={day} · not product ready"
        ready = data.get("product_ready")
        if ready is False:
            return f"🟡 media={n} product_ready=false · {p.name}"
        return f"🟢 media={n} · {p.name} · brand={brand} (still NOT_ARMED until Kyle go)"
    except Exception as e:
        return f"🟡 present unreadable ({e})"


def age_hours(path: Path) -> str:
    if not path.is_file():
        return "MISSING"
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    h = age.total_seconds() / 3600
    return f"{h:.1f}h"


def flag(path: Path, max_h: float) -> str:
    if not path.is_file():
        return "🔴 missing"
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    if age > timedelta(hours=max_h):
        return f"🟡 stale ({age_hours(path)})"
    return f"🟢 ok ({age_hours(path)})"


def windows_verdict() -> dict:
    """Fast Tailscale reachability; never hang on offline host."""
    helper = SCRIPTS / "windows_reachability.py"
    if not helper.is_file():
        return {"verdict": "UNKNOWN", "error": "windows_reachability.py missing"}
    try:
        # import sibling module by path
        import importlib.util

        spec = importlib.util.spec_from_file_location("windows_reachability", helper)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.probe(force_ssh=False)
        mod.write_receipt(result)
        return result
    except Exception as e:
        return {"verdict": "UNKNOWN", "error": str(e)}


def probe_ssh_tasks() -> list[str]:
    # Fast gate: Tailscale offline → one OFFLINE block, no 5× timeout hang
    reach = windows_verdict()
    verdict = reach.get("verdict") or "UNKNOWN"
    ts = reach.get("tailscale") or {}
    lines: list[str] = [
        f"| **Reachability** | `{verdict}` · TS online={ts.get('online')} last_seen=`{ts.get('last_seen')}` |",
    ]
    if not str(verdict).startswith("ONLINE"):
        lines.append(
            f"| **SCH tasks** | 🔴 **UNPROVEN** — host offline / unreachable (`{SSH_HOST}`). "
            "Do not inherit Ready from prior chat. | "
        )
        lines.append("| — | Re-run `--ssh-tasks` when Tailscale shows 3900x Online. |")
        return lines

    # One task per ssh invocation avoids PowerShell quoting hell over SSH
    for name in TASKS:
        try:
            r = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=10",
                    SSH_HOST,
                    f'powershell -NoProfile -Command "(Get-ScheduledTask -TaskName \'{name}\' -EA SilentlyContinue).State"',
                ],
                capture_output=True,
                text=True,
                timeout=20,
            )
            state = (r.stdout or "").strip() or ("MISSING" if r.returncode != 0 else "UNKNOWN")
            # State may be multi-line noise; take last non-empty token
            state = [s for s in state.splitlines() if s.strip()][-1] if state else "MISSING"
            low = state.lower()
            icon = "🟢" if low in ("ready", "running") else ("🔴" if low == "missing" else "🟡")
            lines.append(f"| {name} | {icon} {state} |")
        except Exception as e:
            lines.append(f"| {name} | 🔴 probe error: {e} |")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ssh-tasks", action="store_true")
    args = ap.parse_args()

    skill = Path.home() / ".grok" / "skills" / "kyle-os" / "SKILL.md"
    law = (
        Path.home()
        / "Library"
        / "Application Support"
        / "UAH"
        / "butler"
        / "control-plane"
        / "DELIVERY_INDEPENDENCE_LAW_20260809.md"
    )
    pulse = Path(__file__).parent / "engine_pulse.py"
    post_night = Path(__file__).parent / "post_night_mac.sh"
    stitch = Path(__file__).parent / "stitch_returner_package.py"

    audio_green = False
    if AUDIO_STAMP.is_file():
        parts = AUDIO_STAMP.read_text(encoding="utf-8").split("---", 2)
        fm = parts[1] if len(parts) >= 3 else ""
        audio_green = "status: GREEN" in fm

    outbox_ok = OUTBOX_DB.is_file()
    pkg_line = package_product_line()
    reach_quick = windows_verdict()
    win_v = reach_quick.get("verdict") or "UNKNOWN"

    lines = [
        f"# WoW content engine health — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "**Host:** local vault scan"
        + (" + SSH task probe" if args.ssh_tasks else " (pass `--ssh-tasks` for Windows tasks)"),
        "",
        "| Check | Status | Path |",
        "|-------|--------|------|",
        f"| Roster latest | {flag(ROSTER, 36)} | `wow-roster-tracker/output/latest.md` |",
        f"| Scorecard latest | {flag(SCORE, 36)} | `Characters/scorecards/latest.md` |",
        f"| Capture inbox | {flag(CAPTURE, 48)} | `capture-inbox/latest.md` |",
        f"| Memento inbox | {flag(MEMENTO, 48)} | `memento-inbox/latest.md` |",
        f"| Game audio card | {'🟢 present' if AUDIO.is_file() else '🔴 missing'} | `GAME_AUDIO_RESETUP.md` |",
        f"| Audio green stamp | {'🟢 GREEN' if audio_green else '🟡 OPEN / unstamped'} | `AUDIO_GREEN_STAMP.md` |",
        f"| Episode registry | {'🟢' if REGISTRY.is_file() else '🔴'} | `EPISODE_REGISTRY.json` |",
        f"| Returner daily root | {'🟢 present' if DAILY.is_dir() else '🟡 not scaffolded'} | `returner-daily/` |",
        f"| Local NOT_ARMED package | {pkg_line} | delivery-independence/packages |",
        f"| Package product rule | 🟡 media=0 = HOLD not ready | never green on file presence alone |",
        f"| Outbox SQLite | {'🟢' if outbox_ok else '🟡'} | delivery-independence/data |",
        f"| Windows host (TS) | {'🟢' if str(win_v).startswith('ONLINE') else '🔴'} `{win_v}` | `windows_reachability.py` |",
        f"| engine_pulse.py | {'🟢' if pulse.is_file() else '🔴'} | scripts |",
        f"| post_night_mac.sh | {'🟢' if post_night.is_file() else '🔴'} | scripts |",
        f"| stitch_returner_package | {'🟢' if stitch.is_file() else '🔴'} | scripts |",
        f"| Streamer NOW | {'🟢' if STREAMER_NOW.is_file() else '🟡 run pulse'} | `STREAMER_NOW.md` |",
        f"| GCS citadel map | {'🟢' if (INDEX / 'GCS_CITADEL.md').is_file() else '🔴'} | one house |",
        f"| SIMPLE_START | {'🟢' if (INDEX / 'SIMPLE_START.md').is_file() else '🔴'} | Kyle 3-step |",
        f"| VibeCast wing | {'🟢' if (INDEX / 'VIBECAST_OS.md').is_file() else '🔴'} | under GCS · TWE |",
        f"| Vibe sessions root | {'🟢' if (STORY / 'vibe-sessions').is_dir() else '🟡'} | `vibe-sessions/` |",
        f"| Kyle OS note | {'🟢' if (INDEX / 'KYLE_OS.md').is_file() else '🔴'} | `00-Index/KYLE_OS.md` |",
        f"| Kyle OS skill | {'🟢' if skill.is_file() else '🔴 missing skill'} | `~/.grok/skills/kyle-os/` |",
        f"| Delivery independence law | {'🟢' if law.is_file() else '🟡'} | control-plane |",
        f"| Compact master | {'🟢' if (INDEX / 'COMPACT_MASTER_HANDOFF_2026-08-09.md').is_file() else '🟡'} | compact handoff |",
        f"| Gaps register | {'🟢' if (INDEX / 'GAPS_AND_NEXT_LEVEL.md').is_file() else '🟡'} | next-level SoT |",
        f"| Returner board | {'🟢' if (INDEX / 'RETURNER_DAILY_BOARD.md').is_file() else '🟡 run board'} | product_ready truth |",
        "",
    ]

    if args.ssh_tasks:
        lines += ["## Windows scheduled tasks (SSH)", "", "| Task | State |", "|------|-------|"]
        lines += probe_ssh_tasks()
        lines.append("")
    else:
        lines += [
            "## Windows (quick)",
            "",
            f"- Reachability: **`{win_v}`** (full SCH states only with `--ssh-tasks` when Online)",
            f"- Pointer: `00-Index/WINDOWS_REACHABILITY_latest.md`",
            "",
        ]

    lines += [
        "## Open walls (not auto-fixed)",
        "",
        "- Game audio 10s playback pass (Kyle)",
        "- EP audio Recorded (Kyle)",
        "- Publish go (Kyle)",
        "- Stream Deck Locked binds (Kyle)",
        "- **Package with media=0 is HOLD** — not dogfood product",
        "",
        "## Agent next if yellow/red",
        "",
        "1. `python3 scripts/windows_reachability.py` — if OFFLINE, wait for PC; do not claim SCH Ready",
        "2. Fire CareSix / scorecard if roster stale **and** Windows Online",
        "3. Run capture + memento inbox scripts on Windows",
        "4. `bash scripts/post_night_mac.sh` after nights (pull → stitch → skip/board → pulse)",
        "5. `python3 scripts/engine_pulse.py --health` for Streamer NOW",
        "6. Delivery: local outbox under control-plane/delivery-independence/",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    out = INDEX / "ENGINE_HEALTH_latest.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    day = INDEX / f"ENGINE_HEALTH_{datetime.now().strftime('%Y-%m-%d')}.md"
    day.write_text("\n".join(lines), encoding="utf-8")
    print(f"health -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

