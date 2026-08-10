#!/usr/bin/env python3
"""Chat presence in bottom-left ROI (v1.1 majority). Blur only if chat_present or --force.

v1.1: decision=majority default (max alone caused 223313 FP cluster).
Fixture: clean orbit (no chat) must score false; pride must stay false.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

FF = "ffmpeg"
FP = "ffprobe"

# Tighter BL ROI (v1.1): chat sits lower-left; combat UI mid-left was inflating edge_bl.
ROI_X0, ROI_X1 = 0.012, 0.22
ROI_Y0, ROI_Y1 = 0.68, 0.97


def duration(p: Path) -> float:
    return float(
        subprocess.check_output(
            [
                FP,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(p),
            ],
            text=True,
        ).strip()
        or "0"
    )


def sample_frames(src: Path, n: int = 6) -> list[Path]:
    dur = duration(src)
    outdir = Path(tempfile.mkdtemp(prefix="chatdet_"))
    paths = []
    for i in range(n):
        t = (dur * (i + 0.5) / n) if dur > 0 else float(i)
        dest = outdir / f"f{i:02d}.png"
        subprocess.run(
            [FF, "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", str(dest)],
            capture_output=True,
        )
        if dest.is_file():
            paths.append(dest)
    return paths


def load_rgb(path: Path) -> tuple[int, int, bytes]:
    w = int(
        subprocess.check_output(
            [
                FP,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
    )
    h = int(
        subprocess.check_output(
            [
                FP,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=height",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
    )
    raw = path.with_suffix(".raw")
    subprocess.run(
        [FF, "-y", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", str(raw)],
        capture_output=True,
    )
    data = raw.read_bytes()
    raw.unlink(missing_ok=True)
    return w, h, data


def roi_edge(w: int, h: int, data: bytes, x0: int, y0: int, x1: int, y1: int) -> float:
    edge = 0.0
    n = 0
    prev = None
    for y in range(y0, y1):
        row = y * w * 3
        prev = None
        for x in range(x0, x1):
            i = row + x * 3
            yv = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]
            if prev is not None:
                edge += abs(yv - prev)
            prev = yv
            n += 1
    return edge / max(n, 1)


def score_frame(path: Path) -> dict:
    w, h, data = load_rgb(path)
    x0, x1 = int(w * ROI_X0), int(w * ROI_X1)
    y0, y1 = int(h * ROI_Y0), int(h * ROI_Y1)
    cx0, cx1 = int(w * 0.35), int(w * 0.65)
    cy0, cy1 = int(h * 0.35), int(h * 0.65)
    e_bl = roi_edge(w, h, data, x0, y0, x1, y1)
    e_c = roi_edge(w, h, data, cx0, cy0, cx1, cy1)
    ratio = e_bl / (e_c + 1e-6)
    chat_score = min(1.0, max(0.0, (ratio - 0.85) / 1.5))
    return {
        "edge_bl": round(e_bl, 4),
        "edge_center": round(e_c, 4),
        "edge_ratio": round(ratio, 4),
        "chat_score": round(chat_score, 4),
        "roi": {"x0": x0, "y0": y0, "x1": x1, "y1": y1, "w": w, "h": h},
    }


def detect(
    src: Path,
    threshold: float = 0.45,
    decision: str = "majority",
) -> dict:
    scores = []
    for f in sample_frames(src, 6):
        try:
            scores.append(score_frame(f))
        except Exception as e:
            scores.append({"error": str(e), "chat_score": 0.0})
    vals = [float(s.get("chat_score", 0.0)) for s in scores]
    avg = sum(vals) / len(vals) if vals else 0.0
    mx = max(vals) if vals else 0.0
    n_hot = sum(1 for v in vals if v >= threshold)
    n = len(vals)
    need = max(1, (n + 1) // 2)  # ceil half
    if decision == "max":
        chat_present = bool(mx >= threshold)
    else:
        # majority: ≥ half frames hot (default v1.1)
        chat_present = bool(n_hot >= need)
        decision = "majority"
    return {
        "schema": "gcs_chat_detect/v1.1",
        "src": str(src),
        "threshold": threshold,
        "decision": decision,
        "frames_hot": n_hot,
        "frames_need": need,
        "chat_score_avg": round(avg, 4),
        "chat_score_max": round(mx, 4),
        "chat_present": chat_present,
        "frames": scores,
        "roi_frac": {
            "x0": ROI_X0,
            "x1": ROI_X1,
            "y0": ROI_Y0,
            "y1": ROI_Y1,
        },
        "policy": "blur_only_if_chat_present_or_force",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--threshold", type=float, default=0.45)
    ap.add_argument(
        "--decision",
        choices=("majority", "max"),
        default="majority",
        help="majority (default v1.1) or legacy max",
    )
    args = ap.parse_args()
    d = detect(args.src, args.threshold, args.decision)
    text = json.dumps(d, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
