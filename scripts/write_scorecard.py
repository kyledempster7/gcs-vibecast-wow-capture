#!/usr/bin/env python3
"""
SCH-2: Daily character scorecard from two roster JSON snapshots.

Compares newest roster_snapshot_*.json (or latest.json) to prior stamp.
Writes Characters/scorecards/YYYY-MM-DD.md + latest.md.

Fail-closed: blanks over guesses. No gold/bags unless present in snapshot.
Exit: 0 ok | 1 missing data | 2 write error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
SCORE_DIR = ROOT.parent / "Characters" / "scorecards"


def _num(v):
    if v is None or v == "—" or v == "-":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None


def load_snap(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_char(c: dict) -> dict:
    """Support care-suite (avg_ilvl) and legacy Windows dumps (average_item_level)."""
    row = dict(c)
    if row.get("avg_ilvl") in (None, "", "—", "-"):
        if row.get("average_item_level") is not None:
            row["avg_ilvl"] = row["average_item_level"]
    if row.get("equipped_ilvl") in (None, "", "—", "-"):
        if row.get("equipped_item_level") is not None:
            row["equipped_ilvl"] = row["equipped_item_level"]
    if not row.get("source"):
        row["source"] = row.get("mode") or "—"
    return row


def index_chars(snap: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    chars = snap.get("characters") or snap.get("roster") or []
    for c in chars:
        if not isinstance(c, dict):
            continue
        name = c.get("name")
        if name:
            out[str(name)] = normalize_char(c)
    return out


def snap_quality(path: Path) -> tuple[int, int, str]:
    """Higher is better: prefer care-six + ilvl fields over thin legacy dumps."""
    try:
        snap = load_snap(path)
    except Exception:
        return (-1, 0, path.name)
    idx = index_chars(snap)
    n = len(idx)
    with_ilvl = sum(1 for c in idx.values() if _num(c.get("avg_ilvl")) is not None)
    return (n, with_ilvl, path.name)


def list_snapshots(output: Path) -> list[Path]:
    snaps = sorted(output.glob("roster_snapshot_*.json"), key=lambda p: p.name)
    return snaps


def pick_pair(output: Path, current: Path | None, prior: Path | None) -> tuple[Path, Path | None]:
    if current and prior:
        return current, prior
    snaps = list_snapshots(output)
    latest = output / "latest.json"
    # Rank by care-six coverage then stamp name (newest last among equals)
    ranked = sorted(snaps, key=lambda p: (snap_quality(p)[0], snap_quality(p)[1], p.name))
    if current is None:
        if ranked:
            # Prefer highest quality; break ties toward newest name
            best_n, best_ilvl, _ = snap_quality(ranked[-1])
            candidates = [p for p in ranked if snap_quality(p)[0] == best_n]
            # Among full-care or best n, prefer ones with ilvl then newest stamp
            candidates = sorted(
                candidates,
                key=lambda p: (snap_quality(p)[1], p.name),
            )
            current = candidates[-1]
        elif latest.is_file():
            current = latest
        else:
            raise FileNotFoundError(f"No roster snapshots under {output}")
    if prior is None:
        prior = None
        try:
            cur_stamp = load_snap(current).get("stamp")
        except Exception:
            cur_stamp = None
        # Prefer prior with same quality band (care six) if possible
        cur_n, _, _ = snap_quality(current) if current.exists() else (0, 0, "")
        pool = [p for p in ranked if p.resolve() != current.resolve()]
        same_band = [p for p in pool if snap_quality(p)[0] == cur_n]
        search = same_band or pool
        for p in reversed(search):
            try:
                st = load_snap(p).get("stamp")
            except Exception:
                st = None
            if cur_stamp and st == cur_stamp:
                continue
            prior = p
            break
    return current, prior


def render(cur: dict, pri: dict | None, day: str) -> str:
    cur_idx = index_chars(cur)
    pri_idx = index_chars(pri) if pri else {}
    cur_stamp = cur.get("stamp", "?")
    pri_stamp = pri.get("stamp", "—") if pri else "—"
    mode = cur.get("mode", "?")
    names = sorted(set(cur_idx) | set(pri_idx), key=str.lower)

    lines = [
        f"# Daily character scorecard — {day}",
        "",
        f"**Current:** `{cur_stamp}` mode `{mode}`  ",
        f"**Prior:** `{pri_stamp}`  ",
        "",
        "| Name | Level now | Level prior | Spec | ilvl now | ilvl prior | Δ level | Δ ilvl | Source |",
        "|------|----------:|------------:|------|---------:|-----------:|--------:|-------:|--------|",
    ]
    moved: list[str] = []
    for name in names:
        c = cur_idx.get(name, {})
        p = pri_idx.get(name, {})
        ln = _num(c.get("level"))
        lp = _num(p.get("level"))
        inow = _num(c.get("avg_ilvl"))
        ipri = _num(p.get("avg_ilvl"))
        spec = c.get("active_spec") or p.get("active_spec") or "—"
        src = c.get("source") or p.get("source") or "—"
        dlev = ""
        dilvl = ""
        if ln is not None and lp is not None:
            d = ln - lp
            if d:
                dlev = f"{d:+g}"
                moved.append(f"{name} level {lp}→{ln}")
        if inow is not None and ipri is not None:
            d = inow - ipri
            if d:
                dilvl = f"{d:+g}"
                moved.append(f"{name} ilvl {ipri}→{inow}")
        lines.append(
            f"| **{name}** | {ln if ln is not None else '—'} | {lp if lp is not None else '—'} | "
            f"{spec} | {inow if inow is not None else '—'} | {ipri if ipri is not None else '—'} | "
            f"{dlev or '—'} | {dilvl or '—'} | `{src}` |"
        )

    lines += ["", "## What moved", ""]
    if moved:
        for m in moved:
            lines.append(f"- {m}")
    else:
        lines.append("- No level/ilvl deltas vs prior snapshot (or first pull).")
    lines += [
        "",
        "## Human half (optional · fill after play)",
        "",
        "| Field | Value |",
        "|-------|-------|",
        "| Played |  |",
        "| Intent hit? |  |",
        "| One line |  |",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="WoW care-six scorecard from roster snapshots")
    ap.add_argument("--output", type=Path, default=OUTPUT)
    ap.add_argument("--score-dir", type=Path, default=SCORE_DIR)
    ap.add_argument("--current", type=Path, default=None)
    ap.add_argument("--prior", type=Path, default=None)
    ap.add_argument("--day", default=None, help="YYYY-MM-DD (default: today local)")
    args = ap.parse_args()

    try:
        cur_path, pri_path = pick_pair(args.output, args.current, args.prior)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    cur = load_snap(cur_path)
    pri = load_snap(pri_path) if pri_path and pri_path.is_file() else None
    day = args.day or datetime.now().strftime("%Y-%m-%d")

    md = render(cur, pri, day)
    args.score_dir.mkdir(parents=True, exist_ok=True)
    day_path = args.score_dir / f"{day}.md"
    latest = args.score_dir / "latest.md"
    try:
        day_path.write_text(md, encoding="utf-8")
        latest.write_text(md, encoding="utf-8")
    except OSError as e:
        print(f"ERROR write: {e}", file=sys.stderr)
        return 2

    print(f"scorecard -> {day_path}")
    print(f"scorecard latest -> {latest}")
    print(f"pair current={cur_path.name} prior={pri_path.name if pri_path else 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
