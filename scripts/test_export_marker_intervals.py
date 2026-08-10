#!/usr/bin/env python3
"""Parity test: join_markers windows + skip overlap (Export A3.2 contract mirror).

PowerShell-free unit of the interval rules Export-ShipCandidates now implements.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
JOIN = SCRIPTS / "join_markers.py"
FIXTURE = SCRIPTS.parent / "fixtures" / "markers" / "session_paired.jsonl"


def overlaps(a0: float, a1: float, b0: float, b1: float) -> bool:
    return not (a1 < b0 or a0 > b1)


def main() -> int:
    out = Path(tempfile.mkdtemp()) / "join.json"
    r = subprocess.run(
        [sys.executable, str(JOIN), "--markers", str(FIXTURE), "--out", str(out)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    rep = json.loads(out.read_text(encoding="utf-8"))
    wins = rep.get("windows") or []
    skips = rep.get("skip_zones") or []
    assert wins, rep
    assert skips, rep

    # Export rule: reject any window overlapping a skip zone
    accepted = []
    rejected = []
    for w in wins:
        st, en = float(w["start_sec"]), float(w["end_sec"])
        hit = any(
            overlaps(st, en, float(s["start_sec"]), float(s["end_sec"])) for s in skips
        )
        (rejected if hit else accepted).append(w)

    assert any(w.get("kind") == "broll" for w in accepted), accepted
    assert any(w.get("kind") == "rotate" for w in accepted), accepted
    assert any(w.get("kind") == "gather_broll" for w in accepted), accepted
    # talk_peak overlaps skip in fixture → must be rejected by Export rule
    talk_rej = [w for w in rejected if w.get("kind") == "talk_peak"]
    assert talk_rej, f"expected talk_peak rejected by skip overlap, rejected={rejected}"

    print(
        f"PASS export interval parity accepted={len(accepted)} rejected={len(rejected)} "
        f"(talk_skip_overlap ok)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
