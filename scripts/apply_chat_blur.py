#!/usr/bin/env python3
"""Bottom-left chat safety blur — ONLY if chat_present or --force.

Never always-on. See MACHINE_INTELLIGENCE_BROLL.md.
Failed lesson: orbit-chatblur-v0 blurred empty ground.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

FF = "ffmpeg"
# import sibling
sys.path.insert(0, str(Path(__file__).resolve().parent))
from detect_chat_presence import detect  # noqa: E402


def blur(src: Path, out: Path, w_frac: float, h_frac: float, x_frac: float, y_frac: float) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    fc = (
        f"[0:v]split=2[base][tmp];"
        f"[tmp]crop=iw*{w_frac}:ih*{h_frac}:iw*{x_frac}:ih*{y_frac},"
        f"boxblur=18:8[blurred];"
        f"[base][blurred]overlay=W*{x_frac}:H*{y_frac}"
    )
    r = subprocess.run(
        [
            FF,
            "-y",
            "-i",
            str(src),
            "-filter_complex",
            fc,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--force", action="store_true", help="blur even if detector says no chat")
    ap.add_argument("--threshold", type=float, default=0.45)
    ap.add_argument("--detect-out", type=Path, default=None)
    ap.add_argument("--w-frac", type=float, default=0.26)
    ap.add_argument("--h-frac", type=float, default=0.36)
    ap.add_argument("--x-frac", type=float, default=0.015)
    ap.add_argument("--y-frac", type=float, default=0.58)
    args = ap.parse_args()

    det = detect(args.src, args.threshold)
    if args.detect_out:
        args.detect_out.parent.mkdir(parents=True, exist_ok=True)
        args.detect_out.write_text(json.dumps(det, indent=2), encoding="utf-8")

    if not det["chat_present"] and not args.force:
        # pass-through copy — no redundant blur
        args.out.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(
            ["cp", str(args.src), str(args.out)],
            capture_output=True,
            text=True,
        )
        print(
            json.dumps(
                {
                    "action": "passthrough_no_blur",
                    "reason": "chat_present=false",
                    "chat_score_max": det["chat_score_max"],
                    "out": str(args.out),
                    "rc": r.returncode,
                },
                indent=2,
            )
        )
        return r.returncode

    rc = blur(args.src, args.out, args.w_frac, args.h_frac, args.x_frac, args.y_frac)
    print(
        json.dumps(
            {
                "action": "blur_applied",
                "reason": "force" if args.force else "chat_present=true",
                "chat_score_max": det["chat_score_max"],
                "out": str(args.out),
                "rc": rc,
            },
            indent=2,
        )
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
