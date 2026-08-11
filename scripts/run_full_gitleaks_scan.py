#!/usr/bin/env python3
"""Run redacted governed secret scans over full Git history and Games/WoW."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CONFIG = Path(
    "/Users/kyle/Library/Application Support/UAH/butler/control-plane/"
    "tools/custody_gitleaks.toml"
)
RECEIPT = Path(
    "/Users/kyle/Library/Application Support/UAH/butler/control-plane/"
    "receipts/gcs-vibecast/GITLEAKS_FULL_SCAN_LATEST.json"
)


def run(args: list[str], timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def parse_metric(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None


def atomic_json(path: Path, body: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    binary = shutil.which("gitleaks")
    if not binary or not CONFIG.is_file():
        raise SystemExit("gitleaks binary or governed config missing")
    with tempfile.TemporaryDirectory(prefix="gcs-gitleaks-") as temp:
        scratch = Path(temp)
        history_report = scratch / "history.json"
        tree_report = scratch / "tree.json"
        common = [
            binary,
            "--no-banner",
            "--no-color",
            "--redact=100",
            "--config",
            str(CONFIG),
            "--report-format",
            "json",
        ]
        history = run(
            common
            + ["--report-path", str(history_report), "git", "--log-opts=--all", str(ROOT)]
        )
        tree = run(
            common
            + ["--report-path", str(tree_report), "dir", str(ROOT / "Games/WoW")]
        )
        history_findings = json.loads(history_report.read_text()) if history_report.is_file() else []
        tree_findings = json.loads(tree_report.read_text()) if tree_report.is_file() else []

    head = run(["git", "rev-parse", "HEAD"], 10).stdout.strip()
    branch = run(["git", "branch", "--show-current"], 10).stdout.strip()
    version = run([binary, "version"], 10).stdout.strip()
    history_log = (history.stdout or "") + (history.stderr or "")
    tree_log = (tree.stdout or "") + (tree.stderr or "")
    ok = (
        history.returncode == 0
        and tree.returncode == 0
        and not history_findings
        and not tree_findings
    )
    body = {
        "schema": "gcs_vibecast_gitleaks_scan/v1",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "PASS" if ok else "FAIL",
        "root": str(ROOT),
        "branch": branch,
        "head": head,
        "gitleaks_version": version,
        "scanner_config": str(CONFIG),
        "scanner_config_sha256": hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        "history": {
            "scope": "--all",
            "commits_scanned": parse_metric(history_log, r"(\d+) commits scanned"),
            "bytes_scanned": parse_metric(history_log, r"scanned ~?(\d+) bytes"),
            "findings": len(history_findings),
            "status": "PASS" if history.returncode == 0 and not history_findings else "FAIL",
            "proof_mode": "single_full_history_scan",
            "rc": history.returncode,
        },
        "working_tree": {
            "scope": "Games/WoW",
            "bytes_scanned": parse_metric(tree_log, r"scanned ~?(\d+) bytes"),
            "findings": len(tree_findings),
            "status": "PASS" if tree.returncode == 0 and not tree_findings else "FAIL",
            "rc": tree.returncode,
        },
        "redacted_output": True,
        "secret_values_logged": False,
        "may_publish": False,
        "provider_effects": False,
    }
    atomic_json(RECEIPT, body)
    print(
        f"GITLEAKS status={body['status']} history={len(history_findings)} "
        f"working_tree={len(tree_findings)} head={head[:12]}"
    )
    print(f"RECEIPT {RECEIPT}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
