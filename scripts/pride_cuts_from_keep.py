#!/usr/bin/env python3
"""Cut pride reel variants from a KEEP master using motion windows. No publish."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

FF = "ffmpeg"
FP = "ffprobe"


def duration(path: Path) -> float:
    out = subprocess.check_output(
        [FP, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        text=True,
    ).strip()
    return float(out or "0")


def cut(src: Path, dest: Path, start: float, length: float) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    # re-encode for clean cuts (stream copy often wrong on keyframes)
    subprocess.run(
        [
            FF, "-y", "-ss", str(start), "-t", str(length), "-i", str(src),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k",
            str(dest),
        ],
        check=False, capture_output=True,
    )


def best_window(src: Path, length: float, step: float = 3.0) -> float:
    dur = duration(src)
    if dur <= length:
        return 0.0
    best_t, best_score = 0.0, -1e9
    t = 0.0
    while t + length <= dur + 0.05:
        r = subprocess.run(
            [FF, "-hide_banner", "-ss", str(t), "-t", str(length), "-i", str(src),
             "-vf", r"select='gt(scene,0.015)',showinfo", "-an", "-f", "null", "-"],
            capture_output=True, text=True,
        )
        hits = sum(1 for ln in (r.stderr or "").splitlines() if "pts_time" in ln)
        r2 = subprocess.run(
            [FF, "-hide_banner", "-ss", str(t), "-t", str(length), "-i", str(src),
             "-vf", "blackdetect=d=0.4:pix_th=0.12", "-an", "-f", "null", "-"],
            capture_output=True, text=True,
        )
        black = 0.0
        for line in (r2.stderr or "").splitlines():
            m = __import__("re").search(r"black_duration:([0-9.]+)", line)
            if m:
                black += float(m.group(1))
        score = hits - black * 3
        if score > best_score:
            best_score, best_t = score, t
        t += step
    return best_t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--score-json", type=Path, default=None)
    args = ap.parse_args()
    src = args.src
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    dur = duration(src)

    # 15s start (skip 1s)
    start_15 = 1.0 if dur > 16 else 0.0
    # mid 20s from score best_15 if present else motion
    mid_start = max(0.0, (dur - 20) / 2)
    best30 = best_window(src, 30.0, step=4.0) if dur >= 30 else 0.0
    best20 = best_window(src, 20.0, step=3.0) if dur >= 20 else mid_start

    if args.score_json and args.score_json.is_file():
        data = json.loads(args.score_json.read_text(encoding="utf-8"))
        for r in data.get("candidates") or []:
            if str(r.get("final_verdict", "")).upper() == "KEEP" and r.get("best_15s"):
                mid_start = float(r["best_15s"].get("start", mid_start))
                break

    jobs = [
        ("c-pride-15s-start.mp4", start_15, 15.0),
        ("c-pride-20s-mid.mp4", best20, min(20.0, dur)),
        ("c-pride-30s-best.mp4", best30, min(30.0, dur)),
    ]
    meta = []
    for name, st, ln in jobs:
        dest = out / name
        print(f"pride cut {name} start={st:.1f}s len={ln:.1f}s")
        cut(src, dest, st, ln)
        meta.append({"file": name, "start": st, "length": ln, "exists": dest.is_file(),
                     "bytes": dest.stat().st_size if dest.is_file() else 0})
    (out / "PRIDE_CUTS.json").write_text(json.dumps({"src": str(src), "cuts": meta}, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
