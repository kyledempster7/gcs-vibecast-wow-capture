#!/usr/bin/env python3
"""
Log a vibe-cast / vibe-podcast session folder (scaffold only).

Does not invent media paths. Links Returner Daily + peak ledger + mode cards.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
STORY = WOW / "04-Story-and-Capture"
SESS = STORY / "vibe-sessions"
DAILY = STORY / "returner-daily"
MODES = ("play", "muddy", "clean", "duo", "deck")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    ap.add_argument("--mode", choices=MODES, default="muddy")
    ap.add_argument("--note", default="", help="Kyle one-liner if any")
    ap.add_argument("--game-audio", choices=("yes", "no", "unknown"), default="unknown")
    ap.add_argument("--scaffold-daily", action="store_true", help="also draft_returner_daily")
    args = ap.parse_args()

    day = args.day or datetime.now().strftime("%Y-%m-%d")
    day_dir = SESS / day
    day_dir.mkdir(parents=True, exist_ok=True)

    root_readme = SESS / "README.md"
    if not root_readme.is_file():
        root_readme.write_text(
            """# Vibe sessions

One folder per play/talk night. **Kyle does not fill these** — agents do after his optional one-liner.

Doctrine: `00-Index/VIBECAST_OS.md` · pipeline: `00-Index/VIBECAST_PIPELINE.md`

```bash
python3 wow-roster-tracker/scripts/log_vibe_session.py --mode muddy --note "muddy 40m"
```
""",
            encoding="utf-8",
        )

    if args.scaffold_daily or not (DAILY / day).is_dir():
        subprocess.run(
            [
                sys.executable,
                str(Path(__file__).parent / "draft_returner_daily.py"),
                "--day",
                day,
                "--note",
                f"vibe session {args.mode}",
            ],
            check=False,
        )

    mode_card = {
        "muddy": "YouTube/STREAM_MUDDY_TALK_CARD.md",
        "clean": "YouTube/FLIGHTPATH_VO_TOPICS_EP01.md",
        "play": "00-Index/KYLE_OS.md",
        "duo": "00-Index/KYLE_OS.md",
        "deck": "00-Index/KYLE_OS.md",
    }[args.mode]

    session = f"""# Vibe session — {day}

**Mode:** `{args.mode}`  
**Logged:** {datetime.now().isoformat(timespec='seconds')}  
**Game audio (claimed):** {args.game_audio}  
**Kyle one-liner:** {args.note or '—'}

## Product intent

| Mode | Primary harvest |
|------|-----------------|
| muddy | Returner Daily + peaks (vibe-cast) |
| clean | EP / vibe-podcast show-notes |
| play | Memento + B-roll paths only |
| duo / deck | light harvest |

## Agent checklist

- [ ] Capture inbox fresh
- [ ] Memento inbox fresh
- [ ] Returner Daily day folder exists
- [ ] Peaks table (only real timestamps)
- [ ] Stitch package NOT_ARMED when media real
- [ ] Show-notes only if clean or muddy→essay cut requested

## Links

- Mode card: `../{mode_card}`
- Returner day: `../returner-daily/{day}/`
- Peaks ledger: `../CLIP_PEAK_LEDGER.md`
- This peaks: `peaks.md`
- VibeCast OS: `../../00-Index/VIBECAST_OS.md`
"""
    (day_dir / "SESSION.md").write_text(session, encoding="utf-8")

    peaks = day_dir / "peaks.md"
    if not peaks.is_file():
        peaks.write_text(
            f"""# Peaks — {day}

**Rule:** real timestamps only. Empty is honest.

| t_start | t_end | Tag | Notes |
|---------|-------|-----|-------|
|  |  | `#talk-peak` / `#friction` / `#dk` / `#silent` |  |

Tags: `#talk-peak` `#friction` `#mac-silent` `#dk` `#undead` `#systems` `#cta` `#vibe`
Also copy keepers into `../CLIP_PEAK_LEDGER.md` when verified.
""",
            encoding="utf-8",
        )

    links = day_dir / "LINKS.md"
    links.write_text(
        f"""# Links — {day}

| Piece | Path |
|-------|------|
| Session | SESSION.md |
| Peaks | peaks.md |
| Returner Daily | ../returner-daily/{day}/ |
| Muddy card | ../YouTube/STREAM_MUDDY_TALK_CARD.md |
| Clean topics | ../YouTube/FLIGHTPATH_VO_TOPICS_EP01.md |
| Podcast scaffold | ../YouTube/podcast/ |
| Essay drop (Mac) | ~/Movies/WoW-Essays |
| Package stitch | wow-roster-tracker/scripts/stitch_returner_package.py |
""",
        encoding="utf-8",
    )

    # optional podcast show-note stub for clean (or muddy essay cut)
    if args.mode in ("clean", "muddy"):
        sn_root = STORY / "YouTube" / "podcast" / "show-notes"
        sn_root.mkdir(parents=True, exist_ok=True)
        sn = sn_root / f"{day}-vibe.md"
        if not sn.is_file():
            sn.write_text(
                f"""# Show notes — vibe {day}

**Status:** DRAFT scaffold  
**Mode:** {args.mode}  
**Audio path:** — (fill only when real file exists)  
**Title working:** Returner vibe — {day}

## Cold open (one line)

—

## Beats

1.  
2.  
3.  

## Chapters (after edit)

| t | label |
|---|-------|
|  |  |

## CTA

Soft Thrall / returner · no hard sell.

## Do not

Publish without Kyle go · invent chapters from empty audio.
""",
                encoding="utf-8",
            )

    print(f"vibe session -> {day_dir} mode={args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
