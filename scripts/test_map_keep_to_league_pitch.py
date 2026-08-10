#!/usr/bin/env python3
"""Drive map_keep_to_league_pitch.py fail-closed + attach real path."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
MAP = SCRIPTS / "map_keep_to_league_pitch.py"
WOW = SCRIPTS.parent.parent
STORY = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_STORYBOARD.json"
)


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MAP), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_skip_no_keep() -> None:
    tmp = Path(tempfile.mkdtemp())
    (tmp / "analysis").mkdir()
    (tmp / "analysis" / "human_verdicts.json").write_text(
        json.dumps({"verdicts": {"a": {"verdict": "REJECT", "reason": "x"}}}),
        encoding="utf-8",
    )
    r = run("--day-dir", str(tmp), "--auto-suggest", "--apply")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "SKIP no_KEEP" in r.stdout
    print("PASS skip_no_keep")


def test_attach_explicit() -> None:
    assert STORY.is_file(), STORY
    tmp = Path(tempfile.mkdtemp())
    analysis = tmp / "analysis"
    cand = tmp / "candidates"
    analysis.mkdir()
    cand.mkdir()
    clip = cand / "db-20260810-c-full-test.mp4"
    clip.write_bytes(b"\x00\x00\x00\x18ftypmp42")
    (analysis / "human_verdicts.json").write_text(
        json.dumps(
            {
                "schema": "gcs_human_verdicts/v1",
                "verdicts": {
                    "c": {"verdict": "KEEP", "reason": "hub establish test", "source": "t"}
                },
            }
        ),
        encoding="utf-8",
    )
    # copy storyboard to temp so we don't thrash product board mid-test
    sb = tmp / "storyboard.json"
    sb.write_text(STORY.read_text(encoding="utf-8"), encoding="utf-8")
    r = run(
        "--day-dir",
        str(tmp),
        "--storyboard",
        str(sb),
        "--map",
        "c=pitch.hub_thrall",
        "--apply",
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ATTACH c -> pitch.hub_thrall" in r.stdout, r.stdout
    doc = json.loads(sb.read_text(encoding="utf-8"))
    assert doc.get("armed") is False
    hub = next(s for s in doc["shots"] if s["shot_id"] == "pitch.hub_thrall")
    assert hub.get("captured") is True
    assert hub.get("media_path") and Path(hub["media_path"]).is_file()
    print("PASS attach_explicit")


def test_missing_file_skips() -> None:
    tmp = Path(tempfile.mkdtemp())
    analysis = tmp / "analysis"
    analysis.mkdir()
    (tmp / "candidates").mkdir()
    (analysis / "human_verdicts.json").write_text(
        json.dumps(
            {
                "verdicts": {
                    "c": {"verdict": "KEEP", "reason": "gather herb", "source": "t"}
                }
            }
        ),
        encoding="utf-8",
    )
    sb = tmp / "storyboard.json"
    sb.write_text(STORY.read_text(encoding="utf-8"), encoding="utf-8")
    before = json.loads(sb.read_text())["captured_n"]
    r = run(
        "--day-dir",
        str(tmp),
        "--storyboard",
        str(sb),
        "--auto-suggest",
        "--apply",
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "missing_file" in r.stdout or "attached=0" in r.stdout
    after = json.loads(sb.read_text())["captured_n"]
    # no phantom capture
    assert after == before or after == 0 or "ATTACH" not in r.stdout
    print("PASS missing_file_no_invent")


def main() -> int:
    test_skip_no_keep()
    test_attach_explicit()
    test_missing_file_skips()
    print("ALL_PASS test_map_keep_to_league_pitch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
