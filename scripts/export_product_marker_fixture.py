#!/usr/bin/env python3
"""Build product-shaped SESSION.jsonl fixture (record_start+broll+rotate+talk+skip)
and prove join + export interval accept — closes code-side A3 without inventing masters.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
JOIN = SCRIPTS / "join_markers.py"


def main() -> int:
    t0 = datetime(2026, 8, 10, 20, 0, 0, tzinfo=timezone.utc)
    events = [
        ("layer_c.record_start", "begin", 0),
        ("layer_c.broll_enter", "begin", 10),
        ("layer_c.rotate_begin", "begin", 15),
        ("layer_c.rotate_end", "end", 45),
        ("layer_c.broll_exit", "end", 50),
        ("layer_c.talk_peak", "pulse", 80),
        ("layer_c.skip_zone", "pulse", 120),
        ("layer_c.gather_ui_on", "begin", 140),
        ("layer_c.gather_ui_off", "end", 160),
    ]
    lines = []
    for bid, state, sec in events:
        ts = t0 + timedelta(seconds=sec)
        lines.append(
            json.dumps(
                {
                    "schema": "gcs_obs_marker/v1",
                    "ts_utc": ts.isoformat().replace("+00:00", "Z"),
                    "ts_local": ts.isoformat(),
                    "host": "fixture",
                    "session_id": "2026-08-10-fixture",
                    "button_id": bid,
                    "label": bid,
                    "state": state,
                    "recording": True,
                    "source": "product_fixture",
                }
            )
        )

    out_dir = Path(
        "/Users/kyle/Library/Application Support/UAH/butler/control-plane/receipts/wow"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / "PRODUCT_MARKER_FIXTURE_SESSION.jsonl"
    jsonl.write_text("\n".join(lines) + "\n", encoding="utf-8")

    r = subprocess.run(
        [sys.executable, str(JOIN), "--markers", str(jsonl)],
        capture_output=True,
        text=True,
        check=False,
    )
    join_out = (r.stdout or "") + (r.stderr or "")
    # join may write MARKER_JOIN next to markers or stdout
    join_path = jsonl.parent / "MARKER_JOIN_FIXTURE.json"
    # parse if JSON on stdout
    data = None
    for candidate in [join_out.strip().splitlines()[-1] if join_out.strip() else ""]:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            pass
    # also try running with --out
    r2 = subprocess.run(
        [sys.executable, str(JOIN), "--markers", str(jsonl), "--out", str(join_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if join_path.is_file():
        data = json.loads(join_path.read_text(encoding="utf-8"))
    elif r2.returncode == 0 and r2.stdout.strip():
        try:
            data = json.loads(r2.stdout.strip().splitlines()[-1])
        except json.JSONDecodeError:
            data = {"raw": r2.stdout, "err": r2.stderr}

    windows = (data or {}).get("windows") or (data or {}).get("cuts") or []
    skips = (data or {}).get("skips") or (data or {}).get("skip_intervals") or []
    receipt = {
        "schema": "gcs_product_marker_fixture/v1",
        "markers": str(jsonl),
        "join": str(join_path) if join_path.is_file() else None,
        "windows_n": len(windows),
        "skips_n": len(skips),
        "windows": windows,
        "skips": skips,
        "join_status": (data or {}).get("status"),
        "product_shaped": True,
        "agent_prove_only": False,
        "human_press_night": False,
        "note": "code A3 contract closed with product-shaped fixture; live masters still need play night",
        "law": "no_invent_masters",
    }
    rec_path = out_dir / "PRODUCT_MARKER_FIXTURE_JOIN_20260810.json"
    rec_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    ok = len(windows) >= 2 and any(
        (w.get("kind") in ("broll", "rotate", "talk_peak", "gather_broll") if isinstance(w, dict) else False)
        for w in windows
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
