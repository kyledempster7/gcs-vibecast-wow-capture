#!/usr/bin/env python3
"""
SCH-7 scaffold: create Returner Daily draft folder for a day.

Does NOT invent clips or claim publish. Writes:
  04-Story-and-Capture/returner-daily/YYYY-MM-DD/
    README.md
    caption.md
    SOURCES.md  (optional paths if provided)

Exit: 0 ok | 2 write error
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT.parent / "04-Story-and-Capture" / "returner-daily"


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold Returner Daily draft day")
    ap.add_argument("--day", default=None)
    ap.add_argument("--out-root", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--video", default="", help="Optional video path (not validated as content)")
    ap.add_argument("--still", default="", help="Optional still path")
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    day = args.day or datetime.now().strftime("%Y-%m-%d")
    day_dir = args.out_root / day
    try:
        day_dir.mkdir(parents=True, exist_ok=True)
        root_readme = args.out_root / "README.md"
        if not root_readme.is_file():
            root_readme.write_text(
                """# Returner Daily drafts

**Product:** carousel + B-roll + personality — **not** Class-P.  
**Kyle:** play/talk only. **Agents:** fill day folders after media exists.  
**Publish:** human go only.

```bash
python scripts/draft_returner_daily.py --day YYYY-MM-DD
# optional:
python scripts/draft_returner_daily.py --video "D:\\path\\clip.mp4" --still "C:\\...\\WoWScrnShot_....jpg"
```

Doctrine: `social/RETURNER_DAILY_SOCIAL.md`
""",
                encoding="utf-8",
            )

        (day_dir / "README.md").write_text(
            f"""# Returner Daily — {day}

**Status:** draft scaffold  
**Generated:** {datetime.now().isoformat(timespec='seconds')}

## Slides (target)

| # | Type | File / path | Status |
|---|------|-------------|--------|
| 1 | Video (personality / talk peak) | see SOURCES.md | empty until path |
| 2 | Still (Memento / screenshot) | see SOURCES.md | empty until path |

## Rules

- Blanks beat fakes.  
- Do not tick FOOTAGE or series Recorded from this folder alone.  
- Redact secrets before any public derivative.

## Caption

See `caption.md`.
""",
            encoding="utf-8",
        )

        (day_dir / "caption.md").write_text(
            f"""# Caption draft — {day}

**Status:** scaffold — fill only from real night

## Feed

```
[one line what happened]

Returner energy · Thrall · Horde
```

## Optional positive friction

```
Friction tonight: …
Working around it by: …
Got a workaround?
```

## Do not

- Invent achievements  
- Name BN tags / gold stacks  
- Claim EP Recorded
""",
            encoding="utf-8",
        )

        sources = [
            f"# Sources — {day}",
            "",
            f"**Note:** {args.note or '—'}",
            "",
            "| Role | Path |",
            "|------|------|",
            f"| video | `{args.video or '—'}` |",
            f"| still | `{args.still or '—'}` |",
            "",
            "Pull candidates from:",
            "- `capture-inbox/latest.md`",
            "- `memento-inbox/latest.md`",
            "",
        ]
        (day_dir / "SOURCES.md").write_text("\n".join(sources), encoding="utf-8")

    except OSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(f"returner-daily scaffold -> {day_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
