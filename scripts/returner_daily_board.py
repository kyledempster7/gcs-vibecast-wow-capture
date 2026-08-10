#!/usr/bin/env python3
"""
Returner Daily status board (initiative 50).

Scans day folders + packages → 00-Index/RETURNER_DAILY_BOARD.md
product_ready only when media non-empty AND QA not HOLD-empty.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
INDEX = WOW / "00-Index"
DAILY = WOW / "04-Story-and-Capture" / "returner-daily"
DI = (
    Path.home()
    / "Library"
    / "Application Support"
    / "UAH"
    / "butler"
    / "control-plane"
    / "delivery-independence"
)
PKG_DIR = DI / "packages"


def role_path(sources: str, role: str) -> str | None:
    m = re.search(rf"\|\s*{re.escape(role)}\s*\|\s*`([^`]+)`", sources, re.I)
    if not m:
        return None
    val = m.group(1).strip()
    if val in ("—", "-", "", "none", "–"):
        return None
    return val


def day_row(day_dir: Path) -> dict:
    day = day_dir.name
    src = (day_dir / "SOURCES.md").read_text(encoding="utf-8") if (day_dir / "SOURCES.md").is_file() else ""
    video = role_path(src, "video")
    still = role_path(src, "still")
    media_n = int(bool(video)) + int(bool(still))
    skip = (day_dir / "SKIP_DAY.md").is_file()
    qa = ""
    if (day_dir / "QA.md").is_file():
        qa = (day_dir / "QA.md").read_text(encoding="utf-8")
    hold = "HOLD need real media" in qa or media_n == 0
    pkg = PKG_DIR / f"returner_daily_{day}.NOT_ARMED.json"
    pkg_media = None
    brand = "—"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            pkg_media = len(data.get("media") or [])
            brand = data.get("brand") or "—"
        except Exception:
            pkg_media = -1
    product_ready = media_n > 0 and pkg_media not in (0, None) and not hold
    status = (
        "SKIP"
        if skip and media_n == 0
        else ("HOLD_EMPTY" if media_n == 0 else ("DRAFT_MEDIA" if not product_ready else "MEDIA_READY"))
    )
    return {
        "day": day,
        "video": bool(video),
        "still": bool(still),
        "media_n": media_n,
        "pkg": pkg.is_file(),
        "pkg_media": pkg_media if pkg_media is not None else "—",
        "brand": brand,
        "status": status,
        "product_ready": product_ready,
    }


def main() -> int:
    rows: list[dict] = []
    if DAILY.is_dir():
        days = sorted(
            [p for p in DAILY.iterdir() if p.is_dir() and p.name[:4].isdigit()],
            key=lambda p: p.name,
            reverse=True,
        )
        rows = [day_row(d) for d in days]

    lines = [
        f"# Returner Daily board — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "**Rule:** `package present` ≠ product ready. `product_ready` needs real media paths.",
        "**Publish:** still requires Kyle go + NOT_ARMED arm path.",
        "",
        "| Day | Status | video | still | pkg media | brand | product_ready |",
        "|-----|--------|-------|-------|-----------|-------|---------------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['day']} | {r['status']} | {'Y' if r['video'] else '—'} | "
            f"{'Y' if r['still'] else '—'} | {r['pkg_media']} | {r['brand']} | "
            f"{'YES' if r['product_ready'] else 'NO'} |"
        )
    if not rows:
        lines.append("| — | no day folders | — | — | — | — | NO |")

    lines += [
        "",
        "## Counts",
        "",
        f"- days: **{len(rows)}**",
        f"- product_ready: **{sum(1 for r in rows if r['product_ready'])}**",
        f"- HOLD_EMPTY / SKIP: **{sum(1 for r in rows if r['status'] in ('HOLD_EMPTY', 'SKIP'))}**",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        "",
        "Scripts: `returner_daily_board.py` · `skip_day_receipt.py` · `qa_returner_daily.py`",
        "",
    ]
    out = INDEX / "RETURNER_DAILY_BOARD.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"board -> {out}")
    for r in rows[:10]:
        print(f"  {r['day']} {r['status']} media={r['media_n']} pkg_media={r['pkg_media']} ready={r['product_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
