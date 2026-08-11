#!/usr/bin/env python3
"""Synchronize the tracked 100-gap ledger from the canonical Codex crosswalk."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


CROSSWALK = Path(
    "/Users/kyle/Library/Application Support/UAH/butler/control-plane/"
    "receipts/gcs-vibecast/GAP_100_CROSSWALK_LATEST.json"
)
LEDGER = Path(__file__).resolve().parents[2] / "04-Story-and-Capture/GAUNTLET_100_BUGS_VIBECAST.md"
ROW = re.compile(r"^\|\s*(\d{1,3})\s*\|.*\|$")


def escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def render(source: str, doc: dict) -> str:
    rows = doc.get("rows")
    if not isinstance(rows, list) or len(rows) != 100:
        raise ValueError("canonical crosswalk must contain exactly 100 rows")
    if [row.get("gap") for row in rows] != list(range(1, 101)):
        raise ValueError("canonical crosswalk gaps must be ordered 1..100")
    by_gap = {row["gap"]: row for row in rows}

    output: list[str] = []
    seen: set[int] = set()
    for line in source.splitlines():
        match = ROW.match(line)
        if match and int(match.group(1)) in by_gap:
            gap = int(match.group(1))
            row = by_gap[gap]
            output.append(
                f"| {gap} | {escape_cell(row['title'])} | **{row['status']}** | "
                f"{escape_cell(row['bans_notes'])} |"
            )
            seen.add(gap)
        elif line.startswith("**Live scored:**"):
            output.append("**Canonical source:** Codex 100-row owner crosswalk; run `sync_gap_100_ledger.py` after a refresh.  ")
        elif line.startswith("**Canonical synchronized:**"):
            output.append("**Canonical source:** Codex 100-row owner crosswalk; run `sync_gap_100_ledger.py` after a refresh.  ")
        elif line.startswith("**Legend:**"):
            output.append("**Legend:** **CLOSED** current proof closes the named bug · **PARTIAL** safe work complete but real/human proof remains · **OPEN** real capture/audio/human action required  ")
        else:
            output.append(line)
    if seen != set(range(1, 101)):
        missing = sorted(set(range(1, 101)) - seen)
        raise ValueError(f"tracked ledger row set drifted; missing {missing}")

    text = "\n".join(output) + "\n"
    counts = doc.get("counts") or {}
    remaining = [row for row in rows if row["status"] != "CLOSED"]
    score = "\n".join(
        [
            "## Score snapshot (canonical)",
            "",
            f"- **CLOSED:** {counts.get('CLOSED', 0)}",
            f"- **PARTIAL:** {counts.get('PARTIAL', 0)}",
            f"- **OPEN:** {counts.get('OPEN', 0)}",
            f"- **Verdict:** `{doc.get('verdict')}`",
            f"- **First boundary:** `{doc.get('remaining_first_bad_boundary')}`",
            "",
            "The executable gauntlet is supporting evidence; this 100-row ledger is the complete risk crosswalk.",
            "",
            "## Patches shipped with this gauntlet wave",
        ]
    )
    text, n = re.subn(
        r"## Score snapshot \((?:live|canonical)\).*?## Patches shipped with this gauntlet wave",
        score,
        text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise ValueError("score snapshot block not found")

    actions = list(dict.fromkeys(doc.get("closure_actions") or []))
    shipped = ["## Patches shipped with this gauntlet wave", ""]
    shipped.extend(f"{index}. {action}" for index, action in enumerate(actions, start=1))
    shipped.append("")
    text, n = re.subn(
        r"## Patches shipped with this gauntlet wave.*?(?=## (?:Top 10 to tackle next|Remaining product/human boundaries))",
        "\n".join(shipped),
        text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise ValueError("patches-shipped block not found")

    boundary_lines = [
        f"## Remaining product/human boundaries ({len(remaining)})",
        "",
    ]
    for row in remaining:
        boundary_lines.append(
            f"{row['gap']}. **{row['status']} — {row['title']}:** {row['bans_notes']}"
        )
    boundary_lines += [
        "",
        f"Canonical receipt: `{CROSSWALK}`",
        "",
        "## Related",
    ]
    text, n = re.subn(
        r"## (?:Top 10 to tackle next \(priority\)|Remaining product/human boundaries \(\d+\)).*?## Related",
        "\n".join(boundary_lines),
        text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise ValueError("stale Top 10 block not found")
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    doc = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    current = LEDGER.read_text(encoding="utf-8")
    expected = render(current, doc)
    if args.check:
        if current != expected:
            print("DRIFT tracked 100-gap ledger is not synchronized")
            return 2
        print("PASS tracked 100-gap ledger synchronized")
        return 0
    tmp = LEDGER.with_name(f".{LEDGER.name}.{os.getpid()}.tmp")
    tmp.write_text(expected, encoding="utf-8")
    os.replace(tmp, LEDGER)
    print(f"PASS synchronized 100 rows -> {LEDGER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
