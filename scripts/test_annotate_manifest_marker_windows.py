#!/usr/bin/env python3
"""Fixture regression for source-bound manifest marker windows."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from annotate_manifest_marker_windows import annotate  # noqa: E402


def main() -> int:
    manifest = {
        "files": [
            {
                "filename": "a.mp4",
                "source_master": r"D:\Capture\master-a.mp4",
                "duration_sec": 30,
                "extract": {"start_sec": 10},
            },
            {
                "filename": "b.mp4",
                "source_master": r"D:\Capture\master-b.mp4",
                "duration_sec": 20,
                "extract": {"start_sec": 0},
            },
        ]
    }
    joined = {
        "record_start_weak": True,
        "obs_chapters_by_master": {
            "master-a.mp4": [
                {
                    "kind": "obs_chapter",
                    "start_sec": 15,
                    "end_sec": 25,
                    "press_evidence_only": True,
                }
            ]
        },
    }
    result, summary = annotate(manifest, joined)
    a, b = result["files"]
    assert a["marker_window"]["status"] == "MATCHED_SOURCE_MASTER"
    assert a["marker_window"]["windows"] == [
        {
            "kind": "obs_chapter",
            "start_sec": 5.0,
            "end_sec": 15.0,
            "press_evidence_only": True,
        }
    ]
    assert b["marker_window"]["status"] == "NO_ADMISSIBLE_WINDOW"
    assert b["marker_window"]["windows"] == []
    assert summary == {
        "files_annotated": 2,
        "files_with_windows": 1,
        "matched_windows": 1,
        "record_start_weak": True,
    }
    print("ALL_PASS SOURCE_MASTER_MATCH EMPTY_EXPLICIT WEAK_DECK_EXCLUDED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
