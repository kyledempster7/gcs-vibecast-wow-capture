#!/usr/bin/env python3
"""
SCH-3: Capture-inbox lister — paths only, no FOOTAGE ticks, no media claims.

Scans a folder (default: Windows Videos\\WoW B-Roll) and writes a vault markdown
list of files by mtime. Empty inbox is a valid success (honest zero).

Exit: 0 ok | 1 bad args | 2 write error
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VAULT_OUT = ROOT.parent / "04-Story-and-Capture" / "capture-inbox"


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
        files = [p for p in inbox.rglob("*") if p.is_file()]
    except OSError as e:
        return [], f"{type(e).__name__}: {e}"

    def _rank(p: Path) -> tuple[int, float]:
        parts = {x.lower() for x in p.parts}
        name = p.name.lower()
        if "_receipts" in parts or name.startswith("obs_path_probe"):
            return (3, -p.stat().st_mtime)
        if "_scripts" in parts:
            return (3, -p.stat().st_mtime)
        if "candidates" in parts and name.endswith(".mp4"):
            return (0, -p.stat().st_mtime)
        if "raw" in parts and name.endswith(".mp4"):
            return (1, -p.stat().st_mtime)
        if name.endswith(".mp4"):
            return (2, -p.stat().st_mtime)
        return (4, -p.stat().st_mtime)

    files.sort(key=_rank)
    if since_hours is not None and since_hours > 0:
        cutoff = datetime.now().timestamp() - since_hours * 3600
        files = [p for p in files if p.stat().st_mtime >= cutoff]
    return files, None


def render(
    inbox: Path,
    files: list[Path],
    day: str,
    host: str,
    scan_note: str | None = None,
) -> str:
    lines = [
        f"# Capture inbox — {day}",
        "",
        f"**Host:** `{host}`  ",
        f"**Inbox path:** `{inbox}`  ",
        f"**Scanned:** {datetime.now().isoformat(timespec='seconds')}  ",
        f"**File count:** {len(files)}  ",
        "",
        "## Honesty rails",
        "",
        "- Paths only — **not** FOOTAGE_WISHLIST ticks.",
        "- Prefer `candidates/*.mp4` and `raw/*.mp4`. OBS `_receipts` probes are not masters.",
        "- Do **not** invent episode coverage from filenames.",
        "- When a real take matches a shot line, human/agent ticks FOOTAGE with this path.",
        "",
    ]
    if scan_note:
        lines += [
            "## Scan note",
            "",
            f"- {scan_note}",
            "",
        ]
    lines += [
        "## Files (newest first)",
        "",
    ]
    if not files:
        lines += [
            "_Empty or unreadable inbox — valid. No B-roll paths listed._",
            "",
        ]
    else:
        lines += [
            "| mtime local | size | path |",
            "|-------------|-----:|------|",
        ]
        for p in files:
            st = p.stat()
            mt = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            size = st.st_size
            lines.append(f"| {mt} | {size} | `{p}` |")
        lines.append("")

    lines += [
        "## Next (human or agent after play)",
        "",
        "1. Open `Games/WoW/community-surface/FOOTAGE_WISHLIST.md`.",
        "2. Match **one** P0/P1 line to a real path above (or skip).",
        "3. Optional: one line in `04-Story-and-Capture/broll-log/YYYY-MM-DD.md`.",
        "",
        "Related: [[../community-surface/FOOTAGE_WISHLIST|FOOTAGE_WISHLIST]] · [[../broll-log/README|broll-log]]",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="List WoW B-roll inbox paths into vault")
    ap.add_argument(
        "--inbox",
        type=Path,
        default=None,
        help="Folder to scan (required unless default env path used)",
    )
    ap.add_argument("--vault-out", type=Path, default=DEFAULT_VAULT_OUT)
    ap.add_argument("--day", default=None)
    ap.add_argument("--host", default="local")
    ap.add_argument("--since-hours", type=float, default=None)
    ap.add_argument(
        "--max-files",
        type=int,
        default=80,
        help="Cap listed files (newest first). 0 = no cap.",
    )
    ap.add_argument(
        "--allow-missing-inbox",
        action="store_true",
        help="Write empty report if inbox folder missing (default: still write empty)",
    )
    args = ap.parse_args()

    inbox = args.inbox
    if inbox is None:
        # Prefer trusted D: storage (C:\\Users\\...\\Videos can hit WinError 448)
        candidates = [
            Path(r"D:\WoW B-Roll Storage"),
            Path(r"D:\Codex Review Queue\B-Roll Candidates"),
            Path(r"C:\Users\kyled\Videos\WoW B-Roll"),
            Path.home() / "Movies" / "WoW B-Roll",
        ]
        inbox = candidates[0]
        for c in candidates:
            ok, _ = safe_is_dir(c)
            if ok:
                inbox = c
                break

    day = args.day or datetime.now().strftime("%Y-%m-%d")
    files, scan_err = list_files(inbox, args.since_hours)
    total = len(files)
    if args.max_files and args.max_files > 0 and len(files) > args.max_files:
        files = files[: args.max_files]
    scan_note = None
    if scan_err:
        scan_note = (
            f"Could not fully traverse inbox ({scan_err}). "
            "Honest empty list written. If Windows marks Videos as untrusted mount, "
            "use D:\\WoW B-Roll Storage or another trusted path."
        )
    elif total > len(files):
        scan_note = f"Listed newest {len(files)} of {total} files (cap --max-files={args.max_files})."
    md = render(inbox, files, day, args.host, scan_note=scan_note)

    out_dir = args.vault_out
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        day_path = out_dir / f"{day}.md"
        latest = out_dir / "latest.md"
        day_path.write_text(md, encoding="utf-8")
        latest.write_text(md, encoding="utf-8")
        readme = out_dir / "README.md"
        if not readme.is_file():
            readme.write_text(
                """# Capture inbox

**Role:** Path lists from Windows `Videos\\WoW B-Roll` (or Mac Movies mirror if used).  
**Not:** FOOTAGE ticks · publish claims · invented masters.

```bash
python3 scripts/list_capture_inbox.py --inbox "C:/Users/kyled/Videos/WoW B-Roll" --host windows
```

SCH-3 on automation board. Empty is honest success.
""",
                encoding="utf-8",
            )
    except OSError as e:
        print(f"ERROR write: {e}", file=sys.stderr)
        return 2

    ok, _ = safe_is_dir(inbox)
    print(
        f"capture-inbox -> {day_path} count={len(files)} "
        f"inbox_reachable={ok} scan_err={scan_err or 'none'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
