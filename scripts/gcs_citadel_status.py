#!/usr/bin/env python3
"""
One GCS citadel board: Factory wing + VibeCast wing + Armory.
Plain language for Kyle; paths for agents.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
INDEX = WOW / "00-Index"
STORY = WOW / "04-Story-and-Capture"
SESS = STORY / "vibe-sessions"
DAILY = STORY / "returner-daily"
AUDIO = STORY / "AUDIO_GREEN_STAMP.md"
FLEET = Path.home() / ".codex" / "saturday-fleet-readiness"
FLEET_CFG = FLEET / "fleet-week-2026-08-08.json"
SOCIAL = Path.home() / "Movies" / "WoW-Social-Workflow"
BROLL = Path.home() / "Movies" / "WoW-Broll-Workflow"
DI = (
    Path.home()
    / "Library"
    / "Application Support"
    / "UAH"
    / "butler"
    / "control-plane"
    / "delivery-independence"
)


def latest(dirpath: Path) -> str:
    if not dirpath.is_dir():
        return "none"
    days = sorted(
        [p.name for p in dirpath.iterdir() if p.is_dir() and p.name[:4].isdigit()],
        reverse=True,
    )
    return days[0] if days else "none"


def audio_status() -> str:
    if not AUDIO.is_file():
        return "missing"
    parts = AUDIO.read_text(encoding="utf-8").split("---", 2)
    fm = parts[1] if len(parts) >= 3 else ""
    return "GREEN" if "status: GREEN" in fm else "OPEN"


def kyle_open_count() -> tuple[int, int, str]:
    hj = INDEX / "KYLE_HELP_NEEDED.json"
    if not hj.is_file():
        return 0, 0, "no help json"
    data = json.loads(hj.read_text(encoding="utf-8"))
    items = data.get("items", [])
    open_n = sum(1 for i in items if i.get("status") != "CLOSED")
    ids = ", ".join(i["id"] for i in items if i.get("status") != "CLOSED")
    return open_n, len(items), ids or "—"


def main() -> int:
    pkgs = list((DI / "packages").glob("*.json")) if (DI / "packages").is_dir() else []
    k_open, k_tot, k_ids = kyle_open_count()
    lines = [
        f"# GCS status — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "**Citadel:** Gaming Content Studio · map [[GCS_CITADEL]] · simple [[SIMPLE_START]] · tutorial [[KYLE_WALKTHROUGH]]",
        "",
        "## Wings at a glance",
        "",
        "| Wing | What it is | Status |",
        "|------|------------|--------|",
        f"| **Factory** | Saturday TWE/TDE/TFE zone weeks | fleet dir {'🟢' if FLEET.is_dir() else '🔴'} · cfg {'🟢' if FLEET_CFG.is_file() else '🟡'} |",
        f"| **VibeCast** | Your play nights → Returner Daily / podcast | session `{latest(SESS)}` · daily `{latest(DAILY)}` |",
        f"| **Armory** | Packages before publish | {len(pkgs)} package file(s) · go = Kyle only |",
        f"| **Play door** | Kyle OS | {'🟢' if (INDEX / 'KYLE_OS.md').is_file() else '🔴'} |",
        f"| **Audio stamp** | Game sound 10s | **{audio_status()}** |",
        f"| **Kyle open items** | Help-needed tally | **{k_open}/{k_tot}** open ({k_ids}) · [[KYLE_HELP_NEEDED]] |",
        f"| **Tomorrow ready?** | Binder + scripts | "
        f"{'🟢' if (INDEX / 'TOMORROW_SESSION.md').is_file() and (INDEX / 'PRODUCT_THESIS_VIBECAST.md').is_file() else '🟡'} "
        f"TOMORROW_SESSION · thesis · focus K1→K2 |",
        "",
        "## Factory (agents / Saturday)",
        "",
        f"| Check | Path / note |",
        f"|-------|-------------|",
        f"| Fleet readiness | `{FLEET}` |",
        f"| Social products | `{SOCIAL}` {'🟢' if SOCIAL.is_dir() else '🟡'} |",
        f"| B-roll workflow | `{BROLL}` {'🟢' if BROLL.is_dir() else '🟡'} |",
        f"| Review law | Kyle ACCEPT only — agent eye ≠ green |",
        "",
        "## VibeCast (play night)",
        "",
        f"| Check | Value |",
        f"|-------|-------|",
        f"| Latest vibe session | `{latest(SESS)}` |",
        f"| Latest Returner Daily | `{latest(DAILY)}` |",
        f"| Brand on packages | **twe** (GCS TWE) |",
        f"| Essay drop | `~/Movies/WoW-Essays` |",
        "",
        "## You (Kyle)",
        "",
        "1. [[SIMPLE_START]] or [[KYLE_WALKTHROUGH]]",
        "2. Play / talk · logout",
        "3. Open list: [[KYLE_HELP_NEEDED]]",
        "4. Never open factory trees on play night",
        "",
        "## Agents",
        "",
        "```bash",
        "python3 scripts/gcs_citadel_status.py",
        "python3 scripts/walk_with_kyle.py --tally",
        "python3 scripts/walk_with_kyle.py --path vibe   # when walking Kyle",
        "bash scripts/post_night_mac.sh",
        "# Factory: ~/.codex/saturday-fleet-readiness/",
        "```",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    out = INDEX / "GCS_STATUS.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    # also alias name Kyle might say
    (INDEX / "CITADEL_STATUS.md").write_text(
        "# Alias → [[GCS_STATUS]]\n\nSame board. Prefer **GCS_STATUS**.\n",
        encoding="utf-8",
    )
    print(out.read_text(encoding="utf-8"))
    print(f"gcs_status -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
