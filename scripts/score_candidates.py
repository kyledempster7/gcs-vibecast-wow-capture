#!/usr/bin/env python3
"""Score Returner Daily ship candidates (Mac). Human verdicts win.

Signals: duration, bytes/s (tiny=load), blackdetect, low-motion via freezedetect.
Never publishes.
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
        [FP, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        text=True,
    ).strip()
    return float(out or "0")


def blackdetect(path: Path) -> list[dict]:
    r = subprocess.run(
        [FF, "-hide_banner", "-i", str(path),
         "-vf", "blackdetect=d=0.5:pix_th=0.12", "-an", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    blacks = []
    for line in (r.stderr or "").splitlines():
        if "black_start" not in line:
            continue
        bs = re.search(r"black_start:([0-9.]+)", line)
        be = re.search(r"black_end:([0-9.]+)", line)
        bd = re.search(r"black_duration:([0-9.]+)", line)
        if bs and be and bd:
            blacks.append({
                "start": float(bs.group(1)),
                "end": float(be.group(1)),
                "duration": float(bd.group(1)),
            })
    return blacks


def freezedetect_score(path: Path) -> float:
    """Return fraction of duration covered by freeze segments (0–1-ish)."""
    r = subprocess.run(
        [FF, "-hide_banner", "-i", str(path),
         "-vf", "freezedetect=n=0.003:d=0.8", "-an", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    total = 0.0
    starts = []
    ends = []
    for line in (r.stderr or "").splitlines():
        m = re.search(r"freeze_start:\s*([0-9.]+)", line)
        if m:
            starts.append(float(m.group(1)))
        m = re.search(r"freeze_end:\s*([0-9.]+)", line)
        if m:
            ends.append(float(m.group(1)))
        m = re.search(r"freeze_duration:\s*([0-9.]+)", line)
        if m:
            total += float(m.group(1))
    return total


def motion_window_scores(path: Path, window: float = 15.0, step: float = 5.0) -> list[dict]:
    """Sample short windows; higher select=scene score ≈ more change."""
    dur = duration(path)
    rows = []
    t = 0.0
    while t + window <= dur + 0.01:
        # scene score over window via select=gt(scene\,0.02) count
        r = subprocess.run(
            [FF, "-hide_banner", "-ss", str(t), "-t", str(window), "-i", str(path),
             "-vf", r"select='gt(scene,0.015)',showinfo", "-an", "-f", "null", "-"],
            capture_output=True, text=True,
        )
        hits = sum(1 for ln in (r.stderr or "").splitlines() if "pts_time" in ln and "showinfo" in ln)
        # also freeze in window
        r2 = subprocess.run(
            [FF, "-hide_banner", "-ss", str(t), "-t", str(window), "-i", str(path),
             "-vf", "freezedetect=n=0.003:d=0.5", "-an", "-f", "null", "-"],
            capture_output=True, text=True,
        )
        freeze = 0.0
        for line in (r2.stderr or "").splitlines():
            m = re.search(r"freeze_duration:\s*([0-9.]+)", line)
            if m:
                freeze += float(m.group(1))
        score = hits - freeze * 2
        rows.append({"start": round(t, 2), "window": window, "scene_hits": hits,
                     "freeze_sec": round(freeze, 2), "score": round(score, 2)})
        t += step
    return rows


def cid_from_name(name: str) -> str:
    m = re.search(r"db-\d{8}-([a-z0-9]+)-", name)
    return m.group(1) if m else Path(name).stem


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--human", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--motion-for", default="", help="comma ids to deep-score motion windows")
    args = ap.parse_args()

    human = {}
    if args.human and args.human.is_file():
        human = json.loads(args.human.read_text(encoding="utf-8"))

    motion_ids = {x.strip() for x in args.motion_for.split(",") if x.strip()}
    rows = []
    for p in sorted(args.dir.glob("*.mp4")):
        cid = cid_from_name(p.name)
        # map a/b/c/d keys
        hkey = cid if cid in human else (cid[0] if cid and cid[0] in human else None)
        dur = duration(p)
        size = p.stat().st_size
        bps = size / dur if dur > 0 else 0
        blacks = blackdetect(p)
        black_total = sum(b["duration"] for b in blacks)
        black_frac = black_total / dur if dur else 0
        freeze_total = freezedetect_score(p)
        freeze_frac = freeze_total / dur if dur else 0

        auto = "AUTO_REVIEW"
        reasons = []
        if size < 8_000_000 and dur >= 15:
            auto = "AUTO_REJECT"
            reasons.append("tiny_file_likely_load")
        if bps < 400_000 and dur >= 15:  # < ~0.4 MB/s
            auto = "AUTO_REJECT"
            reasons.append("low_bitrate")
        if black_frac >= 0.35:
            auto = "AUTO_REJECT"
            reasons.append("high_black")
        if freeze_frac >= 0.55:
            auto = "AUTO_REJECT"
            reasons.append("mostly_frozen")
        elif freeze_frac >= 0.35:
            reasons.append("warn_freeze")
            if auto == "AUTO_REVIEW":
                auto = "AUTO_REVIEW"

        hum = human.get(hkey) if hkey else None
        final = auto
        reason = ",".join(reasons) or auto
        if hum:
            final = hum.get("verdict", final)
            reason = hum.get("reason", reason)

        row = {
            "id": hkey or cid,
            "filename": p.name,
            "path": str(p),
            "bytes": size,
            "duration_sec": round(dur, 3),
            "bytes_per_sec": int(bps),
            "black_frac": round(black_frac, 3),
            "freeze_frac": round(min(freeze_frac, 1.5), 3),
            "black_segments": blacks,
            "auto_verdict": auto,
            "auto_reasons": reasons,
            "human": hum,
            "final_verdict": final,
            "final_reason": reason,
        }
        if (hkey or cid) in motion_ids or (hum and hum.get("verdict") == "KEEP"):
            row["motion_windows"] = motion_window_scores(p, window=15.0, step=5.0)
            if row["motion_windows"]:
                best = max(row["motion_windows"], key=lambda x: x["score"])
                row["best_15s"] = best
        rows.append(row)
        print(f"{row['id']}\t{row['final_verdict']}\t{auto}\tbps={row['bytes_per_sec']}\tfreeze={row['freeze_frac']}\t{p.name[:36]}")

    keep, reject, eyes = [], [], []
    for r in rows:
        v = str(r["final_verdict"]).upper()
        if v == "KEEP":
            keep.append(r["id"])
            eyes.append(r["id"])
        elif v in ("REJECT", "AUTO_REJECT"):
            reject.append(r["id"])
        else:
            # OPEN / REVIEW — include if auto still thinks worth eyes
            if r["auto_verdict"] != "AUTO_REJECT":
                eyes.append(r["id"])
            else:
                reject.append(r["id"])

    report = {
        "schema": "gcs_candidate_score/v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dir": str(args.dir),
        "candidates": rows,
        "keep": keep,
        "reject": reject,
        "eyes_on": eyes,
    }

    out = args.out or (args.dir.parent / "analysis" / "REJECT_PROBE.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "keep": keep, "reject": reject, "eyes_on": eyes}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
