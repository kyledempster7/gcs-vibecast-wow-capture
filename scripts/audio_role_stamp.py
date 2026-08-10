#!/usr/bin/env python3
"""Stamp audio role for a returner day: mic_cue vs talk_product vs dual_stem.

Kyle 2026-08-10: mic is present and useful as AI cue; most nights = B-roll bed.
Never invent stems. No publish.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def probe_audio(path: Path) -> list[dict]:
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index,codec_name,channels,sample_rate",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        return []
    try:
        data = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        return []
    return data.get("streams") or []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    args = ap.parse_args()
    day = args.day_dir
    cand = day / "candidates"
    analysis = day / "analysis"
    analysis.mkdir(parents=True, exist_ok=True)

    samples = []
    if cand.is_dir():
        for p in sorted(cand.glob("*.mp4"))[:8]:
            streams = probe_audio(p)
            samples.append(
                {
                    "file": p.name,
                    "audio_streams": len(streams),
                    "streams": streams,
                }
            )

    speech_p = analysis / "SPEECH_PEAKS.json"
    speech_status = None
    if speech_p.is_file():
        speech_status = json.loads(speech_p.read_text(encoding="utf-8")).get("status")

    n_audio = sum(1 for s in samples if s["audio_streams"] > 0)
    # dual stem would be 2+ discrete tracks with different roles — we only see mixed aac usually
    multi_track = any(s["audio_streams"] >= 2 for s in samples)

    if speech_status == "OK":
        night_role = "talk_product_candidate"
        mic_role = "mic_vo_or_cue"
    elif n_audio > 0:
        night_role = "broll_bed_with_mic_cue"
        mic_role = "mic_cue_for_ai"
    else:
        night_role = "silent_or_missing_audio"
        mic_role = "none"

    report = {
        "schema": "gcs_audio_role/v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "day_dir": str(day),
        "night_role": night_role,
        "mic_role": mic_role,
        "speech_peaks_status": speech_status,
        "samples_with_audio": n_audio,
        "multi_track_seen": multi_track,
        "samples": samples,
        "kyle_20260810": {
            "mic_present_useful_as_ai_cue": True,
            "default_product": "background_broll_not_forced_vo",
            "game_desktop_still_open": True,
        },
        "law": "no_invent_stems_no_publish",
    }
    out = analysis / "AUDIO_ROLE.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"audio_role {night_role} mic={mic_role} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
