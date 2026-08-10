#!/usr/bin/env python3
"""
SCH-6: Memento / Screenshots inbox — paths only, no FOOTAGE ticks.

Default inbox: retail WoW Screenshots (Memento + manual shots).
Writes vault markdown under 04-Story-and-Capture/memento-inbox/.

Exit: 0 ok | 1 bad args | 2 write error
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VAULT_OUT = ROOT.parent / "04-Story-and-Capture" / "memento-inbox"
DEFAULT_SCREENSHOTS = Path(
    r"C:\Program Files (x86)\World of Warcraft\_retail_\Screenshots"
)


def safe_is_dir(path: Path) -> tuple[bool, str | None]:
    try:
        return path.is_dir(), None
    except OSError as e:
        return False, f"{type(e).__name__}: {e}"


def list_files(inbox: Path, since_hours: float | None) -> tuple[list[Path], str | None]:
    ok, err = safe_is_dir(inbox)
    if not ok:
        return [], err or "inbox not a directory"
    try:
        files = [p for p in inbox.iterdir() if p.is_file()]
    except OSError as e:
        return [], f"{type(e).__name__}: {e}"
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if since_hours is not None and since_hours > 0:
        cutoff = datetime.now().timestamp() - since_hours * 3600
        files = [p for p in files if p.stat().st_mtime >= cutoff]
    return files, None


def render(
    inbox: Path,
    files: list[Path],
    day: str,
    host: str,
    total: int,
    scan_note: str | None = None,
) -> str:
    lines = [
        f"# Memento / Screenshots inbox — {day}",
        "",
        f"**Host:** `{host}`  ",
        f"**Inbox path:** `{inbox}`  ",
        f"**Scanned:** {datetime.now().isoformat(timespec='seconds')}  ",
        f"**Listed:** {len(files)} of {total}  ",
        "",
        "## Honesty rails",
        "",
        "- Paths only — **not** FOOTAGE ticks · **not** auto-publish.",
        "- Raw Memento is not publish-ready until redacted/selected.",
        "- Prefer achievement / meaningful moments over interval spam.",
        "- Returner Daily stills: pick **one** hero still per draft day.",
        "",
    ]
    if scan_note:
        lines += ["## Scan note", "", f"- {scan_note}", ""]
    lines += ["## Files (newest first)", ""]
    if not files:
        lines += ["_Empty or unreadable — valid._", ""]
    else:
        lines += [
            "| mtime local | size | name |",
            "|-------------|-----:|------|",
        ]
        for p in files:
            st = p.stat()
            mt = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"| {mt} | {st.st_size} | `{p.name}` |")
        lines.append("")
        lines.append(f"Full path prefix: `{inbox}`")
        lines.append("")

    lines += [
        "## Next",
        "",
        "1. Pick 0–1 stills for Returner Daily (`returner-daily/YYYY-MM-DD/`).",
        "2. Redact BN tags / gold / mail before any public derivative.",
        "3. Optional: map to FOOTAGE only after content watch.",
        "",
        "Related: [[../social/RETURNER_DAILY_SOCIAL|Returner Daily]] · capture-inbox",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="List WoW Screenshots/Memento into vault")
    ap.add_argument("--inbox", type=Path, default=None)
    ap.add_argument("--vault-out", type=Path, default=DEFAULT_VAULT_OUT)
    ap.add_argument("--day", default=None)
    ap.add_argument("--host", default="local")
    ap.add_argument("--since-hours", type=float, default=None)
    ap.add_argument("--max-files", type=int, default=40)
    args = ap.parse_args()

    inbox = args.inbox or DEFAULT_SCREENSHOTS
    day = args.day or datetime.now().strftime("%Y-%m-%d")
    files, scan_err = list_files(inbox, args.since_hours)
    total = len(files)
    listed = files
    if args.max_files and args.max_files > 0 and len(listed) > args.max_files:
        listed = listed[: args.max_files]

    scan_note = None
    if scan_err:
        scan_note = f"Could not fully traverse ({scan_err})."
    elif total > len(listed):
        scan_note = f"Listed newest {len(listed)} of {total} (cap --max-files={args.max_files})."

    md = render(inbox, listed, day, args.host, total, scan_note=scan_note)
    try:
        args.vault_out.mkdir(parents=True, exist_ok=True)
        day_path = args.vault_out / f"{day}.md"
        latest = args.vault_out / "latest.md"
        day_path.write_text(md, encoding="utf-8")
        latest.write_text(md, encoding="utf-8")
        readme = args.vault_out / "README.md"
        if not readme.is_file():
            readme.write_text(
                """# Memento / Screenshots inbox

**Source:** retail `Screenshots` (Memento + manual).  
**Role:** path lists for Returner Daily stills. Not publish-ready raw.

```bash
python scripts/list_memento_inbox.py --host windows-3900x
```

SCH-6 on automation board.
""",
                encoding="utf-8",
            )
    except OSError as e:
        print(f"ERROR write: {e}", file=sys.stderr)
        return 2

    ok, _ = safe_is_dir(inbox)
    print(
        f"memento-inbox -> {day_path} listed={len(listed)} total={total} "
        f"reachable={ok} err={scan_err or 'none'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
