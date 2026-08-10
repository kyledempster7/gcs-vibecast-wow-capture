#!/usr/bin/env python3
"""Orbit / fly / still auto-tag v0 from scene + freeze heuristics.

Tags only — never invents FOOTAGE, never publishes.
Heuristics (v0, not ML):
  - high scene_hits + moderate freeze → orbit-ish (camera rotate)
  - sustained high motion + long duration → fly/travel-ish
  - high freeze_frac → still / load / freeze
  - low motion short → static beauty or load
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

FF = "ffmpeg"
FP = "ffprobe"


def duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            FP, "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        text=True,
    ).strip()
    return float(out or "0")


def freezedetect_total(path: Path) -> float:
    r = subprocess.run(
        [FF, "-hide_banner", "-i", str(path),
         "-vf", "freezedetect=n=0.003:d=0.8", "-an", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    total = 0.0
    for line in (r.stderr or "").splitlines():
        m = re.search(r"freeze_duration:\s*([0-9.]+)", line)
        if m:
            total += float(m.group(1))
    return total


def scene_hits(path: Path, window: float | None = None) -> int:
    """Count scene changes. If window set, sample mid portion only."""
    cmd = [FF, "-hide_banner"]
    if window:
        dur = duration(path)
        ss = max(0.0, (dur - window) / 2.0) if dur > window else 0.0
        cmd += ["-ss", str(ss), "-t", str(window)]
    cmd += [
        "-i", str(path),
        "-vf", r"select='gt(scene,0.015)',showinfo",
        "-an", "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return sum(
        1 for ln in (r.stderr or "").splitlines()
        if "pts_time" in ln and "showinfo" in ln
    )


def classify(path: Path) -> dict:
    dur = duration(path)
    size = path.stat().st_size
    bps = size / dur if dur > 0 else 0
    freeze = freezedetect_total(path)
    freeze_frac = freeze / dur if dur else 0
    # sample middle 15s for motion density when long
    w = 15.0 if dur >= 20 else None
    hits = scene_hits(path, window=w)
    hits_per_s = hits / (w or max(dur, 0.001))

    tags: list[str] = []
    shot = "unknown"
    conf = 0.3
    reasons: list[str] = []

    if freeze_frac >= 0.55 or (bps < 400_000 and dur >= 15):
        shot = "still_or_load"
        conf = 0.75
        tags = ["shot=still", "risk=load_or_freeze"]
        reasons.append("high_freeze_or_tiny")
    elif hits_per_s >= 1.2 and freeze_frac < 0.25:
        # many scene edges, not frozen → likely camera orbit / rotate
        shot = "orbit"
        conf = 0.55 if hits_per_s < 2.5 else 0.7
        tags = ["shot=orbit", "auto_tag=v0"]
        reasons.append("dense_scene_edges")
    elif hits_per_s >= 0.4 and freeze_frac < 0.35 and dur >= 20:
        shot = "fly_or_travel"
        conf = 0.5
        tags = ["shot=fly", "auto_tag=v0"]
        reasons.append("sustained_motion")
    elif hits_per_s < 0.15 and freeze_frac < 0.4:
        shot = "static_beauty"
        conf = 0.45
        tags = ["shot=static", "auto_tag=v0"]
        reasons.append("low_motion_clean")
    else:
        shot = "gameplay"
        conf = 0.4
        tags = ["shot=gameplay", "auto_tag=v0"]
        reasons.append("default_gameplay")

    # filename hints — override when name is stronger than crude motion density
    name = path.name.lower()
    if "orbit" in name:
        tags.append("name_hint=orbit")
        if shot not in ("still_or_load",):
            shot = "orbit"
            conf = max(conf, 0.65)
            tags = [t for t in tags if not t.startswith("shot=")] + ["shot=orbit", "auto_tag=v0", "name_hint=orbit"]
            reasons.append("name_hint_orbit_override")
    if "h1" in name or "hero" in name or "fly" in name:
        tags.append("name_hint=fly_hero")
        # h1/hero slices are travel establishes, not camera orbits around toon
        if shot not in ("still_or_load",):
            shot = "fly_or_travel"
            conf = max(conf, 0.6)
            tags = [t for t in tags if not t.startswith("shot=")] + [
                "shot=fly", "auto_tag=v0", "name_hint=fly_hero"
            ]
            reasons.append("name_hint_fly_hero_override")

    return {
        "filename": path.name,
        "path": str(path),
        "duration_sec": round(dur, 3),
        "bytes": size,
        "bytes_per_sec": int(bps),
        "freeze_frac": round(min(freeze_frac, 1.5), 3),
        "scene_hits_window": hits,
        "hits_per_sec": round(hits_per_s, 3),
        "shot": shot,
        "confidence": conf,
        "tags": tags,
        "reasons": reasons,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, required=True, help="candidates or clips dir")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--glob", default="*.mp4")
    args = ap.parse_args()

    rows = []
    for p in sorted(args.dir.glob(args.glob)):
        if not p.is_file():
            continue
        row = classify(p)
        rows.append(row)
        print(f"{row['shot']}\tc={row['confidence']}\thps={row['hits_per_sec']}\t{row['filename'][:48]}")

    report = {
        "schema": "gcs_motion_shot_tag/v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dir": str(args.dir),
        "law": "tag_only_no_publish_no_invent",
        "clips": rows,
        "by_shot": {},
    }
    for r in rows:
        report["by_shot"].setdefault(r["shot"], []).append(r["filename"])

    out = args.out or (args.dir.parent / "analysis" / "MOTION_TAGS.json")
    if args.dir.name in ("candidates", "clips", "pride"):
        out = args.out or (args.dir.parent / "analysis" / "MOTION_TAGS.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "by_shot": report["by_shot"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
