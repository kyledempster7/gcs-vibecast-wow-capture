#!/usr/bin/env python3
"""Promote human KEEP (and pride KEEP) into Moments Library for future projects.

Copy-only. No publish. No invent. Optional Google Drive archive-broll mirror.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_verdicts(day_dir: Path) -> dict:
    hv = day_dir / "analysis" / "human_verdicts.json"
    if not hv.is_file():
        return {}
    return json.loads(hv.read_text(encoding="utf-8"))


def resolve_clip(day_dir: Path, cid: str) -> Path | None:
    cand = day_dir / "candidates"
    pride = cand / "pride"
    # exact / partial filename matches
    patterns = [
        cid if cid.endswith(".mp4") else f"{cid}.mp4",
        f"db-*-{cid}*.mp4",
        f"*{cid}*.mp4",
    ]
    # direct id match on basename stems
    for root in (cand, pride, pride / "vertical", pride / "gated"):
        if not root.is_dir():
            continue
        for p in root.glob("*.mp4"):
            stem = p.stem
            if cid == stem or cid in stem or stem.startswith(cid) or f"-{cid}-" in stem or stem.endswith(f"-{cid}"):
                # prefer full c over random: if cid is short letter like "c"
                if len(cid) <= 2 and cid.isalpha():
                    if stem.startswith(f"db-") and f"-{cid}-" in stem or stem.startswith(f"db-") and f"-{cid}." in p.name:
                        return p
                    if stem == cid:
                        return p
                    continue
                return p
    # letter-id special: db-*-c-full-*.mp4
    if len(cid) <= 2:
        for p in sorted(cand.glob(f"db-*-{cid}-*.mp4")):
            return p
        for p in sorted(cand.glob(f"db-*-{cid}-full-*.mp4")):
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    ap.add_argument("--zone", default="archive", help="Moments folder zone slug")
    ap.add_argument(
        "--moments-root",
        type=Path,
        default=Path.home() / "Movies/WoW-Broll-Workflow/Moments-Library",
    )
    ap.add_argument(
        "--drive",
        action="store_true",
        help="Also mirror keepers to Google Drive archive-broll",
    )
    ap.add_argument(
        "--drive-root",
        type=Path,
        default=Path.home()
        / "Library/CloudStorage/GoogleDrive-kyledempster7@gmail.com/My Drive/GCS-VibeCast-Offload",
    )
    args = ap.parse_args()
    day_dir = args.day_dir.resolve()
    # day from folder name returner-daily-YYYY-MM-DD
    day = day_dir.name.replace("returner-daily-", "") if "returner-daily-" in day_dir.name else day_dir.name
    verdicts = load_verdicts(day_dir)
    keeps = {
        k: v
        for k, v in verdicts.items()
        if str(v.get("verdict", "")).upper() in ("KEEP", "PRIDE_PICK")
    }
    # always try pride KEEP-named stems
    pride_dir = day_dir / "candidates" / "pride"
    if pride_dir.is_dir():
        for p in pride_dir.glob("*.mp4"):
            # if parent c was KEEP, archive pride too
            if "c" in keeps or any(
                str(verdicts.get(x, {}).get("verdict", "")).upper() == "KEEP"
                for x in ("c", "c-pride-15s-start", p.stem)
            ):
                if p.stem not in keeps:
                    # only if pride stem has KEEP or parent c KEEP
                    if p.stem in verdicts:
                        if str(verdicts[p.stem].get("verdict", "")).upper() not in (
                            "KEEP",
                            "PRIDE_PICK",
                        ):
                            continue
                    elif "c" not in keeps and "c-pride-15s-start" not in keeps:
                        continue
                    keeps.setdefault(
                        p.stem,
                        {
                            "verdict": "KEEP",
                            "reason": "pride_from_keep_parent",
                            "source": "archive_keep_auto",
                        },
                    )

    moments_dir = args.moments_root / f"{day}-{args.zone}"
    clips_dir = moments_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    moments_path = moments_dir / "MOMENTS.json"
    moments = {
        "schema": "gcs_moments_library/v1",
        "day": day,
        "zone_hint": args.zone,
        "moments": [],
        "law": "keep_only_for_future; no_invent; no_publish",
    }
    if moments_path.is_file():
        try:
            moments = json.loads(moments_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    by_id = {m.get("id"): m for m in moments.get("moments") or [] if m.get("id")}

    archived = []
    for cid, meta in sorted(keeps.items()):
        src = resolve_clip(day_dir, cid)
        if not src or not src.is_file():
            archived.append({"id": cid, "status": "MISSING_SRC", "meta": meta})
            continue
        dest = clips_dir / src.name
        if not dest.is_file() or dest.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest)
        digest = sha256_file(dest)
        entry = {
            "id": cid,
            "file": f"clips/{dest.name}",
            "tags": [
                "kyle_keep",
                "for_future=true",
                f"source_day={day}",
                f"verdict={meta.get('verdict')}",
            ],
            "note": meta.get("reason") or "",
            "sha256": digest,
            "source_path": str(src),
            "archived_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        # preserve prior tags if any
        if cid in by_id:
            old_tags = by_id[cid].get("tags") or []
            entry["tags"] = sorted(set(list(old_tags) + entry["tags"]))
            if by_id[cid].get("note") and not entry["note"]:
                entry["note"] = by_id[cid]["note"]
        by_id[cid] = entry
        archived.append({"id": cid, "status": "OK", "file": str(dest), "sha256": digest})

        # vertical twin if exists
        vert = day_dir / "candidates" / "pride" / "vertical" / src.name
        if vert.is_file():
            vdest = clips_dir / f"vertical-{src.name}"
            if not vdest.is_file() or vdest.stat().st_size != vert.stat().st_size:
                shutil.copy2(vert, vdest)
            vid = f"{cid}-vertical"
            by_id[vid] = {
                "id": vid,
                "file": f"clips/{vdest.name}",
                "tags": ["kyle_keep", "ratio=9x16", "for_future=true", f"source_day={day}"],
                "sha256": sha256_file(vdest),
                "archived_at_utc": datetime.now(timezone.utc).isoformat(),
            }

    moments["moments"] = list(by_id.values())
    moments["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    moments_path.write_text(json.dumps(moments, indent=2) + "\n", encoding="utf-8")

    archive_doc = {
        "schema": "gcs_archive_keep/v1",
        "day": day,
        "day_dir": str(day_dir),
        "moments_dir": str(moments_dir),
        "keep_ids": list(keeps.keys()),
        "archived": archived,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "law": "copy_only; for_future_projects; no_publish",
    }
    (moments_dir / "ARCHIVE.json").write_text(
        json.dumps(archive_doc, indent=2) + "\n", encoding="utf-8"
    )
    (day_dir / "analysis" / "ARCHIVE_KEEP.json").write_text(
        json.dumps(archive_doc, indent=2) + "\n", encoding="utf-8"
    )

    # CATALOG rollup
    catalog_path = args.moments_root / "CATALOG.json"
    catalog = {"schema": "gcs_moments_catalog/v1", "entries": []}
    if catalog_path.is_file():
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    entries = [
        e
        for e in (catalog.get("entries") or [])
        if e.get("day") != day or e.get("zone_hint") != args.zone
    ]
    for m in moments["moments"]:
        entries.append(
            {
                "day": day,
                "zone_hint": args.zone,
                "id": m.get("id"),
                "file": f"{day}-{args.zone}/{m.get('file')}",
                "tags": m.get("tags") or [],
                "sha256": m.get("sha256"),
            }
        )
    catalog["entries"] = entries
    catalog["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    if args.drive:
        drive_day = args.drive_root / "archive-broll" / day
        drive_day.mkdir(parents=True, exist_ok=True)
        for p in clips_dir.glob("*.mp4"):
            d = drive_day / p.name
            if not d.is_file() or d.stat().st_size != p.stat().st_size:
                shutil.copy2(p, d)
        shutil.copy2(moments_dir / "ARCHIVE.json", drive_day / "ARCHIVE.json")
        shutil.copy2(moments_path, drive_day / "MOMENTS.json")
        archive_doc["drive_dir"] = str(drive_day)
        (drive_day / "ARCHIVE.json").write_text(
            json.dumps(archive_doc, indent=2) + "\n", encoding="utf-8"
        )
        print(f"drive_ok {drive_day}")

    ok = sum(1 for a in archived if a.get("status") == "OK")
    print(
        json.dumps(
            {
                "moments_dir": str(moments_dir),
                "keep_n": len(keeps),
                "archived_ok": ok,
                "catalog": str(catalog_path),
            },
            indent=2,
        )
    )
    return 0 if ok or not keeps else 1


if __name__ == "__main__":
    raise SystemExit(main())
