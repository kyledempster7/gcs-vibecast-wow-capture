#!/usr/bin/env python3
"""Structural check for Explorer’s League community product spine + pitch pack.

Drives real on-disk artifacts under Games/WoW. Exit 0 only if required sections
and fail-closed keys exist. No invent FOOTAGE. No publish.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
SPINE = WOW / "community-surface" / "EXPLORERS_LEAGUE_COMMUNITY_SPINE.md"
PACK = WOW / "04-Story-and-Capture" / "social" / "EXPLORERS_LEAGUE_PITCH_BROLL_PACK.md"
MEDIA = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_MEDIA_MAP.json"
)
INDEX = WOW / "community-surface" / "PRODUCT_INDEX.json"
WISHLIST = WOW / "community-surface" / "FOOTAGE_WISHLIST.md"

PRODUCT_ID = "twe_explorers_league_community_pitch_v1"

SPINE_REQUIRED = [
    r"## Fail-closed status",
    r"## Pillar 1 — Guild intent",
    r"## Pillar 2 — Crafting fair",
    r"## Pillar 3 — Weekly dungeon nights",
    r"## Pillar 4 — Discord",
    r"Thrall",
    r"Horde",
    r"product_id",
    PRODUCT_ID,
    r"scaffold",
    r"never invent",
]

PACK_REQUIRED = [
    r"## Flash text cards",
    r"## Shot / moment list",
    r"flash\.welcome",
    r"flash\.fair",
    r"flash\.dungeons",
    r"pitch\.hub_thrall",
    r"pitch\.craft_cast",
    r"armed",
    PRODUCT_ID,
]


def fail(msg: str) -> None:
    print(f"FAIL {msg}")
    raise SystemExit(1)


def main() -> int:
    for path in (SPINE, PACK, MEDIA, INDEX, WISHLIST):
        if not path.is_file():
            fail(f"missing {path}")

    spine = SPINE.read_text(encoding="utf-8")
    for pat in SPINE_REQUIRED:
        if not re.search(pat, spine, re.I):
            fail(f"spine missing pattern: {pat}")

    pack = PACK.read_text(encoding="utf-8")
    for pat in PACK_REQUIRED:
        if not re.search(pat, pack, re.I):
            fail(f"pack missing pattern: {pat}")

    # Count flash table rows with flash.* ids
    flash_ids = re.findall(r"`(flash\.[a-z0-9_]+)`", pack)
    if len(set(flash_ids)) < 3:
        fail(f"need ≥3 flash ids, got {sorted(set(flash_ids))}")

    media = json.loads(MEDIA.read_text(encoding="utf-8"))
    if media.get("armed") is not False:
        fail(f"media map must armed=false, got {media.get('armed')}")
    if media.get("product_id") != PRODUCT_ID:
        fail("media product_id mismatch")
    if not media.get("flash_text_ids") or len(media["flash_text_ids"]) < 3:
        fail("media flash_text_ids short")

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    products = index.get("products") or []
    hit = [p for p in products if p.get("product_id") == PRODUCT_ID]
    if not hit:
        fail("PRODUCT_INDEX missing product_id")
    entry = hit[0]
    for key in ("spine", "pitch_broll_pack", "media_map", "tags"):
        if key not in entry:
            fail(f"index entry missing {key}")
    if entry.get("armed") is not False:
        fail("index entry must armed=false")

    wish = WISHLIST.read_text(encoding="utf-8")
    if "Community pitch (Explorer’s League)" not in wish and "Community pitch" not in wish:
        fail("FOOTAGE_WISHLIST missing Community pitch section")
    if PRODUCT_ID not in wish:
        fail("FOOTAGE_WISHLIST missing product_id")

    print("PASS validate_explorers_league_community_spine")
    print(f"  spine={SPINE}")
    print(f"  pack={PACK}")
    print(f"  media_armed={media.get('armed')}")
    print(f"  flash_ids={len(set(flash_ids))}")
    print(f"  product_id={PRODUCT_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
