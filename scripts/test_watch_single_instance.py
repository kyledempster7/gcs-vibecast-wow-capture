#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory


WATCH = Path(__file__).resolve().parent / "watch_ready_harvest_once.sh"


def main() -> int:
    with TemporaryDirectory(prefix="gcs-watch-lock-") as td:
        env = os.environ.copy()
        env.update({"HOME": td, "MAX_MIN": "0", "WATCH_TEST_HOLD_SEC": "3"})
        first = subprocess.Popen(
            ["bash", str(WATCH), "2099-01-01"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        lock = Path(td) / "Library/Logs/gcs-vibecast-wow/watch_ready_harvest.lockdir/pid"
        for _ in range(30):
            if lock.is_file():
                break
            time.sleep(0.1)
        assert lock.is_file(), "first watcher did not acquire lock"
        second = subprocess.run(
            ["bash", str(WATCH), "2099-01-01"],
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        assert second.returncode == 1, (second.returncode, second.stdout, second.stderr)
        assert "FAILED" in second.stdout
        first_stdout, first_stderr = first.communicate(timeout=8)
        assert first.returncode == 2, (first.returncode, first_stdout, first_stderr)
        assert not lock.parent.exists(), "lockdir was not released"
    print("ALL_PASS SECOND_WATCH_REFUSED LOCK_RELEASED UNKNOWN_FILES_PRESERVED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
