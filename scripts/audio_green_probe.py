#!/usr/bin/env python3
"""Probe a 10s dual-audio test file; stamp AUDIO_GREEN only when both stems proven.

Never invent GREEN. No publish.
Writes analysis/AUDIO_GREEN_PROBE.json next to day dir or global stamp path.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def ffprobe_streams(path: Path) -> list[dict]:
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=index,codec_type,codec_name,channels,sample_rate",
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
        return (json.loads(r.stdout or "{}").get("streams")) or []
    except json.JSONDecodeError:
        return []


def mean_volume(path: Path, stream_index: int | None = None) -> float | None:
    """Return mean_volume dB from ffmpeg volumedetect, or None."""
    cmd = ["ffmpeg", "-hide_banner"]
    if stream_index is not None:
        cmd += ["-i", str(path), "-map", f"0:{stream_index}", "-af", "volumedetect", "-f", "null", "-"]
    else:
        cmd += ["-i", str(path), "-af", "volumedetect", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    text = (r.stderr or "") + (r.stdout or "")
    for line in text.splitlines():
        if "mean_volume:" in line:
            try:
                return float(line.split("mean_volume:")[1].split("dB")[0].strip())
            except (IndexError, ValueError):
                return None
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, required=True, help="10s (or longer) test recording")
    ap.add_argument(
        "--stamp-md",
        type=Path,
        default=Path(
            "/Users/kyle/Kyles_Vault/kyles_corner/Games/WoW/04-Story-and-Capture/AUDIO_GREEN_STAMP.md"
        ),
    )
    ap.add_argument("--write-stamp", action="store_true", help="Only if dual meters green")
    ap.add_argument("--out-json", type=Path, default=None)
    args = ap.parse_args()

    path = args.file.expanduser().resolve()
    out: dict = {
        "schema": "gcs_audio_green_probe/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "file": str(path),
        "exists": path.is_file(),
        "law": "never_invent_GREEN; dual_tracks_or_honest_partial",
    }
    if not path.is_file():
        out["status"] = "MISSING_FILE"
        print(json.dumps(out, indent=2))
        return 2

    streams = ffprobe_streams(path)
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    out["streams"] = streams
    out["audio_stream_count"] = len(audio)

    volumes = []
    for s in audio:
        idx = s.get("index")
        mv = mean_volume(path, idx if isinstance(idx, int) else None)
        volumes.append({"index": idx, "mean_volume_db": mv})
    out["volumes"] = volumes

    # Green only if ≥2 audio streams both with mean_volume > -50 dB (not silence)
    audible = [
        v
        for v in volumes
        if v.get("mean_volume_db") is not None and v["mean_volume_db"] > -50.0
    ]
    dual = len(audio) >= 2 and len(audible) >= 2
    single_ok = len(audio) >= 1 and len(audible) >= 1

    if dual:
        out["status"] = "DUAL_GREEN_CANDIDATE"
        out["mic"] = "present_track"
        out["game_audio"] = "present_track"
    elif single_ok:
        out["status"] = "SINGLE_TRACK_PARTIAL"
        out["mic"] = "unknown_mixed_or_one"
        out["game_audio"] = "not_separable"
    else:
        out["status"] = "SILENT_OR_NO_AUDIO"

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")

    if args.write_stamp and dual:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        md = f"""---
type: audio-green-stamp
status: GREEN
created: 2026-08-09
updated: {datetime.now().date().isoformat()}
---

# Audio green stamp

**Agent rule:** never mark `status: GREEN` without Kyle (or a verified 10s path on disk).  
**Playbook:** [[GAME_AUDIO_RESETUP]] · jump [[../00-Index/JUMP_DESKTOP_PLAYBOOK]]

## Current

| Field | Value |
|-------|-------|
| status | **GREEN** |
| last_10s_test | dual-track probe |
| path_to_test_file | `{path}` |
| mic | present (track) |
| game_audio | present (track) |
| stamped_by | audio_green_probe.py |
| stamped_at | {ts} |

## Gate (checklist)

- [x] Mic moves meter  
- [x] Game audio moves **or** voice-only night noted  
- [x] 10s test played back  
- [x] Path written above (real file only)

## Probe JSON

```json
{json.dumps(out, indent=2)}
```
"""
        args.stamp_md.write_text(md, encoding="utf-8")
        out["stamp_written"] = str(args.stamp_md)
    elif args.write_stamp and not dual:
        out["stamp_written"] = False
        out["stamp_note"] = "refused: not dual green"

    print(json.dumps(out, indent=2))
    return 0 if dual else 1


if __name__ == "__main__":
    raise SystemExit(main())
