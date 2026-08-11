#!/usr/bin/env python3
"""Fail a Git commit when staged Windows scripts are not deployed byte-for-byte."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PREFIX = "Games/WoW/wow-roster-tracker/scripts/"


def windows_paths(paths: list[str]) -> list[str]:
    return sorted(
        path
        for path in paths
        if path.startswith(PREFIX) and path.endswith(".ps1")
    )


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("GIT_DIR", None)
    env.pop("GIT_WORK_TREE", None)
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    if "--self-test" in sys.argv:
        sample = [PREFIX + "Export-ShipCandidates.ps1", PREFIX + "notes.md", "other.ps1"]
        assert windows_paths(sample) == [PREFIX + "Export-ShipCandidates.ps1"]
        print("ALL_PASS WINDOWS_PATH_FILTER")
        return 0

    root_result = run(["git", "rev-parse", "--show-toplevel"], Path.cwd())
    if root_result.returncode != 0:
        print("WINDOWS_PARITY_GATE no git root", file=sys.stderr)
        return 2
    root = Path(root_result.stdout.strip())
    staged_result = run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        root,
    )
    staged = windows_paths(staged_result.stdout.splitlines())
    if not staged:
        print("WINDOWS_PARITY_GATE skip no staged ps1")
        return 0

    unstaged = run(["git", "diff", "--quiet", "--", *staged], root)
    if unstaged.returncode != 0:
        print("WINDOWS_PARITY_GATE blocked: staged PS1 also has unstaged bytes", file=sys.stderr)
        return 2

    verifier = root / PREFIX / "verify_windows_script_hash_parity.py"
    result = subprocess.run(
        [sys.executable, str(verifier)],
        cwd=verifier.parent,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(
            "WINDOWS_PARITY_GATE blocked: deploy the staged PS1 set with "
            "deploy_windows_scripts.sh, then commit",
            file=sys.stderr,
        )
        return 2
    print(f"WINDOWS_PARITY_GATE PASS staged_ps1={len(staged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
