#!/usr/bin/env python3
"""Draft Returner Daily personality package from real KEEP + signals.

Fail-closed: no KEEP → SKIP (exit 0). Never invent media. armed always false.
Not Class-P. No publish.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


KEEP_OK = frozenset({"KEEP", "PRIDE_PICK"})


def load_verdicts(day_dir: Path) -> dict:
    hv = day_dir / "analysis" / "human_verdicts.json"
    if not hv.is_file():
        return {}
    raw = json.loads(hv.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("verdicts"), dict):
        raw = raw["verdicts"]
    if not isinstance(raw, dict):
        return {}
    out: dict = {}
    for k, v in raw.items():
        if isinstance(v, dict) and "verdict" in v:
            out[str(k)] = v
        elif isinstance(v, str) and v.strip():
            out[str(k)] = {"verdict": v.strip(), "reason": "", "source": "legacy_string"}
    return out


def resolve_clip(day_dir: Path, cid: str) -> Path | None:
    cand = day_dir / "candidates"
    pride = cand / "pride"
    for root in (cand, pride, pride / "vertical", pride / "gated"):
        if not root.is_dir():
            continue
        for p in root.glob("*.mp4"):
            stem = p.stem
            if cid == stem or cid in stem or f"-{cid}-" in stem or stem.endswith(f"-{cid}"):
                if len(cid) <= 2 and cid.isalpha():
                    if stem.startswith("db-") and (f"-{cid}-" in stem or f"-{cid}." in p.name):
                        return p
                    if stem == cid:
                        return p
                    continue
                return p
    if len(cid) <= 2:
        for p in sorted(cand.glob(f"db-*-{cid}-*.mp4")):
            return p
    return None


def load_json(path: Path) -> dict | list | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def pick_stills(day_dir: Path, limit: int = 2) -> list[str]:
    stills: list[Path] = []
    for pattern in ("*.jpg", "*.png", "*.jpeg"):
        stills.extend(day_dir.glob(pattern))
        stills.extend((day_dir / "stills").glob(pattern) if (day_dir / "stills").is_dir() else [])
    stills = sorted({p.resolve() for p in stills if p.is_file()}, key=lambda p: p.stat().st_mtime, reverse=True)
    return [str(p) for p in stills[:limit]]


def speech_notes(day_dir: Path) -> list[str]:
    sp = load_json(day_dir / "analysis" / "SPEECH_PEAKS.json")
    if not isinstance(sp, dict):
        return []
    status = str(sp.get("status") or sp.get("skip_reason") or "")
    peaks = sp.get("peaks") or sp.get("shortlist") or []
    notes = []
    if status:
        notes.append(f"speech_peaks: {status}")
    if isinstance(peaks, list) and peaks:
        notes.append(f"speech_peaks_count: {len(peaks)}")
        notes.append("hint: consider peak=funny if laugh/talk KEEP path used")
    return notes


def story_block(keeps: dict, speech: list[str], stills: list[str]) -> list[str]:
    """Signal-only story lines — no invent levels/rivals."""
    lines = []
    for cid, v in keeps.items():
        reason = (v.get("reason") or "").strip()
        if reason:
            lines.append(f"- KEEP `{cid}`: {reason}")
        else:
            lines.append(f"- KEEP `{cid}` (no reason text)")
    if stills:
        lines.append(f"- Stills available: {len(stills)} (paths in MEDIA_MAP; do not invent achievements)")
    for s in speech:
        lines.append(f"- {s}")
    if not lines:
        lines.append("- No story signals beyond KEEP presence.")
    lines.append("- Style: community / returner / not toxic min-max (CONTENT_STYLE_COMMUNITY).")
    lines.append("- Never invent rival class/race, level counts, or dialogue.")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    ap.add_argument("--force", action="store_true", help="Rewrite draft even if present")
    args = ap.parse_args()
    day_dir = args.day_dir.resolve()
    day = day_dir.name.replace("returner-daily-", "") if "returner-daily-" in day_dir.name else day_dir.name

    verdicts = load_verdicts(day_dir)
    keeps = {
        k: v
        for k, v in verdicts.items()
        if str(v.get("verdict", "")).upper() in KEEP_OK
    }
    if not keeps:
        print(f"draft_personality SKIP no_KEEP day={day}")
        return 0

    pkg = day_dir / "package"
    pkg.mkdir(parents=True, exist_ok=True)
    draft_md = pkg / "DAILY_PERSONALITY_DRAFT.md"
    media_json = pkg / "MEDIA_MAP.json"
    if draft_md.is_file() and not args.force:
        print(f"draft_personality exists (use --force) -> {draft_md}")
        return 0

    videos: list[dict] = []
    for cid, v in keeps.items():
        path = resolve_clip(day_dir, cid)
        videos.append(
            {
                "id": cid,
                "verdict": v.get("verdict"),
                "reason": v.get("reason") or "",
                "path": str(path) if path else None,
                "exists": bool(path and path.is_file()),
            }
        )
    stills = pick_stills(day_dir)
    speech = speech_notes(day_dir)
    utc = datetime.now(timezone.utc).isoformat()

    media = {
        "schema": "gcs_daily_personality_media_map/v1",
        "day": day,
        "generated_at_utc": utc,
        "armed": False,
        "product": "Returner Daily · Personality shape",
        "not_class_p": True,
        "law": "no invent · no silent publish · go-only",
        "videos": videos,
        "stills": stills,
        "speech_notes": speech,
    }
    media_json.write_text(json.dumps(media, indent=2) + "\n", encoding="utf-8")

    story = story_block(keeps, speech, stills)
    real_videos = [v for v in videos if v.get("exists")]
    md = [
        "# Daily personality draft — Returner Daily",
        "",
        f"**Day:** {day}",
        f"**Generated (UTC):** {utc}",
        f"**Armed:** false (NOT_ARMED — kyle_go only)",
        "**Product:** Returner Daily · Personality shape — **not Class-P**",
        "**Law:** real media only · community style · no invent · no silent publish",
        "",
        "## Story block (signals only)",
        "",
        *story,
        "",
        "## Media",
        "",
        f"- KEEP ids: {', '.join(keeps.keys())}",
        f"- Video paths resolved: {len(real_videos)} / {len(videos)}",
        f"- Stills: {len(stills)}",
        f"- Map: `{media_json.name}`",
        "",
        "## Caption seeds (edit; do not invent facts)",
        "",
        "- X: Returner play energy. Real clip from tonight — KEEP only.",
        "- IG: Video + still when both real. Friend leveling next to you. Welcome new + returning.",
        "- Soft footer optional: `Returner energy · Thrall · Horde` (never invent League roster).",
        "",
        "## Agent checklist",
        "",
        "1. Media paths exist?",
        "2. Story claims match KEEP reasons / speech notes only?",
        "3. Tone community-first (CONTENT_STYLE_COMMUNITY)?",
        "4. armed remains false until kyle_go?",
        "",
        "## Next",
        "",
        "- Human KEEP already done for these ids.",
        "- Optional: tag peak=funny if laugh path used.",
        "- Publish only after explicit kyle_go.",
        "",
    ]
    draft_md.write_text("\n".join(md), encoding="utf-8")
    print(f"draft_personality OK day={day} keeps={len(keeps)} videos_ok={len(real_videos)} stills={len(stills)}")
    print(f"  -> {draft_md}")
    print(f"  -> {media_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
