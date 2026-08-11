#!/usr/bin/env python3
"""Audit or apply the guarded Windows AutoHideUI VibeCast profiles."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RECEIPT = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast"
    / "AUTOHIDEUI_CONFIG_LATEST.json"
)
REMOTE = r"D:\WoW B-Roll Storage\_scripts\Configure-VibeCast-AutoHideUI.ps1"


def atomic_json(path: Path, body: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply offline profiles; default is audit-only")
    args = parser.parse_args()

    from resolve_windows_host import ssh_host

    mode = "" if args.apply else " -AuditOnly"
    result = subprocess.run(
        [
            "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", ssh_host(),
            f'powershell -NoProfile -ExecutionPolicy Bypass -File "{REMOTE}"{mode}',
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
            "schema": "gcs_autohideui_config/v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "FAIL",
            "state": "OUTPUT_INVALID",
            "first_bad_boundary": "AUTOHIDEUI_CONFIG_OUTPUT_INVALID",
            "error": str(exc),
            "stderr_tail": (result.stderr or "")[-800:],
            "may_publish": False,
            "provider_effects": False,
        }
    body["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    body["host"] = "3900X"
    body["ssh_rc"] = result.returncode
    atomic_json(RECEIPT, body)
    ok = result.returncode == 0 and body.get("status") == "PASS"
    print(f"AUTOHIDEUI status={body.get('status')} state={body.get('state')} ssh_rc={result.returncode}")
    print(f"RECEIPT {RECEIPT}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
