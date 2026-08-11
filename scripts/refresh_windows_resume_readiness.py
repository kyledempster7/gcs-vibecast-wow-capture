#!/usr/bin/env python3
"""Refresh canonical Windows resume truth from the deployed read-only probe."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RECEIPT = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast"
    / "WINDOWS_RESUME_READINESS_LATEST.json"
)
REMOTE = r"D:\WoW B-Roll Storage\_scripts\Windows-Resume-Readiness.ps1"


def atomic_json(path: Path, body: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    from resolve_windows_host import ssh_host

    result = subprocess.run(
        [
            "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", ssh_host(),
            f'powershell -NoProfile -ExecutionPolicy Bypass -File "{REMOTE}"',
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    try:
        body = json.loads((result.stdout or "").strip())
    except json.JSONDecodeError as exc:
        body = {
            "schema": "gcs_windows_resume_readiness/v1",
            "status": "FAIL",
            "first_bad_boundary": "WINDOWS_READINESS_OUTPUT_INVALID",
            "error": str(exc),
            "stderr_tail": (result.stderr or "")[-800:],
            "may_publish": False,
        }
    profile = body.get("profile") or {}
    settings = profile.get("settings") or {}
    addon = body.get("auto_hide_ui") or {}
    deck = body.get("stream_deck") or {}
    ready = (
        result.returncode == 0
        and str(body.get("host") or "").upper() == "3900X"
        and profile.get("product_path_ok") is True
        and settings.get("Mode") == "Advanced"
        and settings.get("RecTracks") == "7"
        and addon.get("installed") is True
        and addon.get("configured") is True
        and addon.get("active_profile_is_gather") is True
        and addon.get("original_backup_exists") is True
        and deck.get("command_sheet_exists") is True
        and (body.get("resume_card") or {}).get("exists") is True
    )
    body["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    body["status"] = "READY_FOR_HUMAN_CAPTURE" if ready else "FAIL"
    body["first_bad_boundary"] = (
        "HUMAN_AUDIO_AND_REAL_CAPTURE_REQUIRED" if ready else "WINDOWS_RESUME_CONFIGURATION_INCOMPLETE"
    )
    body["ssh_rc"] = result.returncode
    body["may_publish"] = False
    body["provider_effects"] = False
    atomic_json(RECEIPT, body)
    print(f"WINDOWS_RESUME status={body['status']} host={body.get('host')} boundary={body['first_bad_boundary']}")
    print(f"RECEIPT {RECEIPT}")
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
