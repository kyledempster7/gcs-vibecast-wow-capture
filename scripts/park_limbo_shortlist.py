#!/usr/bin/env python3
"""Park second-play / limbo SHORTLIST items older than N days into LIMBO_PARK.md.

Does not invent KEEP/REJECT. No publish. Human can still unpark later.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--returns", type=Path, default=Path.home() / "Movies/WoW-Broll-Workflow/Returns")
    ap.add_argument("--older-than-days", type=int, default=2)
    ap.add_argument("--apply", action="store_true", help="Write LIMBO_PARK.md (default dry-run)")
    args = ap.parse_args()
    cutoff = datetime.now() - timedelta(days=args.older_than_days)
    parks: list[str] = []
    for day in sorted(args.returns.glob("returner-daily-*")):
        day_id = day.name.replace("returner-daily-", "")
        try:
            d0 = datetime.strptime(day_id, "%Y-%m-%d")
        except ValueError:
            continue
        if d0 > cutoff:
            continue
        short = day / "review-pack" / "SHORTLIST.md"
        hv = day / "analysis" / "human_verdicts.json"
        verdicts = {}
        if hv.is_file():
            try:
                verdicts = json.loads(hv.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                verdicts = {}
        if not short.is_file():
            continue
        text = short.read_text(encoding="utf-8")
        limbo_lines = []
        for line in text.splitlines():
            if "second-play" in line.lower() or "AUTO_REVIEW" in line or "_(secondary)_" in line:
                # extract **id**
                if "**" in line:
                    parts = line.split("**")
                    if len(parts) >= 2:
                        cid = parts[1].split()[0]
                        v = (verdicts.get(cid) or {}).get("verdict", "")
                        if str(v).upper() in ("KEEP", "REJECT"):
                            continue
                        limbo_lines.append(f"- `{cid}` · day={day_id} · was: {line.strip()[:120]}")
        if limbo_lines:
            parks.append(f"## {day_id}\n\n" + "\n".join(limbo_lines) + "\n")
            if args.apply:
                park_path = day / "review-pack" / "LIMBO_PARK.md"
                park_path.write_text(
                    f"# Limbo park — {day_id}\n\n"
                    f"_Auto-parked {datetime.now().isoformat()} · older than {args.older_than_days}d · no force KEEP/REJECT_\n\n"
                    + "\n".join(limbo_lines)
                    + "\n",
                    encoding="utf-8",
                )
                # annotate SHORTLIST once
                if "LIMBO_PARK" not in text:
                    short.write_text(
                        text.rstrip()
                        + f"\n\n## Limbo parked\n\nSee `LIMBO_PARK.md` (auto · {args.older_than_days}d+ · no force verdict).\n",
                        encoding="utf-8",
                    )

    print(f"limbo_days={len(parks)} apply={args.apply}")
    for p in parks[:5]:
        print(p[:200].replace("\n", " | "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
