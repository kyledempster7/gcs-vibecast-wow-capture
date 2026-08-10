#!/usr/bin/env python3
"""
Essay / EP show-notes seed helper (P2).

Writes show-notes only when EPISODE_REGISTRY has a real audio_path that exists,
or --force-scaffold for empty honest draft. Never invents audio.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
STORY = WOW / "04-Story-and-Capture"
REG = STORY / "EPISODE_REGISTRY.json"
OUT_ROOT = Path.home() / "Movies" / "WoW-Essays"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ep", default=None, help="episode id e.g. EP01")
    ap.add_argument("--force-scaffold", action="store_true")
    args = ap.parse_args()

    if not REG.is_file():
        print(f"ERROR: missing {REG}")
        return 1
    data = json.loads(REG.read_text(encoding="utf-8"))
    eps = data.get("episodes") or []
    if args.ep:
        ep = next((e for e in eps if e.get("id") == args.ep), None)
        if not ep:
            print(f"ERROR: ep {args.ep} not in registry")
            return 2
        targets = [ep]
    else:
        targets = eps

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    wrote = 0
    for ep in targets:
        eid = ep.get("id") or "EP"
        audio = ep.get("audio_path") or ep.get("path")
        exists = bool(audio and Path(str(audio)).is_file())
        if not exists and not args.force_scaffold:
            print(f"SKIP {eid}: no real audio_path on disk (refuse invent)")
            continue
        dest_dir = OUT_ROOT / eid
        dest_dir.mkdir(parents=True, exist_ok=True)
        notes = dest_dir / "SHOW_NOTES.md"
        body = [
            f"# Show notes — {eid}",
            "",
            f"**Title:** {ep.get('title') or '—'}",
            f"**Status:** {ep.get('status') or '—'}",
            f"**Recorded:** {ep.get('recorded')}",
            f"**audio_path:** `{audio or '—'}`",
            f"**audio_exists:** {exists}",
            f"**Seeded:** {datetime.now().isoformat(timespec='seconds')}",
            "",
            "## Chapters (fill after real markers)",
            "",
            "| t | chapter |",
            "|---|---------|",
            "| 0:00 | cold open |",
            "",
            "## Description seed",
            "",
            f"{ep.get('title') or eid} — Explorer series under TWE / GCS VibeCast.",
            "",
            "Do not invent achievements or timestamps. Fill from real take only.",
            "",
        ]
        notes.write_text("\n".join(body), encoding="utf-8")
        print(f"show_notes -> {notes} exists={exists}")
        wrote += 1
    if wrote == 0:
        print("no notes written — need real audio_path or --force-scaffold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
