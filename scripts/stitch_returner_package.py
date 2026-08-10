#!/usr/bin/env python3
"""
Stitch: Returner Daily day folder → local delivery package + outbox enqueue (NOT_ARMED).
No Zernio network. Fail-closed arm left for human go.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).resolve().parent
DI = (
    Path.home()
    / "Library"
    / "Application Support"
    / "UAH"
    / "butler"
    / "control-plane"
    / "delivery-independence"
)
BUILD = DI / "build_package.py"
OUTBOX = DI / "outbox.py"
PKG_DIR = DI / "packages"
DAILY = WOW / "04-Story-and-Capture" / "returner-daily"
sys.path.insert(0, str(SCRIPTS))
from arm_state import may_publish, write_disarmed  # noqa: E402


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    ap.add_argument(
        "--allow-outbox",
        action="store_true",
        help="Only enqueue outbox if ARM_STATE may_publish (default: never auto-arm)",
    )
    args = ap.parse_args()
    day = args.day or datetime.now().strftime("%Y-%m-%d")
    day_dir = DAILY / day
    if not day_dir.is_dir():
        # scaffold first
        sub = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).parent / "draft_returner_daily.py"),
                "--day",
                day,
                "--note",
                "stitch auto-scaffold",
            ],
            check=False,
        )
        if sub.returncode != 0 or not day_dir.is_dir():
            print(f"ERROR: no day dir {day_dir}", file=sys.stderr)
            return 1

    if not BUILD.is_file():
        print(f"ERROR: missing {BUILD}", file=sys.stderr)
        return 1

    out = PKG_DIR / f"returner_daily_{day}.NOT_ARMED.json"
    PKG_DIR.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [
            sys.executable,
            str(BUILD),
            "--brand",
            "twe",  # GCS brand: The WoW Explorer (not orphan "wow")
            "--returner-dir",
            str(day_dir),
            "--out",
            str(out),
        ],
        check=False,
    )
    if r.returncode != 0:
        return r.returncode

    # copy package pointer into day folder; stamp citadel ownership
    dest = day_dir / "zernio_package.json"
    text = out.read_text(encoding="utf-8")
    dest.write_text(text, encoding="utf-8")
    arm_path = day_dir / "ARM_STATE.json"
    try:
        pkg = json.loads(text)
        pkg["gcs"] = {
            "citadel": "GCS",
            "wing": "VibeCast",
            "brand": "twe",
            "product": "returner_daily",
        }
        # product_ready may already be set by build_package; reaffirm media truth
        media = pkg.get("media") or []
        if "product_ready" not in pkg:
            pkg["product_ready"] = len(media) > 0 and any(m.get("exists") for m in media if isinstance(m, dict))
        if not pkg.get("product_ready"):
            pkg.setdefault("hold_reason", "media_empty_or_missing_on_disk")
        # ARM_STATE: default deny — write disarmed binder for this day
        if not arm_path.is_file():
            write_disarmed(arm_path, day)
        pkg_sha = file_sha(out)
        arm = json.loads(arm_path.read_text(encoding="utf-8"))
        allowed, why = may_publish(arm, pkg_sha, day)
        pkg["arm"] = "ARMED" if allowed else "NOT_ARMED"
        pkg["may_publish"] = False  # hard: stitch never flips publish on
        pkg["arm_check"] = {
            "allowed": allowed,
            "why": why,
            "package_sha256": pkg_sha,
            "arm_path": str(arm_path),
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "law": "default_deny_stitch_cannot_arm",
        }
        if not allowed:
            pkg.setdefault("hold_reason", f"arm_deny:{why}")
        out.write_text(json.dumps(pkg, indent=2), encoding="utf-8")
        dest.write_text(json.dumps(pkg, indent=2), encoding="utf-8")
        print(
            f"stitch product_ready={pkg.get('product_ready')} media={len(media)} "
            f"hold={pkg.get('hold_reason')} may_publish={pkg.get('may_publish')} arm_why={why}"
        )
    except Exception as e:
        print(f"stitch arm stamp soft-fail: {e}", file=sys.stderr)

    # Outbox only if explicitly allowed AND arm would permit (still never silent publish network)
    if args.allow_outbox and OUTBOX.is_file():
        arm = json.loads(arm_path.read_text(encoding="utf-8")) if arm_path.is_file() else {}
        ok, why = may_publish(arm, file_sha(out), day)
        if not ok:
            print(f"outbox SKIP arm_deny:{why}")
        else:
            subprocess.run(
                [
                    sys.executable,
                    str(OUTBOX),
                    "--db",
                    str(DI / "data" / "outbox.sqlite"),
                    "enqueue",
                    "--brand",
                    "twe",
                    "--platform",
                    "instagram",
                    "--package",
                    str(out),
                    "--group",
                    "gcs-twe-returner",
                ],
                check=False,
            )
    elif OUTBOX.is_file():
        print("outbox SKIP default (pass --allow-outbox only with arm proof)")

    # QA
    subprocess.run(
        [sys.executable, str(Path(__file__).parent / "qa_returner_daily.py"), "--day", day],
        check=False,
    )
    print(f"stitch ok package={out} day={day_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
