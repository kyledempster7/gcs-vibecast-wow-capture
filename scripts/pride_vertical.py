#!/usr/bin/env python3
"""Pride landscape → 9:16 vertical center-crop v0. No publish. No invent."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

FF = "ffmpeg"
FP = "ffprobe"


def probe_wh(path: Path) -> tuple[int, int, float]:
    r = subprocess.run(
        [
            FP,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    parts = (r.stdout or "").strip().split(",")
    if len(parts) < 2:
        return 0, 0, 0.0
    w = int(float(parts[0]))
    h = int(float(parts[1]))
    dur = float(parts[2]) if len(parts) > 2 and parts[2] else 0.0
    return w, h, dur


def make_vertical(src: Path, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    w, h, dur = probe_wh(src)
    if w <= 0 or h <= 0:
        return {"file": src.name, "status": "PROBE_FAIL"}
    # Center crop to 9:16, then scale to 1080x1920 if large enough else keep ratio
    # crop_w = h * 9/16 when landscape; if already 9:16, scale only
    if w / h <= 9 / 16 + 0.02:
        vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
        method = "pad_scale"
    else:
        # width of crop = height * 9/16
        vf = (
            "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
            "scale=1080:1920"
        )
        method = "center_crop_9x16"
    if dest.is_file() and dest.stat().st_size > 1000:
        ow, oh, _ = probe_wh(dest)
        return {
            "file": src.name,
            "out": dest.name,
            "status": "EXISTS",
            "src_wh": [w, h],
            "out_wh": [ow, oh],
            "method": method,
            "duration_sec": dur,
        }
    cmd = [
        FF,
        "-y",
        "-i",
        str(src),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if r.returncode != 0 or not dest.is_file():
        return {
            "file": src.name,
            "status": "FFMPEG_FAIL",
            "stderr": (r.stderr or "")[-400:],
        }
    ow, oh, od = probe_wh(dest)
    return {
        "file": src.name,
        "out": dest.name,
        "status": "OK",
        "src_wh": [w, h],
        "out_wh": [ow, oh],
        "method": method,
        "duration_sec": od or dur,
        "bytes": dest.stat().st_size,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--pride-dir",
        type=Path,
        required=True,
        help="…/candidates/pride (landscape cuts)",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="default: pride/vertical",
    )
    args = ap.parse_args()
    pride = args.pride_dir
    out_dir = args.out_dir or (pride / "vertical")
    if not pride.is_dir():
        print(f"missing pride dir {pride}")
        return 1
    results = []
    for src in sorted(pride.glob("*.mp4")):
        dest = out_dir / src.name
        print(f"vertical {src.name}")
        results.append(make_vertical(src, dest))
    report = {
        "schema": "gcs_pride_vertical/v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "pride_dir": str(pride),
        "out_dir": str(out_dir),
        "law": "no_publish_center_crop_v0",
        "clips": results,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    rep_path = out_dir / "VERTICAL.json"
    rep_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    ok = sum(1 for r in results if r.get("status") in ("OK", "EXISTS"))
    print(f"pride_vertical ok={ok}/{len(results)} -> {rep_path}")
    return 0 if results and ok == len(results) else (0 if not results else 1)


if __name__ == "__main__":
    raise SystemExit(main())
