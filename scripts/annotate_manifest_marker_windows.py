#!/usr/bin/env python3
"""Attach source-bound marker-window truth to a VibeCast candidate manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

DEFAULT_RECEIPT = Path(
    "/Users/kyle/Library/Application Support/UAH/butler/control-plane/"
    "receipts/gcs-vibecast/MANIFEST_MARKER_WINDOWS_LATEST.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, body: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def basename(value: str) -> str:
    return PureWindowsPath(value).name if value else ""


def annotate(manifest: dict, joined: dict) -> tuple[dict, dict]:
    files = manifest.get("files")
    if not isinstance(files, list):
        raise ValueError("manifest.files must be a list")
    chapters_by_master = joined.get("obs_chapters_by_master") or {}
    weak = joined.get("record_start_weak") is True
    matched_files = 0
    matched_windows = 0

    for item in files:
        if not isinstance(item, dict):
            continue
        source = basename(str(item.get("source_master") or ""))
        extract = item.get("extract") or {}
        start = float(extract.get("start_sec") or 0.0)
        duration = float(item.get("duration_sec") or extract.get("requested_duration_sec") or 0.0)
        end = start + max(0.0, duration)
        windows = []
        for row in chapters_by_master.get(source, []):
            if not isinstance(row, dict):
                continue
            w_start = float(row.get("start_sec") or 0.0)
            w_end = float(row.get("end_sec") or 0.0)
            left = max(start, w_start)
            right = min(end, w_end)
            if right <= left:
                continue
            windows.append(
                {
                    "kind": str(row.get("kind") or "obs_chapter"),
                    "start_sec": round(left - start, 3),
                    "end_sec": round(right - start, 3),
                    "press_evidence_only": row.get("press_evidence_only", True),
                }
            )
        if windows:
            matched_files += 1
            matched_windows += len(windows)
            status = "MATCHED_SOURCE_MASTER"
            reason = "embedded OBS chapter intersected this candidate extract"
        else:
            status = "NO_ADMISSIBLE_WINDOW"
            reason = (
                "no source-master OBS chapter intersects this extract; "
                "weak or cross-master deck timing is excluded"
            )
        item["marker_window"] = {
            "schema": "gcs_manifest_marker_window/v1",
            "status": status,
            "source_master": source or None,
            "windows": windows,
            "record_start_weak": weak,
            "reason": reason,
        }

    summary = {
        "files_annotated": len([x for x in files if isinstance(x, dict)]),
        "files_with_windows": matched_files,
        "matched_windows": matched_windows,
        "record_start_weak": weak,
    }
    manifest["marker_join"] = {
        "schema": "gcs_manifest_marker_join_summary/v1",
        **summary,
        "policy": "source_master_chapters_only; no_cross_master_inference",
    }
    return manifest, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--join", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = ap.parse_args()
    if args.in_place and args.out:
        raise SystemExit("--in-place and --out are mutually exclusive")
    if not args.manifest.is_file() or not args.join.is_file():
        print("FAIL missing manifest or marker join")
        return 2

    manifest_hash = sha256(args.manifest)
    join_hash = sha256(args.join)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    joined = json.loads(args.join.read_text(encoding="utf-8"))
    result, summary = annotate(manifest, joined)
    target = args.manifest if args.in_place else (args.out or args.manifest.with_name("MANIFEST.marker-windows.json"))
    atomic_json(target, result)
    receipt = {
        "schema": "gcs_manifest_marker_windows_receipt/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "manifest": str(args.manifest),
        "manifest_input_sha256": manifest_hash,
        "marker_join": str(args.join),
        "marker_join_sha256": join_hash,
        "output": str(target),
        **summary,
        "may_publish": False,
        "invention": "none",
    }
    atomic_json(args.receipt, receipt)
    print(
        "PASS "
        f"files={summary['files_annotated']} "
        f"with_windows={summary['files_with_windows']} "
        f"windows={summary['matched_windows']}"
    )
    print(f"RECEIPT {args.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
