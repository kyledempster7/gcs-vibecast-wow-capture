#!/usr/bin/env python3
"""Fixtures for join_markers.py — paired windows, talk pad, skip zones.

Codex fold 2026-08-10: prove contract before Export interval port.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
JOIN = SCRIPTS / "join_markers.py"
FIXTURE = SCRIPTS.parent / "fixtures" / "markers" / "session_paired.jsonl"


def run_join(markers: Path) -> dict:
    out = Path(tempfile.mkdtemp()) / "join.json"
    r = subprocess.run(
        [sys.executable, str(JOIN), "--markers", str(markers), "--out", str(out)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr or r.stdout
    return json.loads(out.read_text(encoding="utf-8"))


def test_empty_markers() -> None:
    empty = Path(tempfile.mkdtemp()) / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    rep = run_join(empty)
    assert rep.get("status") in ("EMPTY_MARKERS", "NO_WINDOWS") or rep.get("windows") == []
    print("PASS empty")


def test_paired_and_pads() -> None:
    assert FIXTURE.is_file(), FIXTURE
    rep = run_join(FIXTURE)
    assert rep.get("status") == "OK", rep
    wins = rep.get("windows") or []
    skips = rep.get("skip_zones") or []
    by_kind = {}
    for w in wins:
        by_kind.setdefault(w["kind"], []).append(w)

    # broll 10→40
    assert by_kind.get("broll"), wins
    b = by_kind["broll"][0]
    assert abs(b["start_sec"] - 10.0) < 0.01
    assert abs(b["end_sec"] - 40.0) < 0.01

    # rotate 50→65
    assert by_kind.get("rotate"), wins
    r = by_kind["rotate"][0]
    assert abs(r["start_sec"] - 50.0) < 0.01
    assert abs(r["end_sec"] - 65.0) < 0.01

    # talk_peak at 80s with default pad 15 → 65–95
    assert by_kind.get("talk_peak"), wins
    t = by_kind["talk_peak"][0]
    assert t["start_sec"] <= 80.0
    assert t["end_sec"] >= 80.0
    assert (t["end_sec"] - t["start_sec"]) >= 29.0  # ~30s with 15 pad each side

    # skip at 90 ±5 → around 85–95
    assert skips, rep
    s = skips[0]
    assert s["start_sec"] <= 90.0 <= s["end_sec"]

    # gather_broll 120→145
    gb = [w for w in wins if w.get("kind") == "gather_broll"]
    assert gb, wins
    assert abs(gb[0]["start_sec"] - 120.0) < 0.01
    assert abs(gb[0]["end_sec"] - 145.0) < 0.01

    # skip overlap with talk: talk window and skip both cover ~90
    talk = by_kind["talk_peak"][0]
    assert not (talk["end_sec"] < s["start_sec"] or talk["start_sec"] > s["end_sec"]), (
        "expected talk and skip to overlap for export reject tests"
    )
    print("PASS paired pads skip gather")


def main() -> int:
    test_empty_markers()
    test_paired_and_pads()
    print("ALL join_markers fixtures PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
