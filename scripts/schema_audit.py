#!/usr/bin/env python3
"""Audit versioned schema strings across VibeCast JSON (decades #96).

No invent. No publish. Writes receipts/wow/SCHEMA_AUDIT_LATEST.json
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOTS = [
    Path.home() / "Movies/WoW-Broll-Workflow",
    Path(__file__).resolve().parents[2] / "04-Story-and-Capture",
]
RECEIPTS = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/wow"
)
SCHEMA_RE = re.compile(r'"schema"\s*:\s*"([^"]+)"')


def main() -> int:
    found: Counter[str] = Counter()
    missing_schema: list[str] = []
    files_scanned = 0
    for root in ROOTS:
        if not root.is_dir():
            continue
        for p in root.rglob("*.json"):
            if any(x in p.parts for x in ("node_modules", ".git", "__pycache__")):
                continue
            if p.stat().st_size > 5_000_000:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            files_scanned += 1
            matches = SCHEMA_RE.findall(text)
            if matches:
                for m in matches:
                    found[m] += 1
            else:
                # only flag small product-ish json
                if p.name in (
                    "MANIFEST.json",
                    "ARM_STATE.json",
                    "human_verdicts.json",
                    "CATALOG.json",
                    "SOFT_POLL_LATEST.json",
                ) or p.name.startswith("chat_detect"):
                    missing_schema.append(str(p))

    out = {
        "schema": "gcs_schema_audit/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "files_scanned": files_scanned,
        "schema_counts": dict(found.most_common()),
        "missing_schema_sample": missing_schema[:40],
        "missing_n": len(missing_schema),
        "law": "version_strings_for_decades",
    }
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    path = RECEIPTS / "SCHEMA_AUDIT_LATEST.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"files": files_scanned, "schemas": len(found), "missing_n": len(missing_schema)}, indent=2))
    for k, v in found.most_common(20):
        print(f"  {v:4d}  {k}")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
