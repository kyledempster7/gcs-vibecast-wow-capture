#!/usr/bin/env python3
"""Read-only SHA-256 parity proof for deployed Windows VibeCast scripts.

No deploy, install, browser, arm, or publish action occurs. The script reads
the live Mac source and the existing Windows copies over batch-mode SSH.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath


LIVE_SCRIPTS = Path(__file__).resolve().parent
REMOTE_ROOT = r"D:\WoW B-Roll Storage\_scripts"
RECEIPT = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast"
    / "WINDOWS_SCRIPT_HASH_PARITY_LATEST.json"
)
FILES = (
    "Append-StreamDeckMarker.ps1",
    "Export-ShipCandidates.ps1",
    "Stage-ShipCandidates.ps1",
    "soft_poll_windows.ps1",
    "Install-InboxTasks.ps1",
    "Install-RemainingTasks.ps1",
    "Install-GCS-ShipTasks.ps1",
    "Install-LayerC-DeckMarkers.ps1",
    "Configure-WoW-BRoll-OBS.ps1",
    "Move-TodayMastersToDayRoot.ps1",
    "Session-End-Ship.ps1",
    "Auto-Session-End-If-Masters.ps1",
    "Gcs-SessionEnd-Guards.ps1",
    "Windows-Preflight.ps1",
    "Windows-Resume-Readiness.ps1",
    "Run-NightlyInboxes.ps1",
    "Run-CaptureInbox.ps1",
    "Run-MementoInbox.ps1",
    "Run-EngineHealth.ps1",
    "check_disk_headroom.ps1",
    "Windows-Agent-Boot.ps1",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_receipt(body: dict) -> None:
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from resolve_windows_host import ssh_host

    host = ssh_host()
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    missing = [name for name in FILES if not (LIVE_SCRIPTS / name).is_file()]
    if missing:
        body = {
            "schema": "gcs_windows_script_hash_parity/v1",
            "utc": utc,
            "status": "FAIL",
            "first_bad_boundary": "LOCAL_SOURCE_MISSING",
            "missing": missing,
            "may_publish": False,
            "provider_effects": False,
        }
        write_receipt(body)
        print(f"FAIL local source missing: {missing}", file=sys.stderr)
        return 2

    quoted_paths = ",".join(
        "'" + REMOTE_ROOT + "\\" + name.replace("'", "''") + "'"
        for name in FILES
    )
    ps = (
        "$ErrorActionPreference='Stop'; "
        f"@(Get-FileHash -Algorithm SHA256 {quoted_paths} | "
        "Select-Object Path,Hash) | ConvertTo-Json -Compress"
    )
    remote_command = f'powershell -NoProfile -Command "{ps}"'
    result = subprocess.run(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=20",
            host,
            remote_command,
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=45,
    )
    if result.returncode != 0:
        body = {
            "schema": "gcs_windows_script_hash_parity/v1",
            "utc": utc,
            "status": "FAIL",
            "first_bad_boundary": "WINDOWS_HASH_READBACK_FAILED",
            "ssh_rc": result.returncode,
            "stderr_tail": (result.stderr or "")[-500:],
            "may_publish": False,
            "provider_effects": False,
        }
        write_receipt(body)
        print(json.dumps(body, indent=2), file=sys.stderr)
        return 2

    try:
        decoded = json.loads((result.stdout or "").strip())
    except json.JSONDecodeError as exc:
        body = {
            "schema": "gcs_windows_script_hash_parity/v1",
            "utc": utc,
            "status": "FAIL",
            "first_bad_boundary": "WINDOWS_HASH_JSON_INVALID",
            "error": str(exc),
            "may_publish": False,
            "provider_effects": False,
        }
        write_receipt(body)
        print(json.dumps(body, indent=2), file=sys.stderr)
        return 2

    remote_rows = decoded if isinstance(decoded, list) else [decoded]
    remote_hashes = {
        PureWindowsPath(str(row.get("Path") or "")).name: str(row.get("Hash") or "").lower()
        for row in remote_rows
        if isinstance(row, dict)
    }
    rows = []
    for name in FILES:
        local_hash = sha256(LIVE_SCRIPTS / name)
        remote_hash = remote_hashes.get(name, "")
        rows.append(
            {
                "file": name,
                "local_sha256": local_hash,
                "remote_sha256": remote_hash or None,
                "match": bool(remote_hash) and local_hash == remote_hash,
            }
        )
    all_match = len(rows) == len(FILES) and all(row["match"] for row in rows)
    body = {
        "schema": "gcs_windows_script_hash_parity/v1",
        "utc": utc,
        "status": "PASS" if all_match else "FAIL",
        "source_root": str(LIVE_SCRIPTS),
        "remote_root": REMOTE_ROOT,
        "file_count": len(rows),
        "all_match": all_match,
        "rows": rows,
        "first_bad_boundary": None if all_match else "WINDOWS_SOURCE_DEPLOY_HASH_DRIFT",
        "may_publish": False,
        "provider_effects": False,
        "mutation": "none_read_only_hash_readback",
    }
    write_receipt(body)
    print(f"HASH_PARITY status={body['status']} files={len(rows)} all_match={all_match}")
    print(f"RECEIPT {RECEIPT}")
    return 0 if all_match else 2


if __name__ == "__main__":
    raise SystemExit(main())
