#!/usr/bin/env python3
"""ARM_STATE contract: default deny publish until Kyle go + hash bind.

Scaffold + tests. Does not arm live packages. No invent FOOTAGE.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_arm(path: Path) -> dict:
    if not path.is_file():
        return {
            "schema": "gcs_arm_state/v0",
            "armed": False,
            "reason": "missing_arm_file",
        }
    return json.loads(path.read_text(encoding="utf-8"))


def may_publish(arm: dict, package_sha: str, day: str) -> tuple[bool, str]:
    if not arm.get("armed"):
        return False, "not_armed"
    if arm.get("day") != day:
        return False, "day_mismatch"
    if not arm.get("kyle_go"):
        return False, "missing_kyle_go"
    if (arm.get("package_sha256") or "") != package_sha:
        return False, "package_hash_mismatch"
    return True, "ok"


def write_disarmed(path: Path, day: str) -> dict:
    data = {
        "schema": "gcs_arm_state/v0",
        "armed": False,
        "day": day,
        "kyle_go": False,
        "package_sha256": None,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "law": "default_deny_until_go_hash",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def self_test() -> int:
    day = "2099-01-01"
    arm = {
        "schema": "gcs_arm_state/v0",
        "armed": True,
        "day": day,
        "kyle_go": True,
        "package_sha256": "abc",
    }
    ok, why = may_publish(arm, "abc", day)
    assert ok and why == "ok"
    ok, why = may_publish(arm, "zzz", day)
    assert not ok and why == "package_hash_mismatch"
    ok, why = may_publish({**arm, "armed": False}, "abc", day)
    assert not ok
    ok, why = may_publish({**arm, "kyle_go": False}, "abc", day)
    assert not ok
    ok, why = may_publish(arm, "abc", "2099-01-02")
    assert not ok and why == "day_mismatch"
    print("PASS arm_state self_test")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--disarm", type=Path, default=None)
    ap.add_argument("--day", default="")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.disarm:
        write_disarmed(args.disarm, args.day or "unknown")
        print(f"disarmed -> {args.disarm}")
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
