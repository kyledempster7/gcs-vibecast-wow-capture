#!/usr/bin/env python3
"""Single status board for the all-in-one VibeCast content system."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
INDEX = WOW / "00-Index"
STORY = WOW / "04-Story-and-Capture"
SESS = STORY / "vibe-sessions"
DAILY = STORY / "returner-daily"
REG = STORY / "EPISODE_REGISTRY.json"
AUDIO = STORY / "AUDIO_GREEN_STAMP.md"
ESSAY = Path.home() / "Movies" / "WoW-Essays"
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
        return "missing stamp"
    parts = AUDIO.read_text(encoding="utf-8").split("---", 2)
    fm = parts[1] if len(parts) >= 3 else ""
    return "GREEN" if "status: GREEN" in fm else "OPEN"


def main() -> int:
    ep_rec = 0
    ep_n = 0
    if REG.is_file():
        eps = json.loads(REG.read_text(encoding="utf-8")).get("episodes", [])
        ep_n = len(eps)
        ep_rec = sum(1 for e in eps if e.get("recorded"))

    pkgs = list((DI / "packages").glob("*.NOT_ARMED.json")) if (DI / "packages").is_dir() else []
    lines = [
        f"# VibeCast status — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "**Citadel:** [[GCS_CITADEL]] (VibeCast = GCS · TWE wing) · [[KYLE_OS]] · [[SIMPLE_START]]",
        "",
        "## System",
        "",
        "| Piece | Status |",
        "|-------|--------|",
        f"| VibeCast OS | {'🟢' if (INDEX / 'VIBECAST_OS.md').is_file() else '🔴'} |",
        f"| Pipeline map | {'🟢' if (INDEX / 'VIBECAST_PIPELINE.md').is_file() else '🔴'} |",
        f"| Latest vibe session | `{latest(SESS)}` |",
        f"| Latest Returner Daily | `{latest(DAILY)}` |",
        f"| Audio stamp | **{audio_status()}** |",
        f"| Essay drop folder | {'🟢' if ESSAY.is_dir() else '🔴'} `~/Movies/WoW-Essays` |",
        f"| NOT_ARMED packages | {len(pkgs)} |",
        f"| EP recorded | {ep_rec}/{ep_n} |",
        f"| Muddy card | {'🟢' if (STORY / 'YouTube' / 'STREAM_MUDDY_TALK_CARD.md').is_file() else '🔴'} |",
        f"| Podcast scaffold | {'🟢' if (STORY / 'YouTube' / 'podcast' / 'README.md').is_file() else '🔴'} |",
        "",
        "## Vibe night recipe (Kyle)",
        "",
        "1. Pick one mode on Kyle OS (muddy = default vibe-cast)",
        "2. 60s audio gate (voice-only OK)",
        "3. Record · stop while fun · logout",
        "4. Optional one-liner — agents do the rest",
        "",
        "## Agent recipe",
        "",
        "```bash",
        "python3 scripts/log_vibe_session.py --mode muddy",
        "bash scripts/post_night_mac.sh",
        "python3 scripts/vibecast_status.py",
        "```",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    out = INDEX / "VIBECAST_STATUS.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))
    print(f"vibecast_status -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
