#!/usr/bin/env python3
"""Probe zone/location text from frames (TitanPanel top strip + optional BR).

Never invent zone names. Empty OCR = honest UNKNOWN.
Uses macOS Vision via zone_label_ocr.swift when available.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

FF = "ffmpeg"
SWIFT_HELPER = Path(__file__).resolve().parent / "zone_label_ocr.swift"

# Loose zone-ish tokens (not a claim of presence)
ZONEISH = re.compile(
    r"\b(Dragonblight|Howling\s+Fjord|Borean\s+Tundra|Grizzly\s+Hills|"
    r"Zul.?Drak|Sholazar|Icecrown|Storm\s+Peaks|Wintergrasp|"
    r"Orgrimmar|Stormwind|Dalaran|Valdrakken|Oribos|Bastion|"
    r"Maldraxxus|Ardenweald|Revendreth|The\s+Maw|Shadowlands|"
    r"Tirisfal|Undercity|Silvermoon|Thunder\s+Bluff)\b",
    re.I,
)


def grab_frame(src: Path, dest: Path, t: float = 2.0) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [FF, "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", str(dest)],
        capture_output=True,
        text=True,
        check=False,
    )
    return r.returncode == 0 and dest.is_file() and dest.stat().st_size > 500


def crop_roi(src: Path, dest: Path, kind: str) -> bool:
    """kind: titan_top | br_label | full"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if kind == "full":
        if dest != src:
            dest.write_bytes(src.read_bytes())
        return dest.is_file()
    # fractions of frame — Titan often top ~6%; BR zone label often bottom-right ~18%x12%
    if kind == "titan_top":
        vf = "crop=iw:ih*0.08:0:0"
    else:  # br_label
        vf = "crop=iw*0.28:ih*0.14:iw*0.70:ih*0.82"
    r = subprocess.run(
        [FF, "-y", "-i", str(src), "-vf", vf, str(dest)],
        capture_output=True,
        text=True,
        check=False,
    )
    return r.returncode == 0 and dest.is_file()


def ocr_image(path: Path) -> list[str]:
    if not SWIFT_HELPER.is_file():
        return []
    r = subprocess.run(
        ["swift", str(SWIFT_HELPER), str(path)],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if r.returncode != 0:
        return []
    lines = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
    return lines


TITAN_CHROME = re.compile(
    r"(XP/hr|Time To Level|Durability|Loot Specialization|Specialization:|Mail:)",
    re.I,
)


def extract_zone(lines: list[str]) -> dict:
    joined = " | ".join(lines)
    titan_chrome = bool(TITAN_CHROME.search(joined))
    m = ZONEISH.search(joined)
    if m:
        return {
            "zone_hint": m.group(0),
            "confidence": 0.7,
            "matched_from": "token_list",
            "titan_chrome_present": titan_chrome,
            "raw_lines": lines[:20],
        }
    # no known token — do not invent; expose raw for human/agent
    note = "OCR text present but no known zone token — do not invent"
    if titan_chrome:
        note = (
            "Titan-like chrome OCR (XP/durability/loot) without zone string — "
            "enable location module on Titan or wider crop next night"
        )
    return {
        "zone_hint": None,
        "confidence": 0.0,
        "matched_from": None,
        "titan_chrome_present": titan_chrome,
        "raw_lines": lines[:20],
        "note": note,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    ap.add_argument("--video", type=Path, default=None, help="optional single mp4")
    ap.add_argument("--t", type=float, default=3.0)
    args = ap.parse_args()
    day = args.day_dir
    analysis = day / "analysis"
    frames = analysis / "frames" / "zone_probe"
    frames.mkdir(parents=True, exist_ok=True)

    videos: list[Path] = []
    if args.video and args.video.is_file():
        videos = [args.video]
    else:
        cand = day / "candidates"
        pride = cand / "pride"
        for p in sorted(pride.glob("*.mp4")) if pride.is_dir() else []:
            videos.append(p)
        for p in sorted(cand.glob("wow-*.mp4"))[:3]:
            videos.append(p)
        if not videos:
            for p in sorted(cand.glob("*.mp4"))[:3]:
                videos.append(p)

    results = []
    for vid in videos:
        base = frames / vid.stem
        full = Path(str(base) + "-full.jpg")
        if not grab_frame(vid, full, args.t):
            results.append({"video": vid.name, "status": "FRAME_FAIL"})
            continue
        entry = {"video": vid.name, "frame": str(full), "rois": {}}
        for kind in ("titan_top", "br_label", "full"):
            roi_path = Path(str(base) + f"-{kind}.jpg")
            if not crop_roi(full, roi_path, kind):
                entry["rois"][kind] = {"status": "CROP_FAIL"}
                continue
            lines = ocr_image(roi_path)
            z = extract_zone(lines)
            entry["rois"][kind] = {
                "status": "OK" if lines else "EMPTY_OCR",
                "path": str(roi_path),
                **z,
            }
        # pick best zone_hint
        best = None
        titan_seen = False
        for kind in ("titan_top", "br_label", "full"):
            r = entry["rois"].get(kind) or {}
            if r.get("titan_chrome_present"):
                titan_seen = True
            if r.get("zone_hint") and not best:
                best = {"source_roi": kind, **r}
        entry["zone_hint"] = (best or {}).get("zone_hint")
        entry["best"] = best
        entry["titan_chrome_present"] = titan_seen
        if entry["zone_hint"]:
            entry["status"] = "ZONE"
        elif titan_seen:
            entry["status"] = "TITAN_CHROME_NO_ZONE"
        else:
            entry["status"] = "NO_ZONE_TOKEN"
        results.append(entry)

    report = {
        "schema": "gcs_zone_label_probe/v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "day_dir": str(day),
        "law": "no_invent_zone_titan_when_visible",
        "kyle_signal_20260810": "TitanPanel location readable when bar up",
        "clips": results,
    }
    out = analysis / "ZONE_LABEL.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    zones = [r.get("zone_hint") for r in results if r.get("zone_hint")]
    print(f"zone_label_probe clips={len(results)} zones_found={zones} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
