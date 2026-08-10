#!/usr/bin/env python3
"""Drive stitch_league_pitch_dry.py on real storyboard with residual media."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
STITCH = SCRIPTS / "stitch_league_pitch_dry.py"
STORY = (
    SCRIPTS.parents[1]
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_STORYBOARD.json"
)
OUT = (
    SCRIPTS.parents[1]
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "pitch-montage-dry"
)


def main() -> int:
    assert STORY.is_file(), STORY
    board = json.loads(STORY.read_text(encoding="utf-8"))
    n_cap = sum(1 for s in board.get("shots") or [] if s.get("captured") and s.get("media_path"))
    r = subprocess.run(
        [sys.executable, str(STITCH), "--storyboard", str(STORY), "--out-dir", str(OUT)],
        capture_output=True,
        text=True,
        check=False,
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr[-400:], file=sys.stderr)
    assert r.returncode == 0, r.returncode
    meta_p = OUT / "STITCH_DRY.json"
    assert meta_p.is_file(), meta_p
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    assert meta.get("armed") is False
    if n_cap >= 2:
        assert meta.get("status") == "DRY_OK", meta
        out_mp4 = Path(meta["out_mp4"])
        assert out_mp4.is_file() and out_mp4.stat().st_size > 1000
        print(f"PASS dry_ok bytes={out_mp4.stat().st_size}")
    else:
        assert meta.get("status") in ("INSUFFICIENT_CLIPS", "INSUFFICIENT_TRIMS")
        print(f"PASS insufficient_ok status={meta.get('status')}")
    print("ALL_PASS test_stitch_league_pitch_dry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
