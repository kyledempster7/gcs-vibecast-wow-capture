#!/usr/bin/env python3
"""Append plain-English candidate feedback. Human wins. No publish."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--verdict", required=True, choices=["KEEP", "REJECT", "REVIEW", "PRIDE_PICK"])
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    fb = args.day_dir / "CANDIDATE_FEEDBACK.md"
    ts = datetime.now().strftime("%H:%M")
    line = f"| {ts} | `{args.id}` | **{args.verdict}** | {args.note} |"
    if not fb.is_file():
        fb.write_text(
            "# Candidate feedback\n\n| time | id | verdict | note |\n|------|----|---------|------|\n",
            encoding="utf-8",
        )
    text = fb.read_text(encoding="utf-8")
    if "## Live log" not in text:
        text = text.rstrip() + "\n\n## Live log\n\n| time | id | verdict | note |\n|------|----|---------|------|\n"
    text = text.rstrip() + "\n" + line + "\n"
    fb.write_text(text, encoding="utf-8")
    # also human_verdicts for score
    hv = args.day_dir / "analysis" / "human_verdicts.json"
    import json
    data = {}
    if hv.is_file():
        data = json.loads(hv.read_text(encoding="utf-8"))
    if "schema" not in data:
        data = {"schema": "gcs_human_verdicts/v1", "verdicts": data if all(isinstance(v, dict) for v in data.values()) else {}}
    if "verdicts" not in data:
        data = {"schema": "gcs_human_verdicts/v1", "verdicts": data}
    data["verdicts"][args.id] = {"verdict": args.verdict if args.verdict != "PRIDE_PICK" else "KEEP",
                     "reason": args.note or args.verdict, "source": "record_feedback"}
    hv.parent.mkdir(parents=True, exist_ok=True)
    hv.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
