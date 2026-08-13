#!/usr/bin/env python3
"""Unit tests for harvest completeness helper. No invent. No harvest."""
from __future__ import annotations

import json
from pathlib import Path

import harvest_completeness as hc


def test_completeness_math() -> None:
    assert hc.completeness.__doc__ is None or True
    status, mac_n, win_n = hc.completeness("2026-08-12")
    print(f"live 2026-08-12 status={status} mac={mac_n} win={win_n}")
    assert status in ("complete", "incomplete", "unknown")
    assert mac_n >= 0
    if win_n is not None and mac_n >= win_n and mac_n > 0:
        assert status == "complete"
    if win_n is not None and mac_n < win_n:
        assert status == "incomplete"


def test_write_live(tmp_path: Path | None = None) -> None:
    path = hc.write_live("2026-08-12")
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("day") == "2026-08-12"
    assert "mac_mp4_n" in data
    assert data.get("armed") is False
    print("PASS write_live", path)


def main() -> int:
    test_completeness_math()
    test_write_live()
    print("ALL_PASS test_harvest_completeness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
