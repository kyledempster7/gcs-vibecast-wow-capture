#!/usr/bin/env python3
"""Talk-night speech peaks from existing transcript / whisper.

Skip honestly when ambience-only. Never invent VO. No publish.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def load_srt_segments(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\n\s*\n", text.strip())
    segs = []
    for b in blocks:
        lines = [ln.strip() for ln in b.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        # find time line
        tline = next((ln for ln in lines if "-->" in ln), None)
        if not tline:
            continue
        m = re.match(
            r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})",
            tline,
        )
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        body = " ".join(ln for ln in lines if ln != tline and not ln.isdigit())
        segs.append({"start": start, "end": end, "text": body})
    return segs


def load_json_segments(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    # mlx_whisper / openai whisper json shapes
    segs = []
    for s in data.get("segments") or []:
        segs.append(
            {
                "start": float(s.get("start") or 0),
                "end": float(s.get("end") or 0),
                "text": (s.get("text") or "").strip(),
            }
        )
    if not segs and data.get("text"):
        segs.append({"start": 0.0, "end": 0.0, "text": str(data["text"]).strip()})
    return segs


def meaningful(text: str) -> bool:
    t = re.sub(r"[^\w\s']", "", text.lower()).strip()
    if len(t) < 4:
        return False
    # single filler tokens
    if t in {"you", "yeah", "uh", "um", "oh", "ah", "mm", "hmm", "okay", "ok"}:
        return False
    words = t.split()
    if len(words) == 1 and len(words[0]) < 5:
        return False
    return True


def cluster_peaks(segs: list[dict], pad: float = 2.0, merge_gap: float = 3.0) -> list[dict]:
    good = [s for s in segs if meaningful(s.get("text") or "")]
    if not good:
        return []
    good.sort(key=lambda s: s["start"])
    clusters: list[dict] = []
    cur = {
        "start": max(0.0, good[0]["start"] - pad),
        "end": good[0]["end"] + pad,
        "texts": [good[0]["text"]],
    }
    for s in good[1:]:
        if s["start"] <= cur["end"] + merge_gap:
            cur["end"] = max(cur["end"], s["end"] + pad)
            cur["texts"].append(s["text"])
        else:
            clusters.append(cur)
            cur = {
                "start": max(0.0, s["start"] - pad),
                "end": s["end"] + pad,
                "texts": [s["text"]],
            }
    clusters.append(cur)
    peaks = []
    for i, c in enumerate(clusters, 1):
        joined = " ".join(c["texts"]).strip()
        peaks.append(
            {
                "id": f"speech-{i:02d}",
                "start_sec": round(c["start"], 3),
                "end_sec": round(c["end"], 3),
                "duration_sec": round(c["end"] - c["start"], 3),
                "text_preview": joined[:160],
                "wordish_count": len(joined.split()),
                "role": "talk_peak_seed",
            }
        )
    return peaks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    ap.add_argument("--force", action="store_true", help="rank even weak text")
    args = ap.parse_args()
    day = args.day_dir
    analysis = day / "analysis"
    analysis.mkdir(parents=True, exist_ok=True)
    out = analysis / "SPEECH_PEAKS.json"

    transcript_note = analysis / "TRANSCRIPT_NOTE.md"
    segs: list[dict] = []
    source = None
    # prefer srt then json under transcripts/
    tdir = analysis / "transcripts"
    if tdir.is_dir():
        for srt in sorted(tdir.glob("*.srt")):
            segs = load_srt_segments(srt)
            source = str(srt)
            break
        if not segs:
            for jp in sorted(tdir.glob("*.json")):
                segs = load_json_segments(jp)
                source = str(jp)
                break

    note_text = transcript_note.read_text(encoding="utf-8") if transcript_note.is_file() else ""
    ambience_hint = any(
        x in note_text.lower()
        for x in ("ambience", "near-empty", "little vo", "not a talk")
    )

    peaks = cluster_peaks(segs) if segs else []
    if not args.force and (ambience_hint or not peaks):
        report = {
            "schema": "gcs_speech_peaks/v0",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "day_dir": str(day),
            "status": "SKIP_AMBIENCE_OR_EMPTY",
            "source": source,
            "segment_count": len(segs),
            "peaks": [],
            "shortlist": [],
            "note": "No meaningful speech peaks — treat as ambience/game SFX; use motion KEEP.",
            "law": "no_invent_vo_no_publish",
        }
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"speech_peaks SKIP -> {out}")
        return 0

    shortlist = sorted(peaks, key=lambda p: -p["wordish_count"])[:5]
    report = {
        "schema": "gcs_speech_peaks/v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "day_dir": str(day),
        "status": "OK",
        "source": source,
        "segment_count": len(segs),
        "peaks": peaks,
        "shortlist": shortlist,
        "law": "vo_nights_only_no_publish",
    }
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"speech_peaks peaks={len(peaks)} shortlist={len(shortlist)} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
