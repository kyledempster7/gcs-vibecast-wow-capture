#!/usr/bin/env python3
"""Query / rebuild Moments-Library CATALOG.json. No invent. No publish."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_catalog(path: Path) -> dict:
    if not path.is_file():
        return {"schema": "gcs_moments_catalog/v1", "entries": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema": "gcs_moments_catalog/v1", "entries": []}


def rebuild(moments_root: Path) -> dict:
    entries: list[dict] = []
    for zone_dir in sorted(moments_root.iterdir()):
        if not zone_dir.is_dir() or zone_dir.name.startswith("."):
            continue
        moments_path = zone_dir / "MOMENTS.json"
        if not moments_path.is_file():
            continue
        try:
            doc = json.loads(moments_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        day = doc.get("day") or zone_dir.name[:10]
        zone = doc.get("zone_hint") or (
            zone_dir.name[11:] if len(zone_dir.name) > 11 else zone_dir.name
        )
        for m in doc.get("moments") or []:
            rel = m.get("file") or ""
            file_rel = f"{zone_dir.name}/{rel}" if rel else None
            abs_clip = zone_dir / rel if rel else None
            digest = m.get("sha256")
            if abs_clip and abs_clip.is_file() and not digest:
                digest = sha256_file(abs_clip)
            entries.append(
                {
                    "day": day,
                    "zone_hint": zone,
                    "id": m.get("id"),
                    "file": file_rel,
                    "tags": m.get("tags") or [],
                    "sha256": digest,
                }
            )
    # Dedupe by file path: prefer sha256 present + kyle_keep tags
    by_file: dict[str, dict] = {}
    for e in entries:
        key = e.get("file") or f"id:{e.get('id')}"
        prev = by_file.get(key)
        if prev is None:
            by_file[key] = e
            continue
        score = (1 if e.get("sha256") else 0) + (
            1 if "kyle_keep" in (e.get("tags") or []) else 0
        )
        pscore = (1 if prev.get("sha256") else 0) + (
            1 if "kyle_keep" in (prev.get("tags") or []) else 0
        )
        if score >= pscore:
            # merge tags
            tags = sorted(set((prev.get("tags") or []) + (e.get("tags") or [])))
            e = dict(e)
            e["tags"] = tags
            if not e.get("sha256") and prev.get("sha256"):
                e["sha256"] = prev["sha256"]
            by_file[key] = e
        else:
            tags = sorted(set((prev.get("tags") or []) + (e.get("tags") or [])))
            prev = dict(prev)
            prev["tags"] = tags
            if not prev.get("sha256") and e.get("sha256"):
                prev["sha256"] = e["sha256"]
            by_file[key] = prev
    out = {
        "schema": "gcs_moments_catalog/v1",
        "entries": list(by_file.values()),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "law": "keep_library_index; no_invent; no_publish",
    }
    return out


def query(entries: list[dict], tag: str | None, day: str | None, keep_only: bool) -> list[dict]:
    out = []
    for e in entries:
        tags = e.get("tags") or []
        if day and e.get("day") != day:
            continue
        if tag and tag not in tags and not any(tag in t for t in tags):
            continue
        if keep_only and "kyle_keep" not in tags and "for_future=true" not in tags:
            continue
        out.append(e)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Moments CATALOG query/rebuild")
    ap.add_argument(
        "--moments-root",
        type=Path,
        default=Path.home() / "Movies/WoW-Broll-Workflow/Moments-Library",
    )
    ap.add_argument("--rebuild", action="store_true", help="Rebuild CATALOG from MOMENTS.json")
    ap.add_argument("--tag", default=None, help="Filter tag substring/exact")
    ap.add_argument("--day", default=None)
    ap.add_argument("--keep-only", action="store_true")
    ap.add_argument("--json", action="store_true", help="Print full JSON results")
    args = ap.parse_args()
    root = args.moments_root.resolve()
    catalog_path = root / "CATALOG.json"

    if args.rebuild:
        cat = rebuild(root)
        catalog_path.write_text(json.dumps(cat, indent=2) + "\n", encoding="utf-8")
        print(
            json.dumps(
                {
                    "action": "rebuild",
                    "entries": len(cat["entries"]),
                    "with_sha256": sum(1 for e in cat["entries"] if e.get("sha256")),
                    "path": str(catalog_path),
                },
                indent=2,
            )
        )
        return 0

    cat = load_catalog(catalog_path)
    hits = query(cat.get("entries") or [], args.tag, args.day, args.keep_only)
    if args.json:
        print(json.dumps(hits, indent=2))
    else:
        for e in hits:
            print(
                f"{e.get('day')}\t{e.get('id')}\t{e.get('file')}\t"
                f"sha={'yes' if e.get('sha256') else 'no'}\t"
                f"tags={','.join(e.get('tags') or [])}"
            )
        print(f"# n={len(hits)} catalog={catalog_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
