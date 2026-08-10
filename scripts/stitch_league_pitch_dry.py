#!/usr/bin/env python3
"""Dry-stitch Explorer’s League pitch from storyboard captured media only.

Uses real media_path rows. Trims each clip. Concat. NOT_ARMED. No invent.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

FF = "ffmpeg"
WOW = Path(__file__).resolve().parents[2]
STORY = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "EXPLORERS_LEAGUE_PITCH_STORYBOARD.json"
)
OUT_DIR = (
    WOW
    / "04-Story-and-Capture"
    / "social"
    / "package"
    / "pitch-montage-dry"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--storyboard", type=Path, default=STORY)
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--max-sec-per-clip", type=float, default=12.0)
    ap.add_argument("--max-clips", type=int, default=6)
    args = ap.parse_args()

    if not args.storyboard.is_file():
        print(f"stitch_pitch SKIP missing {args.storyboard}")
        return 0

    board = json.loads(args.storyboard.read_text(encoding="utf-8"))
    shot_by = {s["shot_id"]: s for s in board.get("shots") or []}
    # sequence order preferred; only captured with real path
    picked = []
    for step in board.get("sequence") or []:
        sid = step.get("shot_id")
        s = shot_by.get(sid) or {}
        mp = s.get("media_path")
        if not mp:
            continue
        p = Path(mp)
        if not p.is_file():
            continue
        picked.append(
            {
                "id": sid,
                "path": p,
                "flash_id": step.get("flash_id"),
                "keep_id": s.get("keep_id"),
            }
        )
        if len(picked) >= args.max_clips:
            break
    # also any captured not in sequence
    if len(picked) < 2:
        for s in board.get("shots") or []:
            if not s.get("captured") or not s.get("media_path"):
                continue
            p = Path(s["media_path"])
            if not p.is_file():
                continue
            if any(x["id"] == s["shot_id"] for x in picked):
                continue
            picked.append(
                {
                    "id": s["shot_id"],
                    "path": p,
                    "flash_id": None,
                    "keep_id": s.get("keep_id"),
                }
            )
            if len(picked) >= args.max_clips:
                break

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "schema": "gcs_league_pitch_stitch_dry/v1",
        "product_id": board.get("product_id"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "armed": False,
        "kyle_go": False,
        "status": "DRY",
        "picked": [
            {
                "shot_id": x["id"],
                "path": str(x["path"]),
                "flash_id": x.get("flash_id"),
                "keep_id": x.get("keep_id"),
            }
            for x in picked
        ],
        "law": "no invent · no silent publish · NOT_ARMED",
    }

    if len(picked) < 2:
        meta["status"] = "INSUFFICIENT_CLIPS"
        (out_dir / "STITCH_DRY.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(f"stitch_pitch INSUFFICIENT_CLIPS n={len(picked)} -> {out_dir}")
        return 0

    trim_dir = out_dir / "trim"
    trim_dir.mkdir(exist_ok=True)
    max_sec = max(3.0, float(args.max_sec_per_clip))
    list_lines = []
    for x in picked:
        trim_p = trim_dir / f"{x['id'].replace('.', '_')}-t{int(max_sec)}.mp4"
        if not trim_p.is_file() or trim_p.stat().st_size < 1000:
            tr = subprocess.run(
                [
                    FF,
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-ss",
                    "0",
                    "-t",
                    str(max_sec),
                    "-i",
                    str(x["path"]),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "23",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "96k",
                    str(trim_p),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if tr.returncode != 0 or not trim_p.is_file():
                print(f"WARN trim fail {x['id']}: {tr.stderr[-200:] if tr.stderr else ''}")
                continue
        list_lines.append(f"file '{str(trim_p).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'")

    if len(list_lines) < 2:
        meta["status"] = "INSUFFICIENT_TRIMS"
        (out_dir / "STITCH_DRY.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(f"stitch_pitch INSUFFICIENT_TRIMS -> {out_dir}")
        return 0

    list_path = out_dir / "concat.txt"
    list_path.write_text("\n".join(list_lines) + "\n", encoding="utf-8")
    out_mp4 = out_dir / "league-pitch-montage-dry.mp4"
    cmd = [
        FF,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        str(out_mp4),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if r.returncode != 0 or not out_mp4.is_file():
        meta["status"] = "FFMPEG_FAIL"
        meta["stderr"] = (r.stderr or "")[-500:]
        (out_dir / "STITCH_DRY.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(f"stitch_pitch FFMPEG_FAIL rc={r.returncode}")
        return 1

    meta["status"] = "DRY_OK"
    meta["out_mp4"] = str(out_mp4)
    meta["bytes"] = out_mp4.stat().st_size
    (out_dir / "STITCH_DRY.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (out_dir / "BOARD.md").write_text(
        f"""# League pitch montage dry

**Status:** DRY_OK · **Armed:** false  
**Clips:** {len(list_lines)} · **Out:** `{out_mp4.name}` ({meta['bytes']} bytes)

Sequence uses storyboard captured media only. Flash overlays not burned (HTML cards separate).

**Law:** no invent · no silent publish · NOT_ARMED until kyle_go
""",
        encoding="utf-8",
    )
    print(f"stitch_pitch DRY_OK n={len(list_lines)} bytes={meta['bytes']} -> {out_mp4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
