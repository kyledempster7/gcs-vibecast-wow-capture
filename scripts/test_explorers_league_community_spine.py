#!/usr/bin/env python3
"""Drive validate_explorers_league_community_spine.py on real Games/WoW files."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
VALIDATOR = SCRIPTS / "validate_explorers_league_community_spine.py"
WOW = SCRIPTS.parent.parent
PACK = WOW / "04-Story-and-Capture" / "social" / "EXPLORERS_LEAGUE_PITCH_BROLL_PACK.md"
MEDIA = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_MEDIA_MAP.json"
)


def test_validator_pass() -> None:
    r = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout
    print("PASS validator_exit_0")


def test_media_map_not_armed() -> None:
    media = json.loads(MEDIA.read_text(encoding="utf-8"))
    assert media.get("armed") is False
    assert media.get("kyle_go") is False
    assert len(media.get("flash_text_ids") or []) >= 3
    print("PASS media_map_not_armed")


def test_pack_has_flash_and_shots() -> None:
    text = PACK.read_text(encoding="utf-8")
    flashes = set(re.findall(r"`(flash\.[a-z0-9_]+)`", text))
    shots = set(re.findall(r"`(pitch\.[a-z0-9_]+)`", text))
    assert len(flashes) >= 3, flashes
    assert len(shots) >= 1, shots
    assert "NOT_ARMED" in text or "armed: false" in text or "**false**" in text
    print(f"PASS pack flashes={len(flashes)} shots={len(shots)}")


def test_no_false_live_claims() -> None:
    """Banned invent patterns must not appear as live ops claims."""
    spine = (WOW / "community-surface" / "EXPLORERS_LEAGUE_COMMUNITY_SPINE.md").read_text(
        encoding="utf-8"
    )
    pack = PACK.read_text(encoding="utf-8")
    blob = spine + "\n" + pack
    # Allow scaffold language; forbid clear false-live patterns
    banned = [
        r"(?i)guild is recruiting now",
        r"(?i)discord\.gg/[A-Za-z0-9]+",
        r"(?i)members:\s*\d{2,}",
        r"(?i)we have \d+ members",
        r"(?i)join our live discord today",
    ]
    for pat in banned:
        m = re.search(pat, blob)
        assert m is None, f"banned pattern found: {pat} -> {m.group(0) if m else ''}"
    # Must still have scaffold honesty
    assert re.search(r"(?i)scaffold|not claimed|intent only", blob)
    print("PASS no_false_live_claims")


def main() -> int:
    test_validator_pass()
    test_media_map_not_armed()
    test_pack_has_flash_and_shots()
    test_no_false_live_claims()
    print("ALL_PASS test_explorers_league_community_spine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
