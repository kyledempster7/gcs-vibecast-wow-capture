#!/usr/bin/env python3
"""Drive build_league_pitch_storyboard.py on real pack files."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
BUILD = SCRIPTS / "build_league_pitch_storyboard.py"
WOW = SCRIPTS.parent.parent
PACK = WOW / "04-Story-and-Capture" / "social" / "EXPLORERS_LEAGUE_PITCH_BROLL_PACK.md"
FLASH = (
    WOW
    / "04-Story-and-Capture"
    / "hyperframes-brand-kit"
    / "slots"
    / "league-pitch-flash"
    / "index.html"
)


def test_build_storyboard() -> None:
    assert PACK.is_file(), PACK
    assert FLASH.is_file(), FLASH
    out = Path(tempfile.mkdtemp()) / "storyboard.json"
    r = subprocess.run(
        [sys.executable, str(BUILD), "--out", str(out), "--pack", str(PACK)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "storyboard OK" in r.stdout
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc.get("armed") is False
    assert doc.get("kyle_go") is False
    assert doc.get("product_id") == "twe_explorers_league_community_pitch_v1"
    assert len(doc.get("flash_cards") or []) >= 3
    assert len(doc.get("shots") or []) >= 1
    assert len(doc.get("sequence") or []) >= 3
    # no invent: media_path always None until filled
    assert all(s.get("media_path") is None for s in doc["shots"])
    assert doc.get("ready_to_edit") is False
    print(
        f"PASS build_storyboard flash={len(doc['flash_cards'])} shots={len(doc['shots'])}"
    )


def test_flash_html_ids() -> None:
    html = FLASH.read_text(encoding="utf-8")
    for fid in (
        "flash.welcome",
        "flash.fair",
        "flash.dungeons",
        "flash.not_alone",
        "flash.discord_door",
    ):
        assert fid in html, fid
    print("PASS flash_html_ids")


def main() -> int:
    test_build_storyboard()
    test_flash_html_ids()
    print("ALL_PASS test_league_pitch_storyboard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
