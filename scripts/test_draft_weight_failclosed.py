#!/usr/bin/env python3
"""Drive real draft_daily_personality_package.py + write_weight_row.py fail-closed paths.

No invent FOOTAGE. No publish. Law: SKIP without KEEP; armed always false with KEEP.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
DRAFT = SCRIPTS / "draft_daily_personality_package.py"
WEIGHT = SCRIPTS / "write_weight_row.py"
REAL_KEEP_DAY = (
    Path.home() / "Movies/WoW-Broll-Workflow/Returns/returner-daily-2026-08-09"
)


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_skip_no_keep() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="gcs_draft_skip_"))
    analysis = tmp / "analysis"
    analysis.mkdir(parents=True)
    (analysis / "human_verdicts.json").write_text(
        json.dumps(
            {
                "schema": "gcs_human_verdicts/v1",
                "verdicts": {
                    "x": {"verdict": "REJECT", "reason": "load", "source": "test"}
                },
            }
        ),
        encoding="utf-8",
    )
    r = run(DRAFT, "--day-dir", str(tmp))
    assert r.returncode == 0, r.stderr or r.stdout
    assert "SKIP" in (r.stdout + r.stderr), r.stdout
    assert not (tmp / "package" / "DAILY_PERSONALITY_DRAFT.md").is_file()
    print("PASS skip_no_keep")


def test_skip_empty_verdicts_weight() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="gcs_weight_skip_"))
    analysis = tmp / "analysis"
    analysis.mkdir(parents=True)
    (analysis / "human_verdicts.json").write_text("{}", encoding="utf-8")
    r = run(WEIGHT, "--day-dir", str(tmp))
    assert r.returncode == 0, r.stderr or r.stdout
    assert "SKIP" in (r.stdout + r.stderr), r.stdout
    print("PASS skip_empty_weight")


def test_weight_and_draft_from_temp_keep() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="gcs_keep_"))
    analysis = tmp / "analysis"
    cand = tmp / "candidates"
    analysis.mkdir(parents=True)
    cand.mkdir(parents=True)
    # minimal fake media file the resolver can find by short id "c"
    clip = cand / "db-20260810-c-full-test.mp4"
    clip.write_bytes(b"\x00\x00\x00\x18ftypmp42")  # tiny not-real-mp4 bytes; path must exist
    (analysis / "human_verdicts.json").write_text(
        json.dumps(
            {
                "schema": "gcs_human_verdicts/v1",
                "verdicts": {
                    "c": {
                        "verdict": "KEEP",
                        "reason": "unit test keep",
                        "source": "test",
                    },
                    "z": {
                        "verdict": "REJECT",
                        "reason": "unit test reject",
                        "source": "test",
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    rw = run(WEIGHT, "--day-dir", str(tmp), "--note", "unit")
    assert rw.returncode == 0, rw.stderr or rw.stdout
    assert "write_weight OK" in rw.stdout, rw.stdout
    wpath = analysis / "WEIGHT.json"
    assert wpath.is_file(), wpath
    wdoc = json.loads(wpath.read_text(encoding="utf-8"))
    assert wdoc["rows"][-1]["keep_n"] == 1
    assert wdoc["rows"][-1]["reject_n"] == 1

    rd = run(DRAFT, "--day-dir", str(tmp), "--force")
    assert rd.returncode == 0, rd.stderr or rd.stdout
    assert "draft_personality OK" in rd.stdout, rd.stdout
    media = json.loads((tmp / "package" / "MEDIA_MAP.json").read_text(encoding="utf-8"))
    assert media.get("armed") is False
    assert media.get("not_class_p") is True
    assert any(v.get("id") == "c" and v.get("exists") for v in media.get("videos") or [])
    draft = (tmp / "package" / "DAILY_PERSONALITY_DRAFT.md").read_text(encoding="utf-8")
    assert "NOT_ARMED" in draft or "Armed:** false" in draft or "armed" in draft.lower()
    assert "Class-P" in draft or "not Class-P" in draft
    print("PASS weight_and_draft_temp_keep")


def test_real_keep_day_if_present() -> None:
    """Optional integration: residual KEEP day on disk (no invent)."""
    if not (REAL_KEEP_DAY / "analysis" / "human_verdicts.json").is_file():
        print("SKIP real_keep_day absent")
        return
    r = run(DRAFT, "--day-dir", str(REAL_KEEP_DAY), "--force")
    assert r.returncode == 0, r.stderr or r.stdout
    assert "draft_personality OK" in r.stdout or "exists" in r.stdout, r.stdout
    media_path = REAL_KEEP_DAY / "package" / "MEDIA_MAP.json"
    assert media_path.is_file(), media_path
    media = json.loads(media_path.read_text(encoding="utf-8"))
    assert media.get("armed") is False
    print("PASS real_keep_day armed=false")


def main() -> int:
    test_skip_no_keep()
    test_skip_empty_verdicts_weight()
    test_weight_and_draft_from_temp_keep()
    test_real_keep_day_if_present()
    print("ALL_PASS test_draft_weight_failclosed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
