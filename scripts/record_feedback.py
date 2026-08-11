#!/usr/bin/env python3
"""Append plain-English candidate feedback. Human wins. No publish."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def clean_cell(value: str) -> str:
    return " ".join(value.replace("|", "/").split())


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def record(day_dir: Path, candidate_id: str, verdict: str, note: str) -> str:
    candidate_id = clean_cell(candidate_id)
    note = clean_cell(note)
    if not candidate_id:
        raise ValueError("candidate id is empty")

    lock_path = day_dir / ".feedback.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        fb = day_dir / "CANDIDATE_FEEDBACK.md"
        ts = datetime.now().strftime("%H:%M")
        line = f"| {ts} | `{candidate_id}` | **{verdict}** | {note} |"
        if fb.is_file():
            text = fb.read_text(encoding="utf-8")
        else:
            text = "# Candidate feedback\n\n| time | id | verdict | note |\n|------|----|---------|------|\n"
        if "## Live log" not in text:
            text = text.rstrip() + "\n\n## Live log\n\n| time | id | verdict | note |\n|------|----|---------|------|\n"
        atomic_write(fb, text.rstrip() + "\n" + line + "\n")

        hv = day_dir / "analysis" / "human_verdicts.json"
        data: dict = {}
        if hv.is_file():
            decoded = json.loads(hv.read_text(encoding="utf-8"))
            if isinstance(decoded, dict):
                data = decoded
        if data.get("schema") == "gcs_human_verdicts/v1" and isinstance(data.get("verdicts"), dict):
            verdicts = data["verdicts"]
        else:
            verdicts = {
                key: value
                for key, value in data.items()
                if key != "schema" and isinstance(value, dict)
            }
            data = {"schema": "gcs_human_verdicts/v1", "verdicts": verdicts}
        verdicts[candidate_id] = {
            "verdict": verdict if verdict != "PRIDE_PICK" else "KEEP",
            "reason": note or verdict,
            "source": "record_feedback",
        }
        data["updated_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        atomic_write(hv, json.dumps(data, indent=2) + "\n")
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    return line


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--verdict", required=True, choices=["KEEP", "REJECT", "REVIEW", "PRIDE_PICK"])
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    line = record(args.day_dir.resolve(), args.id, args.verdict, args.note)
    print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
