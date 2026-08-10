#!/usr/bin/env python3
"""Export dry on a real SESSION.jsonl — join + skip-overlap accept/reject counts.

Does NOT invent masters or cut video. Proves Export A3.2 interval contract against
live marker files. Product A3 e2e still needs human multi-act + new masters.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
JOIN = SCRIPTS / "join_markers.py"


def overlaps(a0: float, a1: float, b0: float, b1: float) -> bool:
    return not (a1 < b0 or a0 > b1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--markers",
        type=Path,
        default=Path.home()
        / "Movies/WoW-Broll-Workflow/Returns/returner-daily-2026-08-09/markers/SESSION.jsonl",
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    if not args.markers.is_file():
        print(f"FAIL missing markers {args.markers}", file=sys.stderr)
        return 2

    tmp = Path(tempfile.mkdtemp()) / "join.json"
    r = subprocess.run(
        [sys.executable, str(JOIN), "--markers", str(args.markers), "--out", str(tmp)],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        return 2
    rep = json.loads(tmp.read_text(encoding="utf-8"))
    wins = rep.get("windows") or []
    skips = rep.get("skip_zones") or []
    accepted, rejected = [], []
    for w in wins:
        st, en = float(w["start_sec"]), float(w["end_sec"])
        hit = any(
            overlaps(st, en, float(s["start_sec"]), float(s["end_sec"])) for s in skips
        )
        (rejected if hit else accepted).append(w)

    deck_n = int(rep.get("deck_event_count") or 0)
    humanish = deck_n > 0 and not all(
        "agent_prove" in str(w) for w in wins  # windows lack labels; use status honesty
    )
    # Honest product gate: agent_prove-only nights are not A3 e2e
    labels = []
    for line in args.markers.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        lab = str(row.get("label") or "")
        if lab:
            labels.append(lab)
    agent_only = bool(labels) and all("agent_prove" in lab or lab.startswith("Gather") for lab in labels)
    # Gather UI on/off can be real; agent_prove* is not human multi-act product
    agent_prove_only = bool(labels) and all(
        "agent_prove" in lab or lab in ("Gather UI ON", "Gather UI OFF") for lab in labels
    )

    out = {
        "schema": "gcs_export_dry_real_session/v1",
        "markers_path": str(args.markers),
        "join_status": rep.get("status"),
        "windows_n": len(wins),
        "skips_n": len(skips),
        "accepted_n": len(accepted),
        "rejected_n": len(rejected),
        "deck_event_count": deck_n,
        "labels": labels,
        "agent_prove_only": agent_prove_only,
        "product_a3_e2e": False if agent_prove_only else bool(accepted),
        "note": (
            "code interval contract OK; product A3 e2e blocked until human multi-act "
            "+ new masters (not agent_prove labels only)"
            if agent_prove_only
            else "code OK; product A3 still needs masters export e2e if not yet run"
        ),
        "windows": wins,
        "accepted_kinds": [w.get("kind") for w in accepted],
        "law": "no_invent_masters; no_publish",
    }
    text = json.dumps(out, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(
        f"export_dry windows={len(wins)} accepted={len(accepted)} "
        f"agent_prove_only={agent_prove_only} product_a3_e2e={out['product_a3_e2e']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
