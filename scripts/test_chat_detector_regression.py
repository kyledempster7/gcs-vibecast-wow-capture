#!/usr/bin/env python3
"""Regression proof for conditional chat blur on real archived media."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from detect_chat_presence import detect  # noqa: E402

DEFAULT_CLEAN = Path(
    "/Users/kyle/Movies/WoW-Broll-Workflow/Moments-Library/"
    "2026-08-09-dragonblight/clips/c-pride-15s-start.mp4"
)
DEFAULT_VISIBLE = Path(
    "/Users/kyle/Movies/WoW-Broll-Workflow/Returns/"
    "returner-daily-2026-08-09/candidates/wow-20260809-223313-start30.mp4"
)
DEFAULT_RECEIPT = Path(
    "/Users/kyle/Library/Application Support/UAH/butler/control-plane/"
    "receipts/gcs-vibecast/CHAT_DETECTOR_REGRESSION_LATEST.json"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", type=Path, default=DEFAULT_CLEAN)
    ap.add_argument("--visible-chat", type=Path, default=DEFAULT_VISIBLE)
    ap.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = ap.parse_args()

    missing = [str(p) for p in (args.clean, args.visible_chat) if not p.is_file()]
    if missing:
        print(json.dumps({"status": "FAIL", "missing": missing}, indent=2))
        return 2

    clean = detect(args.clean)
    visible = detect(args.visible_chat)
    checks = {
        "clean_orbit_false": clean.get("chat_present") is False,
        "visible_chat_true": visible.get("chat_present") is True,
    }

    with tempfile.TemporaryDirectory(prefix="chatblur_regression_") as tmp:
        tmp_dir = Path(tmp)
        out = tmp_dir / "clean-passthrough.mp4"
        det = tmp_dir / "clean-detect.json"
        run = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "apply_chat_blur.py"),
                "--src",
                str(args.clean),
                "--out",
                str(out),
                "--detect-out",
                str(det),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        try:
            action = json.loads(run.stdout)
        except json.JSONDecodeError:
            action = {}
        checks["passthrough_action"] = (
            run.returncode == 0 and action.get("action") == "passthrough_no_blur"
        )
        checks["passthrough_hash_match"] = (
            out.is_file() and sha256(args.clean) == sha256(out)
        )

    status = "PASS" if all(checks.values()) else "FAIL"
    body = {
        "schema": "gcs_chat_detector_regression/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "checks": checks,
        "clean_fixture": {
            "path": str(args.clean),
            "expected_chat_present": False,
            "actual_chat_present": clean.get("chat_present"),
            "frames_hot": clean.get("frames_hot"),
            "frames_need": clean.get("frames_need"),
        },
        "visible_chat_fixture": {
            "path": str(args.visible_chat),
            "expected_chat_present": True,
            "actual_chat_present": visible.get("chat_present"),
            "frames_hot": visible.get("frames_hot"),
            "frames_need": visible.get("frames_need"),
        },
        "policy": "blur_only_if_chat_present_or_force",
        "may_publish": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    tmp_receipt = args.receipt.with_suffix(args.receipt.suffix + ".tmp")
    tmp_receipt.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    tmp_receipt.replace(args.receipt)
    if status == "PASS":
        print("ALL_PASS CLEAN_ORBIT_FALSE VISIBLE_CHAT_TRUE PASSTHROUGH_HASH_MATCH")
        print(f"RECEIPT {args.receipt}")
        return 0
    print(json.dumps(body, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
