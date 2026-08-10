#!/usr/bin/env python3
"""Map real KEEP clips → Explorer’s League pitch storyboard shot_ids.

Fail-closed:
- never invent media paths
- only attach if file exists under day-dir candidates/
- armed stays false
- without KEEP or without --map / --auto-suggest hits, SKIP cleanly

product_id: twe_explorers_league_community_pitch_v1
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PRODUCT_ID = "twe_explorers_league_community_pitch_v1"
WOW = Path(__file__).resolve().parents[2]
STORYBOARD = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_STORYBOARD.json"
)
PROGRESS = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_PROGRESS.md"
)

# Keyword hints for *suggestions only* — never auto-claim without file
SUGGEST_RULES: list[tuple[str, str]] = [
    (r"orbit|around.?toon", "pitch.hub_thrall"),  # weak: hub-like beauty
    (r"gather|herb|mine|node", "pitch.gather_to_craft"),
    (r"craft|profession|enchant|disenchant", "pitch.craft_cast"),
    (r"ah|auction", "pitch.ah_browse"),
    (r"dungeon|queue|finder", "pitch.dungeon_door"),
    (r"fly|flight|travel", "pitch.flight_soft"),
    (r"select|cast|lineup", "pitch.cast_lineup"),
]


def load_verdicts(day_dir: Path) -> dict:
    hv = day_dir / "analysis" / "human_verdicts.json"
    if not hv.is_file():
        return {}
    raw = json.loads(hv.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("verdicts"), dict):
        raw = raw["verdicts"]
    if not isinstance(raw, dict):
        return {}
    out: dict = {}
    for k, v in raw.items():
        if isinstance(v, dict) and "verdict" in v:
            out[str(k)] = v
        elif isinstance(v, str) and v.strip():
            out[str(k)] = {"verdict": v.strip(), "reason": ""}
    return out


def resolve_clip(day_dir: Path, cid: str) -> Path | None:
    cand = day_dir / "candidates"
    pride = cand / "pride"
    for root in (cand, pride, pride / "vertical", pride / "gated"):
        if not root.is_dir():
            continue
        for p in root.glob("*.mp4"):
            stem = p.stem
            if cid == stem or f"-{cid}-" in stem or stem.endswith(f"-{cid}"):
                if len(cid) <= 2 and cid.isalpha():
                    if stem.startswith("db-") and f"-{cid}-" in stem:
                        return p
                    continue
                return p
    if len(cid) <= 2:
        for p in sorted(cand.glob(f"db-*-{cid}-*.mp4")):
            return p
    return None


def keeps(verdicts: dict) -> dict:
    return {
        k: v
        for k, v in verdicts.items()
        if str(v.get("verdict", "")).upper() in ("KEEP", "PRIDE_PICK")
    }


def suggest(keep_id: str, reason: str) -> str | None:
    blob = f"{keep_id} {reason}".lower()
    for pat, shot in SUGGEST_RULES:
        if re.search(pat, blob, re.I):
            return shot
    return None


def write_progress(board: dict, day: str, attachments: list[dict]) -> None:
    lines = [
        "---",
        "type: pitch-progress",
        f"product_id: {PRODUCT_ID}",
        f"updated: {board.get('last_map_utc') or datetime.now(timezone.utc).isoformat()}",
        "armed: false",
        "---",
        "",
        "# Explorer’s League pitch — capture progress",
        "",
        f"**Day source:** {day}",
        f"**Shots captured (path attached):** {board.get('captured_n', 0)} / {board.get('shots_n', 0)}",
        f"**Armed:** false",
        "",
        "## Attachments this run",
        "",
    ]
    if not attachments:
        lines.append("_None — waiting for KEEP + explicit map or --auto-suggest with real files._")
    else:
        lines.append("| keep_id | shot_id | path | mode |")
        lines.append("|---------|---------|------|------|")
        for a in attachments:
            lines.append(
                f"| `{a['keep_id']}` | `{a['shot_id']}` | `{a['path']}` | {a['mode']} |"
            )
    lines += [
        "",
        "## Shot board",
        "",
        "| shot_id | captured | media_path |",
        "|---------|----------|------------|",
    ]
    for s in board.get("shots") or []:
        mp = s.get("media_path") or "—"
        lines.append(
            f"| `{s.get('shot_id')}` | {'yes' if s.get('captured') else 'no'} | {mp} |"
        )
    lines += [
        "",
        "## Next",
        "",
        "1. Capture remaining P0 shots (hub · craft · gather).",
        "2. KEEP in review-pack.",
        "3. `map_keep_to_league_pitch.py --day-dir … --auto-suggest` or `--map keep=shot`.",
        "",
    ]
    PROGRESS.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    ap.add_argument(
        "--storyboard",
        type=Path,
        default=STORYBOARD,
        help="Storyboard JSON to update",
    )
    ap.add_argument(
        "--map",
        action="append",
        default=[],
        help="keep_id=shot_id (repeatable). Example: --map c=pitch.hub_thrall",
    )
    ap.add_argument(
        "--auto-suggest",
        action="store_true",
        help="Suggest maps from KEEP reasons; only attach if file exists",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Write storyboard + progress (default dry-run print)",
    )
    args = ap.parse_args()
    day_dir = args.day_dir.resolve()
    if not day_dir.is_dir():
        print(f"map_pitch SKIP no_day_dir {day_dir}")
        return 0

    verdicts = load_verdicts(day_dir)
    k = keeps(verdicts)
    if not k:
        print(f"map_pitch SKIP no_KEEP day={day_dir.name}")
        return 0

    # build map plan
    plan: list[tuple[str, str, str]] = []  # keep_id, shot_id, mode
    for item in args.map:
        if "=" not in item:
            print(f"WARN bad --map {item}")
            continue
        kid, shot = item.split("=", 1)
        plan.append((kid.strip(), shot.strip(), "explicit"))

    if args.auto_suggest:
        for kid, v in k.items():
            shot = suggest(kid, v.get("reason") or "")
            if shot:
                # don't override explicit
                if any(p[0] == kid for p in plan):
                    continue
                plan.append((kid, shot, "auto_suggest"))

    if not plan:
        print(
            f"map_pitch SKIP no_plan keeps={list(k.keys())} "
            f"(pass --map keep=shot_id and/or --auto-suggest)"
        )
        return 0

    if not args.storyboard.is_file():
        print(f"map_pitch FAIL missing storyboard {args.storyboard}")
        return 2

    board = json.loads(args.storyboard.read_text(encoding="utf-8"))
    shot_by_id = {s["shot_id"]: s for s in board.get("shots") or [] if s.get("shot_id")}
    attachments: list[dict] = []
    skipped: list[str] = []

    for kid, shot_id, mode in plan:
        if shot_id not in shot_by_id:
            skipped.append(f"{kid}->{shot_id} unknown_shot")
            continue
        path = resolve_clip(day_dir, kid)
        if not path or not path.is_file():
            skipped.append(f"{kid}->{shot_id} missing_file")
            continue
        # attach
        shot_by_id[shot_id]["media_path"] = str(path.resolve())
        shot_by_id[shot_id]["captured"] = True
        shot_by_id[shot_id]["keep_id"] = kid
        shot_by_id[shot_id]["map_mode"] = mode
        attachments.append(
            {
                "keep_id": kid,
                "shot_id": shot_id,
                "path": str(path.resolve()),
                "mode": mode,
            }
        )

    board["shots"] = list(shot_by_id.values()) if shot_by_id else board.get("shots")
    # preserve order from original if possible
    if board.get("shots") and isinstance(board["shots"], list):
        # rebuild from shot_by_id using original order
        orig = json.loads(args.storyboard.read_text(encoding="utf-8")).get("shots") or []
        ordered = []
        for s in orig:
            sid = s.get("shot_id")
            ordered.append(shot_by_id.get(sid, s))
        board["shots"] = ordered

    board["captured_n"] = sum(1 for s in board.get("shots") or [] if s.get("captured"))
    board["ready_to_edit"] = board["captured_n"] >= 1
    board["armed"] = False
    board["kyle_go"] = False
    board["last_map_utc"] = datetime.now(timezone.utc).isoformat()
    board["last_map_day"] = day_dir.name
    board["product_id"] = PRODUCT_ID

    print(
        f"map_pitch plan={len(plan)} attached={len(attachments)} skipped={len(skipped)} "
        f"captured_n={board['captured_n']}"
    )
    for a in attachments:
        print(f"  ATTACH {a['keep_id']} -> {a['shot_id']} ({a['mode']})")
    for s in skipped:
        print(f"  SKIP {s}")

    if not args.apply:
        print("DRY_RUN (pass --apply to write storyboard + progress)")
        return 0

    args.storyboard.write_text(json.dumps(board, indent=2) + "\n", encoding="utf-8")
    write_progress(board, day_dir.name, attachments)
    print(f"WROTE {args.storyboard}")
    print(f"WROTE {PROGRESS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
