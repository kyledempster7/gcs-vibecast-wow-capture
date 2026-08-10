#!/usr/bin/env python3
"""Append analysis/WEIGHT.json from human_verdicts (KEEP vs REJECT tags).

Fail-closed: no verdicts → SKIP. No invent. No publish.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_verdicts(day_dir: Path) -> dict:
    hv = day_dir / "analysis" / "human_verdicts.json"
    if not hv.is_file():
        return {}
    raw = json.loads(hv.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("verdicts"), dict):
        raw = raw["verdicts"]
    if not isinstance(raw, dict):
        return {}
    out: dict = {}
    for k, v in raw.items():
        if isinstance(v, dict) and "verdict" in v:
            out[str(k)] = v
        elif isinstance(v, str) and v.strip():
            out[str(k)] = {"verdict": v.strip(), "reason": "", "source": "legacy_string"}
    return out


def bucket(verdicts: dict) -> tuple[list[str], list[str], list[str]]:
    keep, reject, other = [], [], []
    for cid, v in verdicts.items():
        ver = str(v.get("verdict", "")).upper()
        reason = (v.get("reason") or "").strip()
        tag = f"{cid}:{reason}" if reason else cid
        if ver in ("KEEP", "PRIDE_PICK"):
            keep.append(tag)
        elif ver == "REJECT":
            reject.append(tag)
        else:
            other.append(f"{cid}:{ver}:{reason}" if reason else f"{cid}:{ver}")
    return keep, reject, other


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    ap.add_argument("--note", default="", help="Optional one-line agent/human note")
    args = ap.parse_args()
    day_dir = args.day_dir.resolve()
    day = day_dir.name.replace("returner-daily-", "") if "returner-daily-" in day_dir.name else day_dir.name
    analysis = day_dir / "analysis"
    analysis.mkdir(parents=True, exist_ok=True)

    verdicts = load_verdicts(day_dir)
    if not verdicts:
        print(f"write_weight SKIP no_verdicts day={day}")
        return 0

    keep, reject, other = bucket(verdicts)
    if not keep and not reject:
        print(f"write_weight SKIP no_KEEP_or_REJECT day={day}")
        return 0

    weight_path = analysis / "WEIGHT.json"
    if weight_path.is_file():
        try:
            doc = json.loads(weight_path.read_text(encoding="utf-8"))
        except Exception:
            doc = {"schema": "gcs_weight_ledger/v1", "rows": []}
    else:
        doc = {"schema": "gcs_weight_ledger/v1", "rows": []}
    if not isinstance(doc.get("rows"), list):
        doc["rows"] = []

    row = {
        "day": day,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "keep_n": len(keep),
        "reject_n": len(reject),
        "other_n": len(other),
        "KEEP_tags": keep,
        "REJECT_tags": reject,
        "other": other,
        "note": (args.note or "").strip(),
        "law": "from human_verdicts only · no invent · no virality score",
    }
    # replace same-day row if re-run
    doc["rows"] = [r for r in doc["rows"] if r.get("day") != day]
    doc["rows"].append(row)
    doc["updated_at_utc"] = row["generated_at_utc"]
    weight_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"write_weight OK day={day} keep={len(keep)} reject={len(reject)} -> {weight_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
