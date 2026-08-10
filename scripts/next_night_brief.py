#!/usr/bin/env python3
"""Build NEXT_NIGHT_BRIEF.md from last day tags + KEEP. No publish."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    day = args.day_dir
    analysis = day / "analysis"
    motion_p = analysis / "MOTION_TAGS.json"
    hv_p = analysis / "human_verdicts.json"
    speech_p = analysis / "SPEECH_PEAKS.json"
    short_p = day / "review-pack" / "SHORTLIST.md"
    vert_p = day / "candidates" / "pride" / "vertical" / "VERTICAL.json"

    shots = Counter()
    if motion_p.is_file():
        data = json.loads(motion_p.read_text(encoding="utf-8"))
        for c in data.get("clips") or []:
            shots[c.get("shot") or "unknown"] += 1

    keeps = []
    if hv_p.is_file():
        hv = json.loads(hv_p.read_text(encoding="utf-8"))
        for k, v in hv.items():
            if str(v.get("verdict", "")).upper() == "KEEP":
                keeps.append(k)

    speech_status = "n/a"
    if speech_p.is_file():
        speech_status = json.loads(speech_p.read_text(encoding="utf-8")).get("status", "?")

    audio_role = "n/a"
    ar_p = analysis / "AUDIO_ROLE.json"
    if ar_p.is_file():
        audio_role = json.loads(ar_p.read_text(encoding="utf-8")).get("night_role", "?")

    zone_hints: list[str] = []
    zl_p = analysis / "ZONE_LABEL.json"
    if zl_p.is_file():
        for c in json.loads(zl_p.read_text(encoding="utf-8")).get("clips") or []:
            if c.get("zone_hint"):
                zone_hints.append(str(c["zone_hint"]))

    vertical_n = 0
    if vert_p.is_file():
        vertical_n = sum(
            1
            for c in json.loads(vert_p.read_text(encoding="utf-8")).get("clips") or []
            if c.get("status") in ("OK", "EXISTS")
        )

    chat_true = 0
    chat_false = 0
    if analysis.is_dir():
        for p in analysis.glob("chat_detect_*.json"):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if d.get("chat_present") is True:
                chat_true += 1
            elif d.get("chat_present") is False:
                chat_false += 1

    lines = [
        f"# Next night brief — from `{day.name}`",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Shot mix last harvest",
        "",
    ]
    if shots:
        for k, v in shots.most_common():
            lines.append(f"- **{k}**: {v}")
    else:
        lines.append("- _(no MOTION_TAGS)_")
    lines += [
        "",
        "## Human KEEP ids",
        "",
        (", ".join(f"`{k}`" for k in keeps) if keeps else "- _(none logged)_"),
        "",
        "## Machine signals",
        "",
        f"- Speech peaks: `{speech_status}`",
        f"- Audio night role: `{audio_role}` (mic = AI cue by default)",
        f"- Zone OCR hints: {', '.join(f'`{z}`' for z in zone_hints) if zone_hints else '_(none — Titan off or OCR empty)_'}",
        f"- Pride vertical ready: **{vertical_n}**",
        f"- Chat detect true/false: **{chat_true}/{chat_false}**",
        f"- SHORTLIST present: {'yes' if short_p.is_file() else 'no'}",
        "",
        "## Record more of (agent advice)",
        "",
    ]
    # simple rules
    if shots.get("orbit", 0) >= shots.get("fly_or_travel", 0):
        lines.append("- More **fly/establish** with **cinematic hide UI** (orbit stock already good) — see CINEMATIC_ORBIT_UI_MODE.")
    else:
        lines.append("- More **slow orbits** on keepable vistas (fly stock higher).")
    if chat_true > chat_false:
        lines.append("- Prefer **Gather / hide UI** or mark skip_zone when chat dense.")
    else:
        lines.append("- Chat mostly clean — keep current chat hygiene.")
    if speech_status == "SKIP_AMBIENCE_OR_EMPTY" or "broll_bed" in str(audio_role):
        lines.append("- Default product = **B-roll bed**; mic is **AI cue**, not forced VO cuts.")
        lines.append("- Intentional talk night only if you want speech_peaks product.")
    if not zone_hints:
        lines.append("- Leave **TitanPanel up** on MI nights so zone OCR can read location.")
    lines += [
        "- Press **Deck multi-actions** (broll/rotate/talk/skip/gather) so marker export can cut smart.",
        "- Game/desktop dual audio still OPEN until AUDIO_GREEN 10s proof.",
        "- Close **CINEMATIC_ORBIT_UI_MODE** with one clean Alt+Z (or Auto Hide) orbit night.",
        "",
        "## Law",
        "",
        "- No invent FOOTAGE · no silent publish · KEEP wins · no invent zone names.",
        "",
    ]
    out = args.out or (day / "NEXT_NIGHT_BRIEF.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    # also copy to story capture for cold agents
    story = (
        Path(__file__).resolve().parents[2]
        / "04-Story-and-Capture"
        / "returner-daily"
        / "NEXT_NIGHT_BRIEF_LATEST.md"
    )
    try:
        story.parent.mkdir(parents=True, exist_ok=True)
        story.write_text("\n".join(lines), encoding="utf-8")
    except OSError:
        pass
    print(f"next_night_brief -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
