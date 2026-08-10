#!/usr/bin/env python3
"""Build a NOT_ARMED Explorer’s League pitch storyboard from on-disk pack + flash slot.

Fail-closed: no invent FOOTAGE paths. armed always false.
product_id: twe_explorers_league_community_pitch_v1
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PRODUCT_ID = "twe_explorers_league_community_pitch_v1"
WOW = Path(__file__).resolve().parents[2]
PACK = WOW / "04-Story-and-Capture" / "social" / "EXPLORERS_LEAGUE_PITCH_BROLL_PACK.md"
FLASH_HTML = (
    WOW
    / "04-Story-and-Capture"
    / "hyperframes-brand-kit"
    / "slots"
    / "league-pitch-flash"
    / "index.html"
)
OUT_DEFAULT = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_STORYBOARD.json"
)
MEDIA_MAP = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_MEDIA_MAP.json"
)


def parse_flash_cards(pack_text: str) -> list[dict]:
    """Parse flash table rows: | `flash.x` | text | use |"""
    cards = []
    for line in pack_text.splitlines():
        m = re.match(
            r"\|\s*`?(flash\.[a-z0-9_]+)`?\s*\|\s*([^|]+)\|\s*([^|]+)\|",
            line.strip(),
        )
        if not m:
            continue
        cards.append(
            {
                "id": m.group(1).strip(),
                "text": m.group(2).strip(),
                "over": m.group(3).strip(),
                "overlay": f"file://{FLASH_HTML}?id={m.group(1).strip()}",
            }
        )
    return cards


def parse_shots(pack_text: str) -> list[dict]:
    shots = []
    for line in pack_text.splitlines():
        m = re.match(
            r"\|\s*`?(pitch\.[a-z0-9_]+)`?\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*\[([ xX])\]\s*\|",
            line.strip(),
        )
        if not m:
            continue
        done = m.group(4).lower() == "x"
        shots.append(
            {
                "shot_id": m.group(1).strip(),
                "description": m.group(2).strip(),
                "why": m.group(3).strip(),
                "captured": done,
                "media_path": None,  # never invent
            }
        )
    return shots


def suggested_sequence() -> list[dict]:
    """Edit sequence from pack doctrine (scaffold)."""
    return [
        {"order": 1, "shot_id": "pitch.hub_thrall", "flash_id": "flash.welcome"},
        {"order": 2, "shot_id": "pitch.flight_soft", "flash_id": "flash.league"},
        {"order": 3, "shot_id": "pitch.play_together", "flash_id": "flash.community"},
        {"order": 4, "shot_id": "pitch.craft_cast", "flash_id": "flash.fair"},
        {"order": 5, "shot_id": "pitch.prof_panel", "flash_id": "flash.fair"},
        {"order": 6, "shot_id": "pitch.gather_to_craft", "flash_id": "flash.fair"},
        {"order": 7, "shot_id": "pitch.dungeon_door", "flash_id": "flash.dungeons"},
        {"order": 8, "shot_id": "pitch.still_waitlist", "flash_id": "flash.discord_door"},
        {"order": 9, "shot_id": "pitch.cast_lineup", "flash_id": "flash.not_alone"},
    ]


def build(pack_path: Path = PACK) -> dict:
    if not pack_path.is_file():
        raise FileNotFoundError(pack_path)
    if not FLASH_HTML.is_file():
        raise FileNotFoundError(FLASH_HTML)
    text = pack_path.read_text(encoding="utf-8")
    flashes = parse_flash_cards(text)
    shots = parse_shots(text)
    if len(flashes) < 3:
        raise ValueError(f"need ≥3 flash cards, got {len(flashes)}")
    if len(shots) < 1:
        raise ValueError("need ≥1 shot row")
    return {
        "schema": "gcs_explorers_league_pitch_storyboard/v1",
        "product_id": PRODUCT_ID,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "armed": False,
        "kyle_go": False,
        "status": "scaffold_storyboard",
        "law": "no invent FOOTAGE · no silent publish · never invent League roster · go-only",
        "flash_cards": flashes,
        "shots": shots,
        "sequence": suggested_sequence(),
        "captured_n": sum(1 for s in shots if s.get("captured")),
        "shots_n": len(shots),
        "flash_n": len(flashes),
        "flash_html": str(FLASH_HTML),
        "pack": str(pack_path),
        "ready_to_edit": False,  # true only when captured media paths filled later
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--pack", type=Path, default=PACK)
    args = ap.parse_args()
    doc = build(args.pack)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    # keep media map flash list in sync (armed stays false)
    if MEDIA_MAP.is_file():
        try:
            media = json.loads(MEDIA_MAP.read_text(encoding="utf-8"))
            media["flash_text_ids"] = [c["id"] for c in doc["flash_cards"]]
            media["shot_ids"] = [s["shot_id"] for s in doc["shots"]]
            media["storyboard"] = str(args.out)
            media["armed"] = False
            media["generated_at_utc"] = doc["generated_at_utc"]
            MEDIA_MAP.write_text(json.dumps(media, indent=2) + "\n", encoding="utf-8")
        except Exception as e:
            print(f"WARN media_map sync: {e}")
    print(
        f"storyboard OK product={PRODUCT_ID} flash={doc['flash_n']} shots={doc['shots_n']} "
        f"captured={doc['captured_n']} armed=false -> {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
