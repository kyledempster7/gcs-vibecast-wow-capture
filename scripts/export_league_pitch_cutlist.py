#!/usr/bin/env python3
"""Export a human/agent edit cutlist from League pitch storyboard.

NOT_ARMED. No invent media — only rows with real media_path or flash-only.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
STORY = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_STORYBOARD.json"
)
OUT = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_CUTLIST.md"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--storyboard", type=Path, default=STORY)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    if not args.storyboard.is_file():
        print(f"export_cutlist FAIL missing {args.storyboard}")
        return 2
    board = json.loads(args.storyboard.read_text(encoding="utf-8"))
    flash_by = {f["id"]: f for f in board.get("flash_cards") or []}
    shot_by = {s["shot_id"]: s for s in board.get("shots") or []}

    lines = [
        "---",
        "type: pitch-cutlist",
        f"product_id: {board.get('product_id')}",
        f"generated: {datetime.now(timezone.utc).isoformat()}",
        "armed: false",
        "---",
        "",
        "# Explorer’s League pitch — edit cutlist",
        "",
        f"**Status:** {board.get('status')} · captured {board.get('captured_n')}/{board.get('shots_n')}",
        f"**Armed:** false · **kyle_go:** false",
        f"**Law:** {board.get('law')}",
        "",
        "## Sequence (edit order)",
        "",
        "| # | shot | flash | media | overlay |",
        "|---|------|-------|-------|---------|",
    ]
    for step in board.get("sequence") or []:
        shot_id = step.get("shot_id")
        flash_id = step.get("flash_id")
        shot = shot_by.get(shot_id) or {}
        flash = flash_by.get(flash_id) or {}
        media = shot.get("media_path") or "_(missing — capture later)_"
        overlay = flash.get("overlay") or "—"
        lines.append(
            f"| {step.get('order')} | `{shot_id}` | `{flash_id}` · {flash.get('text','')} | `{media}` | {overlay} |"
        )

    lines += [
        "",
        "## Captured media only",
        "",
    ]
    captured = [s for s in board.get("shots") or [] if s.get("captured") and s.get("media_path")]
    if not captured:
        lines.append("_None yet._")
    else:
        for s in captured:
            lines.append(f"- **`{s['shot_id']}`** ← `{s.get('keep_id','?')}` · `{s['media_path']}`")

    lines += [
        "",
        "## Flash cards (all scaffold)",
        "",
    ]
    for f in board.get("flash_cards") or []:
        lines.append(f"- `{f['id']}`: {f.get('text')} · open `{f.get('overlay')}`")

    lines += [
        "",
        "## Publish",
        "",
        "NOT_ARMED until kyle_go. Never invent Discord invite or guild roster on slate.",
        "",
    ]
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"export_cutlist OK captured={len(captured)} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
