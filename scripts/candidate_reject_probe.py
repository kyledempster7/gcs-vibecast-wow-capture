#!/usr/bin/env python3
"""Score ship candidates: blackdetect + tiny-file reject. Human verdicts win.

Usage:
  python3 candidate_reject_probe.py --dir ~/Movies/.../candidates [--human feedback.json]
Writes REJECT_PROBE.json next to candidates (or --out).
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


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            FP,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out or "0")


def blackdetect(path: Path) -> list[dict]:
    r = subprocess.run(
        [
            FF,
            "-hide_banner",
            "-i",
            str(path),
            "-vf",
            "blackdetect=d=0.5:pix_th=0.10",
            "-an",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    blacks = []
    for line in (r.stderr or "").splitlines():
        if "black_start" not in line:
            continue
        bs = re.search(r"black_start:([0-9.]+)", line)
        be = re.search(r"black_end:([0-9.]+)", line)
        bd = re.search(r"black_duration:([0-9.]+)", line)
        if bs and be and bd:
            blacks.append(
                {
                    "start": float(bs.group(1)),
                    "end": float(be.group(1)),
                    "duration": float(bd.group(1)),
                }
            )
    return blacks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--human", type=Path, default=None, help="JSON map id→{verdict,reason}")
    args = ap.parse_args()
    human = {}
    if args.human and args.human.is_file():
        human = json.loads(args.human.read_text(encoding="utf-8"))

    rows = []
    for p in sorted(args.dir.glob("*.mp4")):
        dur = probe_duration(p)
        blacks = blackdetect(p)
        black_total = sum(b["duration"] for b in blacks)
        black_frac = (black_total / dur) if dur > 0 else 0.0
        auto = "REVIEW"
        if black_frac >= 0.40:
            auto = "REJECT_AUTO_BLACK"
        elif p.stat().st_size < 8_000_000 and dur >= 20:
            auto = "REJECT_AUTO_TINY"
        elif black_frac >= 0.15:
            auto = "WARN_BLACK"

        m = re.search(r"db-\d{8}-([a-z0-9]+)-", p.name)
        cid = m.group(1) if m else p.stem
        hum = human.get(cid) or human.get(cid[0] if cid else "")
        final = auto
        reason = auto
        if hum:
            final = hum.get("verdict", final)
            reason = hum.get("reason", reason)
        elif auto.startswith("REJECT"):
            final = "REJECT"
        elif auto.startswith("WARN"):
            final = "REVIEW"

        rows.append(
            {
                "id": cid,
                "filename": p.name,
                "bytes": p.stat().st_size,
                "duration_sec": round(dur, 3),
                "black_segments": blacks,
                "black_total_sec": round(black_total, 3),
                "black_frac": round(black_frac, 3),
                "auto_verdict": auto,
                "human": hum,
                "final_verdict": final,
                "final_reason": reason,
            }
        )

    report = {
        "schema": "gcs_candidate_reject_probe/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dir": str(args.dir),
        "candidates": rows,
        "keep": [r["id"] for r in rows if str(r["final_verdict"]).upper() == "KEEP"],
        "reject": [r["id"] for r in rows if str(r["final_verdict"]).upper() == "REJECT"],
        "review_open": [
            r["id"]
            for r in rows
            if str(r["final_verdict"]).upper() not in ("KEEP", "REJECT")
        ],
    }
    out = args.out or (args.dir.parent / "analysis" / "REJECT_PROBE.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "keep": report["keep"], "reject": report["reject"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
