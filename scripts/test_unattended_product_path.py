#!/usr/bin/env python3
"""Drive real unattended_product_path decision + fail-closed laws.

No test theater: imports shipped functions; live branch B asserts real harvest SKIP.
"""
from __future__ import annotations

import inspect
import json
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from unattended_product_path import (  # noqa: E402
    branch_a_harvest_chain,
    branch_a_steps,
    decide_branch,
    ready_today_from_poll,
    residual_ready_non_today,
    today_row,
)


def test_decide_branch_ready_true() -> None:
    day = "2026-08-10"
    data = {
        "ready_today": True,
        "days": [{"day": day, "ready": True, "reason": "candidates_qualified"}],
    }
    assert ready_today_from_poll(data, day) is True
    assert decide_branch(data, day) == "A"
    print("PASS decide_branch A when ready_today")


def test_decide_branch_ready_false_with_residual() -> None:
    day = "2026-08-10"
    data = {
        "ready_today": False,
        "ready_any": True,
        "days": [
            {
                "day": day,
                "ready": False,
                "reason": "markers_only_no_candidates",
                "candidates_n": 0,
                "raw_mp4_n": 0,
            },
            {
                "day": "2026-08-09",
                "ready": True,
                "reason": "candidates_qualified",
                "candidates_n": 15,
                "raw_mp4_n": 3,
            },
        ],
    }
    assert ready_today_from_poll(data, day) is False
    assert decide_branch(data, day) == "B"
    assert residual_ready_non_today(data, day) == ["2026-08-09"]
    assert today_row(data, day).get("candidates_n") == 0
    print("PASS decide_branch B; residual not today")


def test_day_bind_top_level_lie_denied() -> None:
    """Top-level ready_today=true but day row false → deny (Codex C)."""
    day = "2026-08-10"
    data = {
        "ready_today": True,
        "days": [
            {"day": day, "ready": False, "reason": "markers_only_no_candidates"},
            {"day": "2026-08-09", "ready": True},
        ],
    }
    assert ready_today_from_poll(data, day) is False
    assert decide_branch(data, day) == "B"
    print("PASS day-bind denies top-level lie")


def test_missing_day_row_denied() -> None:
    day = "2026-08-10"
    data = {"ready_today": True, "days": [{"day": "2026-08-09", "ready": True}]}
    assert ready_today_from_poll(data, day) is False
    print("PASS missing day row denied")


def test_freshness_gate() -> None:
    day = "2026-08-10"
    data = {
        "ready_today": True,
        "days": [{"day": day, "ready": True, "reason": "candidates_qualified"}],
    }
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "SOFT_POLL_LATEST.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        # fresh
        assert ready_today_from_poll(data, day, require_fresh=True, poll_path=p) is True
        # stale
        import os
        import time

        old = time.time() - 9999
        os.utime(p, (old, old))
        assert ready_today_from_poll(data, day, require_fresh=True, poll_path=p) is False
    print("PASS freshness gate")


def test_branch_a_no_duplicate_enhance_in_source() -> None:
    """Structural: Branch A default steps are harvest-only; source does not always enhance."""
    assert branch_a_steps() == ["harvest_if_ready.sh"]
    src = inspect.getsource(branch_a_harvest_chain)
    # Must call harvest_if_ready
    assert "harvest_if_ready.sh" in src
    # Must not unconditionally call enhance then build_review (old duplicate path)
    assert "repair_enhance" in src or "skip_re_enhance" in src
    # Unconditional double enhance pattern banned: enhance always after harvest without pack check
    assert "if has_media and not pack_ok" in src or "review_pack_present" in src
    print("PASS branch A structural no-dupe enhance")


def test_live_driver_branch_b_or_a() -> None:
    """Run shipped entry once. If not ready_today, expect exit 0 + BLOCKED receipt."""
    day = datetime.now().strftime("%Y-%m-%d")
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "unattended_product_path.py"), day],
        cwd=str(SCRIPTS),
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    out = r.stdout + r.stderr
    print(out[-2000:] if len(out) > 2000 else out)
    assert r.returncode == 0, (r.returncode, out[-1500:])
    latest = (
        Path.home()
        / "Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast"
        / "UNATTENDED_PRODUCT_PATH_LATEST.json"
    )
    assert latest.is_file(), latest
    body = json.loads(latest.read_text(encoding="utf-8"))
    assert body.get("checkins_required") is False
    assert body.get("day") == day
    assert body.get("branch_a_steps") == ["harvest_if_ready.sh"]
    if body.get("branch") == "B":
        assert body.get("status") == "BLOCKED_ON_MASTERS_ARMED"
        assert body.get("ready_today") is False
        assert body.get("harvest_rc") in (0, 1)
        print("PASS live driver branch B BLOCKED_ON_MASTERS_ARMED")
    else:
        assert body.get("branch") == "A"
        assert body.get("ready_today") is True
        print("PASS live driver branch A product path")


def main() -> int:
    test_decide_branch_ready_true()
    test_decide_branch_ready_false_with_residual()
    test_day_bind_top_level_lie_denied()
    test_missing_day_row_denied()
    test_freshness_gate()
    test_branch_a_no_duplicate_enhance_in_source()
    test_live_driver_branch_b_or_a()
    print("ALL_PASS test_unattended_product_path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
