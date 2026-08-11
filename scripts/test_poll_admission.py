#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from poll_admission import decide


def main() -> int:
    with TemporaryDirectory(prefix="gcs-poll-admission-") as td:
        latest = Path(td) / "SOFT_POLL_LATEST.json"
        day = "2026-08-11"
        base = {"schema": "gcs_soft_poll_ready/v2", "ready_today": False, "days": []}
        assert decide(latest, day) == "POLL"
        base["days"] = [{"day": day, "ready": False}]
        latest.write_text(json.dumps(base), encoding="utf-8")
        assert decide(latest, day, now=latest.stat().st_mtime + 10) == "SKIP"
        base["days"][0]["ready"] = True
        latest.write_text(json.dumps(base), encoding="utf-8")
        assert decide(latest, day, now=latest.stat().st_mtime + 10) == "POLL"
        base["days"] = [{"day": "2026-08-10", "ready": False}]
        latest.write_text(json.dumps(base), encoding="utf-8")
        assert decide(latest, day, now=latest.stat().st_mtime + 10) == "POLL"
        base["days"] = [{"day": day, "ready": False}]
        latest.write_text(json.dumps(base), encoding="utf-8")
        os.utime(latest, (latest.stat().st_atime, latest.stat().st_mtime - 120))
        assert decide(latest, day) == "POLL"
    print("ALL_PASS READY_NEVER_HIDDEN FRESH_NOT_READY_REUSED MISSING_OR_STALE_POLLED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
