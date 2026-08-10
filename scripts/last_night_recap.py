#!/usr/bin/env python3
"""Write LAST_NIGHT_RECAP.md — what agents did + what waits on Kyle."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
INDEX = WOW / "00-Index"
STORY = WOW / "04-Story-and-Capture"
SESS = STORY / "vibe-sessions"
DAILY = STORY / "returner-daily"
HELP = INDEX / "KYLE_HELP_NEEDED.json"
DI = (
    Path.home()
    / "Library"
    / "Application Support"
    / "UAH"
    / "butler"
    / "control-plane"
    / "delivery-independence"
    / "packages"
)


def latest(dirpath: Path) -> str:
    if not dirpath.is_dir():
        return "none"
    days = sorted(
        [p.name for p in dirpath.iterdir() if p.is_dir() and p.name[:4].isdigit()],
        reverse=True,
    )
    return days[0] if days else "none"


def main() -> int:
    day = latest(SESS) if latest(SESS) != "none" else latest(DAILY)
    day_dir = DAILY / day if day != "none" else None
    sources = ""
    if day_dir and (day_dir / "SOURCES.md").is_file():
        sources = (day_dir / "SOURCES.md").read_text(encoding="utf-8")
    has_video = bool(re_search_path(sources, "video"))
    has_still = bool(re_search_path(sources, "still"))
    pkgs = list(DI.glob("*.json")) if DI.is_dir() else []
    open_k = []
    if HELP.is_file():
        for it in json.loads(HELP.read_text(encoding="utf-8")).get("items", []):
            if it.get("status") != "CLOSED":
                open_k.append(it["id"])

    lines = [
        f"# Last night recap — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "**For Kyle:** what agents already did · what only you unlock next.",
        "",
        "## Agents did / state",
        "",
        f"| Item | Value |",
        f"|------|-------|",
        f"| Vibe session | `{latest(SESS)}` |",
        f"| Returner Daily day | `{latest(DAILY)}` |",
        f"| Video path set | {'yes' if has_video else 'no — need real path or voice-only night'} |",
        f"| Still path set | {'yes' if has_still else 'no — Memento/list after play'} |",
        f"| NOT_ARMED packages | {len(pkgs)} |",
        f"| Publish | **not** fired (fail-closed) |",
        "",
        "## Waiting on Kyle",
        "",
        f"Open help IDs: **{', '.join(open_k) if open_k else 'none'}** · full list [[KYLE_HELP_NEEDED]]",
        "",
        "### Tomorrow focus",
        "",
        "1. Open [[TOMORROW_SESSION]]",
        "2. Prefer **K1** (audio once) then **K2** (vibe-cast night)",
        "3. After play: full logout · optional one-liner",
        "",
        "## Agent commands after your night",
        "",
        "```bash",
        "bash wow-roster-tracker/scripts/post_night_mac.sh",
        "# when paths known:",
        "python3 wow-roster-tracker/scripts/attach_media_to_day.py --day YYYY-MM-DD \\",
        '  --video "D:\\\\path\\\\file.mp4" --allow-missing',
        "python3 wow-roster-tracker/scripts/merge_caption_seed.py --day YYYY-MM-DD",
        "```",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    out = INDEX / "LAST_NIGHT_RECAP.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"recap -> {out}")
    return 0


def re_search_path(text: str, role: str) -> str | None:
    import re

    m = re.search(rf"\|\s*{role}\s*\|\s*`([^`]+)`", text or "", re.I)
    if not m:
        return None
    val = m.group(1).strip()
    if val in ("—", "-", "none", "–", ""):
        return None
    return val


if __name__ == "__main__":
    raise SystemExit(main())
