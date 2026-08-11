#!/usr/bin/env python3
"""Prove harvest claim-before-work and watch soft_poll defer source markers.

No invent. No network. No kill of live processes.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
HARVEST = SCRIPTS / "harvest_if_ready.sh"
WATCH = SCRIPTS / "watch_ready_harvest_once.sh"
RETURNS = Path.home() / "Movies/WoW-Broll-Workflow/Returns"


def test_watch_source_defers_when_golden_pattern() -> None:
    text = WATCH.read_text(encoding="utf-8")
    assert "defer_to_golden" in text or "golden_alive" in text
    assert "soft_poll_windows.sh" in text
    # only one soft_poll invocation path when not golden (not dual thrash)
    # count soft_poll calls outside comments
    lines = [ln for ln in text.splitlines() if "soft_poll_windows.sh" in ln and not ln.strip().startswith("#")]
    assert len(lines) <= 2, lines  # one in else branch + maybe docs
    print("PASS watch source has golden defer + non-dual soft_poll")


def test_harvest_claim_string() -> None:
    text = HARVEST.read_text(encoding="utf-8")
    assert ".harvest_claim.lockdir" in text
    assert "exit 3" in text or "exit=3" in text
    print("PASS harvest claimdir in source")


def test_claim_held_exit_3() -> None:
    day = time.strftime("%Y-%m-%d")
    day_dir = RETURNS / f"returner-daily-{day}"
    claim = day_dir / ".harvest_claim.lockdir"
    claim.mkdir(parents=True, exist_ok=True)
    holder = subprocess.Popen(["sleep", "30"])
    try:
        (claim / "pid").write_text(str(holder.pid) + "\n", encoding="utf-8")
        env = os.environ.copy()
        env["HARVEST_FORCE_POLL"] = "0"
        r = subprocess.run(
            ["bash", str(HARVEST), day],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(SCRIPTS),
            check=False,
        )
        assert r.returncode == 3, (r.returncode, r.stdout, r.stderr)
        assert "claim held" in r.stdout.lower() or "claim held" in r.stderr.lower()
        print("PASS harvest claim held exit 3")
    finally:
        holder.kill()
        holder.wait(timeout=5)
        shutil.rmtree(claim, ignore_errors=True)


def main() -> int:
    test_watch_source_defers_when_golden_pattern()
    test_harvest_claim_string()
    test_claim_held_exit_3()
    print("ALL_PASS test_harvest_claim_and_watch_defer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
