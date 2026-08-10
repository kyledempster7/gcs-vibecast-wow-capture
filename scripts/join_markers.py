#!/usr/bin/env python3
"""Join SESSION.jsonl markers → cut windows (seconds into file).

Needs record_start_utc either as first marker type or --record-start.
Never publishes. Empty markers → empty windows + honest report.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_ts(s: str) -> datetime:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--markers", type=Path, required=True, help="SESSION.jsonl")
    ap.add_argument("--record-start", default="", help="ISO UTC if not in file")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--talk-pad", type=float, default=15.0)
    ap.add_argument("--skip-pad", type=float, default=5.0)
    args = ap.parse_args()

    events = load_jsonl(args.markers)
    windows: list[dict] = []
    skip_zones: list[dict] = []
    chapter_by_master: dict[str, list] = {}
    open_broll = None
    open_rotate = None
    weak_start = False
    record_start = None

    if not events:
        report = {
            "schema": "gcs_marker_join/v0",
            "status": "EMPTY_MARKERS",
            "markers_path": str(args.markers),
            "windows": [],
            "note": "No SESSION.jsonl events — cut on auto-score only",
        }
        out = args.out or args.markers.with_suffix(".join.json")
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0

    # OBS embedded chapters (press evidence only — not visual claims)
    for e in events:
        if e.get("schema") != "local_embedded_chapter_extract/v1":
            continue
        master = e.get("source_master") or "?"
        t = float(e.get("time_seconds") or 0)
        chapter_by_master.setdefault(master, []).append({
            "kind": "obs_chapter",
            "title": e.get("title"),
            "start_sec": round(max(0.0, t - 2), 3),
            "end_sec": round(t + 15, 3),
            "press_evidence_only": e.get("press_evidence_only", True),
        })

    deck_events = [
        e for e in events
        if e.get("schema") == "gcs_obs_marker/v1" or e.get("button_id")
    ]

    if args.record_start:
        record_start = parse_ts(args.record_start)
    for e in deck_events:
        if e.get("button_id") in ("layer_c.record_start", "record_start") or e.get("kind") == "record_start":
            record_start = parse_ts(e["ts_utc"])
            break
        if e.get("recording") is True and e.get("is_record_start"):
            record_start = parse_ts(e["ts_utc"])
            break

    if deck_events and record_start is None and "ts_utc" in deck_events[0]:
        record_start = parse_ts(deck_events[0]["ts_utc"])
        weak_start = True

    def t_sec(e: dict) -> float:
        assert record_start is not None
        return (parse_ts(e["ts_utc"]) - record_start).total_seconds()

    if record_start is not None:
        for e in deck_events:
            if not e.get("recording", True):
                continue
            if "ts_utc" not in e:
                continue
            bid = e.get("button_id", "")
            st = e.get("state", "pulse")
            t = t_sec(e)
            if bid == "layer_c.broll_enter" and st == "begin":
                open_broll = t
            elif bid == "layer_c.broll_exit" and st == "end" and open_broll is not None:
                windows.append({
                    "kind": "broll",
                    "start_sec": round(open_broll, 3),
                    "end_sec": round(t, 3),
                })
                open_broll = None
            elif bid == "layer_c.rotate_begin" and st == "begin":
                open_rotate = t
            elif bid == "layer_c.rotate_end" and st == "end" and open_rotate is not None:
                windows.append({
                    "kind": "rotate",
                    "start_sec": round(open_rotate, 3),
                    "end_sec": round(t, 3),
                })
                open_rotate = None
            elif bid == "layer_c.talk_peak":
                windows.append({
                    "kind": "talk_peak",
                    "start_sec": round(max(0.0, t - args.talk_pad), 3),
                    "end_sec": round(t + args.talk_pad, 3),
                })
            elif bid == "layer_c.skip_zone":
                skip_zones.append({
                    "start_sec": round(max(0.0, t - args.skip_pad), 3),
                    "end_sec": round(t + args.skip_pad, 3),
                })
            elif bid == "layer_c.record_mark":
                windows.append({
                    "kind": "chapter",
                    "start_sec": round(max(0.0, t - 2), 3),
                    "end_sec": round(t + 2, 3),
                })
            elif bid in ("layer_c.gather_ui_on", "WOWCAP.GATHER_UI_ON") and st in ("begin", "pulse"):
                open_broll = t  # gather window shares b-roll prefer semantics
                windows.append({
                    "kind": "gather_ui_on",
                    "start_sec": round(t, 3),
                    "end_sec": round(t + 0.1, 3),
                    "event": "WOWCAP.GATHER_UI_ON",
                })
            elif bid in ("layer_c.gather_ui_off", "WOWCAP.GATHER_UI_OFF") and st in ("end", "pulse"):
                if open_broll is not None:
                    windows.append({
                        "kind": "gather_broll",
                        "start_sec": round(open_broll, 3),
                        "end_sec": round(t, 3),
                        "event": "WOWCAP.GATHER_UI_OFF",
                    })
                    open_broll = None
                else:
                    windows.append({
                        "kind": "gather_ui_off",
                        "start_sec": round(t, 3),
                        "end_sec": round(t + 0.1, 3),
                        "event": "WOWCAP.GATHER_UI_OFF",
                    })

    report = {
        "schema": "gcs_marker_join/v0",
        "status": "OK" if (windows or chapter_by_master) else "NO_WINDOWS",
        "markers_path": str(args.markers),
        "record_start_utc": (
            record_start.astimezone(timezone.utc).isoformat() if record_start else None
        ),
        "record_start_weak": weak_start,
        "event_count": len(events),
        "deck_event_count": len(deck_events),
        "windows": windows,
        "skip_zones": skip_zones,
        "obs_chapters_by_master": chapter_by_master,
        "law": "prefer_export_inside_windows_skip_skip_zones; obs_chapters=press_evidence_only",
    }
    out = args.out or args.markers.with_suffix(".join.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "windows": len(windows), "skips": len(skip_zones)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
