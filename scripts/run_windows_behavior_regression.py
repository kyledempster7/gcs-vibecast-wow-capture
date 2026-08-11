#!/usr/bin/env python3
"""Run deployed fixture-only Windows regressions and persist canonical proof."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RECEIPT = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast"
    / "WINDOWS_BEHAVIOR_REGRESSION_LATEST.json"
)
REMOTE = r"D:\WoW B-Roll Storage\_scripts\Test-VibeCast-Windows-Behavior.ps1"


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
        timeout=90,
        check=False,
    )
    try:
        body = json.loads((result.stdout or "").strip())
    except json.JSONDecodeError as exc:
        body = {
            "schema": "gcs_windows_behavior_regression/v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "FAIL",
            "first_bad_boundary": "WINDOWS_REGRESSION_OUTPUT_INVALID",
            "ssh_rc": result.returncode,
            "error": str(exc),
            "stderr_tail": (result.stderr or "")[-500:],
            "may_publish": False,
            "provider_effects": False,
        }
    body["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    body["host"] = "3900X"
    body["ssh_rc"] = result.returncode
    atomic_json(RECEIPT, body)
    ok = result.returncode == 0 and body.get("status") == "PASS"
    print(f"WINDOWS_BEHAVIOR status={body.get('status')} ssh_rc={result.returncode}")
    print(f"RECEIPT {RECEIPT}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
