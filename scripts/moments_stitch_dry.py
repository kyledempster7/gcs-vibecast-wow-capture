#!/usr/bin/env python3
"""Moments Library → montage dry-run (concat demuxer). NOT_ARMED. No Zernio."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

FF = "ffmpeg"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--moments-dir", type=Path, required=True)
    ap.add_argument("--max-clips", type=int, default=4)
    ap.add_argument("--prefer-tags", default="orbit,fly")
    ap.add_argument(
        "--max-sec-per-clip",
        type=float,
        default=15.0,
        help="trim each clip for dry montage (avoid multi-hour concat)",
    )
    args = ap.parse_args()
    root = args.moments_dir
    moments_json = root / "MOMENTS.json"
    clips_dir = root / "clips"
    if not moments_json.is_file():
        print(f"missing {moments_json}")
        return 1
    data = json.loads(moments_json.read_text(encoding="utf-8"))
    prefer = [t.strip() for t in args.prefer_tags.split(",") if t.strip()]
    moments = list(data.get("moments") or [])

    def score(m: dict) -> int:
        tags = " ".join(m.get("tags") or [])
        s = 0
        for i, p in enumerate(prefer):
            if p in tags or p in str(m.get("motion", {}).get("shot", "")):
                s += 10 - i
        if "chat_present=true" in tags:
            s -= 2
        return s

    moments.sort(key=score, reverse=True)
    picked = []
    for m in moments:
        rel = m.get("file") or ""
        p = root / rel if rel else clips_dir / f"{m.get('id')}.mp4"
        if not p.is_file():
            # try clips/<id>.mp4
            p2 = clips_dir / f"{m.get('id')}.mp4"
            if p2.is_file():
                p = p2
            else:
                continue
        picked.append({"id": m.get("id"), "path": p, "tags": m.get("tags")})
        if len(picked) >= args.max_clips:
            break

    out_dir = root / "montage-dry"
    out_dir.mkdir(parents=True, exist_ok=True)
    board = {
        "schema": "gcs_moments_stitch_dry/v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "moments_dir": str(root),
        "picked": [{"id": x["id"], "path": str(x["path"]), "tags": x["tags"]} for x in picked],
        "status": "DRY",
        "arm": "NOT_ARMED",
        "law": "no_publish_no_zernio",
    }
    if len(picked) < 2:
        board["status"] = "INSUFFICIENT_CLIPS"
        board["note"] = f"need ≥2 clips, got {len(picked)}"
        (out_dir / "STITCH_DRY.json").write_text(json.dumps(board, indent=2), encoding="utf-8")
        (out_dir / "BOARD.md").write_text(
            f"# Montage dry — insufficient clips ({len(picked)})\n\nNOT_ARMED\n",
            encoding="utf-8",
        )
        print(json.dumps(board, indent=2))
        return 0

    # Pre-trim each clip so dry montage stays review-sized (not multi-hour masters)
    trim_dir = out_dir / "trim"
    trim_dir.mkdir(parents=True, exist_ok=True)
    list_path = out_dir / "concat.txt"
    lines = []
    max_sec = max(3.0, float(args.max_sec_per_clip))
    for x in picked:
        trim_p = trim_dir / f"{x['id']}-t{int(max_sec)}.mp4"
        if not trim_p.is_file() or trim_p.stat().st_size < 1000:
            tr = subprocess.run(
                [
                    FF,
                    "-y",
                    "-ss",
                    "0",
                    "-t",
                    str(max_sec),
                    "-i",
                    str(x["path"]),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "23",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "96k",
                    str(trim_p),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if tr.returncode != 0 or not trim_p.is_file():
                continue
        path = str(trim_p).replace("'", "'\\''")
        lines.append(f"file '{path}'")
    if len(lines) < 2:
        board["status"] = "INSUFFICIENT_TRIMS"
        (out_dir / "STITCH_DRY.json").write_text(json.dumps(board, indent=2), encoding="utf-8")
        print(f"moments_stitch_dry INSUFFICIENT_TRIMS -> {out_dir}")
        return 0
    list_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out_mp4 = out_dir / "montage-dry.mp4"
    # re-encode for safety across different inputs
    cmd = [
        FF,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        str(out_mp4),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    board["ffmpeg_rc"] = r.returncode
    board["out_mp4"] = str(out_mp4) if out_mp4.is_file() else None
    if r.returncode != 0:
        board["status"] = "FFMPEG_FAIL"
        board["stderr_tail"] = (r.stderr or "")[-500:]
    else:
        board["status"] = "DRY_OK"
        board["bytes"] = out_mp4.stat().st_size

    (out_dir / "STITCH_DRY.json").write_text(json.dumps(board, indent=2), encoding="utf-8")
    md = [
        "# Montage dry-run (NOT_ARMED)",
        "",
        f"Status: **{board['status']}**",
        "",
        "## Clips",
    ]
    for x in picked:
        md.append(f"- `{x['id']}`")
    md += ["", f"Output: `{out_mp4.name if out_mp4.is_file() else 'none'}`", "", "No Zernio · no publish.", ""]
    (out_dir / "BOARD.md").write_text("\n".join(md), encoding="utf-8")
    print(f"moments_stitch_dry {board['status']} -> {out_dir}")
    return 0 if board["status"] in ("DRY_OK", "INSUFFICIENT_CLIPS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
