#!/usr/bin/env python3
"""
Merge caption-seeds into Returner Daily caption.md only if still scaffold.
Never overwrites a filled human/agent caption.
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
DAILY = WOW / "04-Story-and-Capture" / "returner-daily"
SEEDS = DAILY / "caption-seeds"


def is_scaffold(caption: str) -> bool:
    return "[one line what happened]" in caption or "**Status:** scaffold" in caption


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    ap.add_argument("--force", action="store_true", help="Overwrite even if not scaffold")
    args = ap.parse_args()
    day = args.day or datetime.now().strftime("%Y-%m-%d")
    cap_path = DAILY / day / "caption.md"
    seed_path = SEEDS / f"{day}.md"
    if not seed_path.is_file():
        seed_path = SEEDS / "latest.md"
    if not cap_path.is_file():
        print(f"ERROR: no caption {cap_path}")
        return 1
    if not seed_path.is_file():
        print(f"ERROR: no seed {seed_path}")
        return 1

    caption = cap_path.read_text(encoding="utf-8")
    if not args.force and not is_scaffold(caption):
        print("skip: caption already filled (use --force to overwrite)")
        return 0

    seed = seed_path.read_text(encoding="utf-8").strip()
    # pull first non-empty useful line from seed
    lines = [ln.strip() for ln in seed.splitlines() if ln.strip() and not ln.startswith("#")]
    one = lines[0] if lines else "Returner night"
    footer = (
        "\n\n---\n"
        "**Soft promo (optional):** Explorer’s League someday · Thrall · "
        "returner energy — never invent members or force CTA.\n"
    )
    body = f"""# Caption draft — {day}

**Status:** seeded from caption-seeds · edit before go

## Feed

```
{one}

Returner energy · Thrall · Horde
```

## Seed source

`{seed_path.name}`

## Optional positive friction

```
Friction tonight: …
Working around it by: …
Got a workaround?
```
{footer}
"""
    cap_path.write_text(body, encoding="utf-8")
    print(f"merged caption -> {cap_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
