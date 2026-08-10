#!/usr/bin/env python3
"""Build local review-pack: contact sheets + 720p proxies + HTML board. No publish."""
from __future__ import annotations

import argparse
import html
import json
import subprocess
from pathlib import Path

FF = "ffmpeg"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=False, capture_output=True)


def contact_sheet(src: Path, dest: Path, n: int = 9) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    # tile n frames
    cols = 3
    rows = (n + cols - 1) // cols
    vf = f"fps=1/{max(n/10, 0.5)},scale=320:-1,tile={cols}x{rows}"
    run([FF, "-y", "-i", str(src), "-frames:v", "1", "-vf", vf, str(dest)])


def proxy720(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 1000:
        return
    run([
        FF, "-y", "-i", str(src),
        "-vf", "scale=-2:720",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
        "-c:a", "aac", "-b:a", "96k",
        str(dest),
    ])


def load_motion_by_file(day: Path) -> dict[str, dict]:
    path = day / "analysis" / "MOTION_TAGS.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    out: dict[str, dict] = {}
    for clip in data.get("clips") or []:
        fn = clip.get("filename")
        if fn:
            out[fn] = clip
    return out


def load_chat_by_stem(day: Path) -> dict[str, dict]:
    analysis = day / "analysis"
    out: dict[str, dict] = {}
    if not analysis.is_dir():
        return out
    for p in analysis.glob("chat_detect_*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        # chat_detect_wow-....json or chat_detect_c-pride-...
        stem = p.stem.replace("chat_detect_", "", 1)
        out[stem] = d
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True, help="Returns/YYYY-MM-DD")
    ap.add_argument("--score", type=Path, default=None)
    args = ap.parse_args()
    day = args.day_dir
    cand = day / "candidates"
    score_path = args.score or (day / "analysis" / "REJECT_PROBE.json")
    score = json.loads(score_path.read_text(encoding="utf-8")) if score_path.is_file() else {}
    by_id = {r["id"]: r for r in score.get("candidates") or []}
    eyes = set(score.get("eyes_on") or score.get("keep") or [])
    # always include KEEP even if eyes empty
    for r in score.get("candidates") or []:
        if str(r.get("final_verdict", "")).upper() == "KEEP":
            eyes.add(r["id"])

    motion_by_file = load_motion_by_file(day)
    chat_by_stem = load_chat_by_stem(day)

    pack = day / "review-pack"
    sheets = pack / "sheets"
    proxies = pack / "proxies"
    pack.mkdir(parents=True, exist_ok=True)

    cards = []
    for p in sorted(cand.glob("*.mp4")):
        # id
        import re
        m = re.search(r"db-\d{8}-([a-z0-9]+)-", p.name)
        cid = m.group(1) if m else p.stem
        row = by_id.get(cid) or by_id.get(cid[0] if cid else "") or {}
        if not row:
            # score rows use full stem for wow-* files
            row = by_id.get(p.stem) or {}
            if row:
                cid = p.stem
        verdict = str(row.get("final_verdict") or "OPEN").upper()
        if verdict in ("REJECT", "AUTO_REJECT") and cid not in eyes:
            continue
        if eyes and cid not in eyes and verdict != "KEEP":
            # still show REJECT briefly in HTML as muted? skip media gen
            if verdict in ("REJECT", "AUTO_REJECT"):
                cards.append({"id": cid, "file": p.name, "verdict": verdict,
                              "reason": row.get("final_reason", ""), "sheet": None, "proxy": None,
                              "duration": row.get("duration_sec"), "skip_media": True,
                              "shot": None, "chat_present": None})
                continue

        mot = motion_by_file.get(p.name) or {}
        chat = chat_by_stem.get(p.stem) or chat_by_stem.get(cid) or {}
        shot = mot.get("shot")
        chat_present = chat.get("chat_present")
        reason_bits = [str(row.get("final_reason") or "")]
        if shot:
            reason_bits.append(f"shot={shot}")
        if chat_present is True:
            reason_bits.append("chat_present=true")
        elif chat_present is False:
            reason_bits.append("chat_present=false")
        reason = " · ".join(x for x in reason_bits if x)

        sheet = sheets / f"{cid}.jpg"
        prox = proxies / f"{cid}-720p.mp4"
        print(f"pack {cid} {verdict} shot={shot}")
        contact_sheet(p, sheet)
        if verdict == "KEEP" or cid in eyes:
            proxy720(p, prox)
        cards.append({
            "id": cid,
            "file": p.name,
            "verdict": verdict,
            "reason": reason,
            "sheet": f"sheets/{cid}.jpg" if sheet.is_file() else None,
            "proxy": f"proxies/{cid}-720p.mp4" if prox.is_file() else None,
            "duration": row.get("duration_sec") or mot.get("duration_sec"),
            "skip_media": False,
            "shot": shot,
            "chat_present": chat_present,
            "second_play": p.name.startswith("wow-"),
        })

    # pride folder if present
    pride_dir = cand / "pride"
    pride_cards = []
    if pride_dir.is_dir():
        for p in sorted(pride_dir.glob("*.mp4")):
            cid = p.stem
            sheet = sheets / f"{cid}.jpg"
            prox = proxies / f"{cid}-720p.mp4"
            contact_sheet(p, sheet)
            # pride already short — copy or light proxy
            proxy720(p, prox)
            vert = pride_dir / "vertical" / p.name
            vert_rel = None
            if vert.is_file():
                vprox = proxies / f"{cid}-9x16.mp4"
                if not vprox.is_file() or vprox.stat().st_size < 1000:
                    # hardlink or light re-proxy path copy via ffmpeg scale only if needed
                    try:
                        if not vprox.exists():
                            vprox.hardlink_to(vert)
                    except OSError:
                        proxy720(vert, vprox)
                if vprox.is_file() or vert.is_file():
                    vert_rel = f"proxies/{cid}-9x16.mp4" if vprox.is_file() else f"../candidates/pride/vertical/{p.name}"
            pride_cards.append({
                "id": cid, "file": p.name, "verdict": "REVIEW_PRIDE",
                "reason": "pride cut from KEEP c",
                "sheet": f"sheets/{cid}.jpg" if sheet.is_file() else None,
                "proxy": f"proxies/{cid}-720p.mp4" if prox.is_file() else None,
                "vertical": vert_rel,
            })

    def card_html(c: dict) -> str:
        badge = c["verdict"]
        color = {"KEEP": "#2d6a4f", "REJECT": "#6b1c1c", "AUTO_REJECT": "#6b1c1c",
                 "REVIEW_PRIDE": "#1d3557", "AUTO_REVIEW": "#6c584c"}.get(badge, "#333")
        img = f'<img src="{c["sheet"]}" alt="{c["id"]}" style="width:100%;border-radius:6px"/>' if c.get("sheet") else ""
        vid = f'<p><a href="{c["proxy"]}">720p proxy</a></p>' if c.get("proxy") else ""
        vert = f'<p><a href="{c["vertical"]}">9:16 vertical</a></p>' if c.get("vertical") else ""
        shot = c.get("shot")
        shot_line = f'<p style="color:#9bdeac;font-size:12px">shot={html.escape(str(shot))}</p>' if shot else ""
        sp = ' · second-play' if c.get("second_play") else ""
        return f'''<div class="card" style="border:1px solid #333;padding:12px;border-radius:8px;background:#121826">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <strong style="color:#f3e9d7">{html.escape(c["id"])}{html.escape(sp)}</strong>
    <span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:12px">{html.escape(badge)}</span>
  </div>
  <p style="color:#a89b84;font-size:13px;margin:6px 0">{html.escape(str(c.get("reason") or ""))}</p>
  <p style="color:#7ec8e3;font-size:12px">{html.escape(c.get("file") or "")}</p>
  {shot_line}
  {img}
  {vid}
  {vert}
  <div class="gcs-one-tap-verdict" data-id="{html.escape(c["id"])}">
    <button class="keep" type="button" data-v="KEEP">KEEP</button>
    <button class="reject" type="button" data-v="REJECT">REJECT</button>
    <div class="msg"></div>
  </div>
</div>'''

    second_play = [c for c in cards if c.get("second_play")]
    first_play = [c for c in cards if not c.get("second_play")]
    body = "\n".join(card_html(c) for c in pride_cards + second_play + first_play)
    page = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>Review pack — Returner Daily</title>
<style>
body {{ font-family: system-ui,sans-serif; background:#0b0e14; color:#f3e9d7; margin:24px; }}
h1 {{ color:#7ec8e3; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:16px; }}
.note {{ color:#a89b84; max-width:720px; }}
.gcs-one-tap-verdict button {{ margin:4px 4px 0 0; padding:6px 10px; border-radius:6px; border:0; cursor:pointer; font-weight:600; }}
.gcs-one-tap-verdict .keep {{ background:#2d6a4f; color:#fff; }}
.gcs-one-tap-verdict .reject {{ background:#9b2226; color:#fff; }}
.gcs-one-tap-verdict .msg {{ font-size:12px; color:#9bdeac; min-height:1em; }}
</style></head>
<body>
<h1>Returner Daily review pack</h1>
<p class="note">No publish. Human feedback wins. Pride cuts first, then <strong>second-play orbit</strong> shortlist, then earlier eyes.
One-tap KEEP/REJECT needs: <code>python3 scripts/review_pack_feedback_server.py --day-dir &lt;day&gt;</code> then open the local URL.
Or CLI: <em>keep mid</em> · <em>reject h2</em> · plain English · <em>go video with &lt;id&gt;</em> only if proud.</p>
<p class="note">eyes_on: {", ".join(html.escape(x) for x in sorted(eyes)) or "(none)"}</p>
<div class="grid">
{body}
</div>
<script>
async function gcsVerdict(id, verdict, el) {{
  const msg = el.parentElement.querySelector('.msg');
  try {{
    const r = await fetch('/verdict', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{id, verdict, note: 'one_tap_board'}})
    }});
    const j = await r.json();
    msg.textContent = j.ok ? (verdict + ' saved') : ('err ' + (j.stderr || j.error || ''));
  }} catch (e) {{
    msg.textContent = 'start review_pack_feedback_server.py for one-tap';
  }}
}}
document.querySelectorAll('.gcs-one-tap-verdict button').forEach(btn => {{
  btn.addEventListener('click', () => gcsVerdict(btn.parentElement.dataset.id, btn.dataset.v, btn));
}});
</script>
</body></html>'''
    (pack / "index.html").write_text(page, encoding="utf-8")

    # ≤60s product: cap primary eyes to ≤8 (pride + best second-play + KEEP)
    short = [
        "# SHORTLIST — ≤60s review (open these first)",
        "",
        "_Primary eyes capped ≤8. Skip the rest unless curious._",
        "",
        "## Pride cuts (from KEEP)",
        "",
    ]
    primary_count = 0
    for c in pride_cards:
        vnote = " · **9:16 ready**" if c.get("vertical") else ""
        short.append(f"- **{c['id']}** — REVIEW_PRIDE{vnote}")
        primary_count += 1
    short += ["", "## Second-play (orbit shortlist · eyes only · not KEEP)", ""]
    sp_added = 0
    for c in second_play:
        if c["verdict"] not in ("KEEP", "AUTO_REVIEW", "OPEN", "REVIEW"):
            continue
        if primary_count >= 8:
            short.append(f"- _(cap)_ more second-play in index.html only")
            break
        short.append(
            f"- **{c['id']}** — {c['verdict']} — {c.get('reason') or 'second-play'}"
        )
        primary_count += 1
        sp_added += 1
    if not second_play or sp_added == 0:
        if not second_play:
            short.append("- _(none landed)_")
    short += ["", "## Eyes on (earlier night · secondary)", ""]
    for c in first_play:
        if c["verdict"] in ("KEEP", "AUTO_REVIEW", "OPEN", "REVIEW"):
            if primary_count < 8 or str(c["verdict"]).upper() == "KEEP":
                short.append(f"- **{c['id']}** — {c['verdict']} — {c.get('reason','')}")
                primary_count += 1
            else:
                short.append(f"- _(secondary)_ **{c['id']}** — {c['verdict']}")
    short += ["", "## Rejected (skip)", ""]
    for c in cards:
        if c["verdict"] in ("REJECT", "AUTO_REJECT"):
            short.append(f"- ~~{c['id']}~~ — {c.get('reason','')}")
    # speech peaks section
    speech_p = day / "analysis" / "SPEECH_PEAKS.json"
    if speech_p.is_file():
        try:
            spj = json.loads(speech_p.read_text(encoding="utf-8"))
            short += ["", "## Speech peaks", ""]
            if spj.get("status") == "OK" and spj.get("shortlist"):
                for p in spj["shortlist"]:
                    short.append(
                        f"- **{p['id']}** {p['start_sec']}–{p['end_sec']}s — {p.get('text_preview','')[:80]}"
                    )
            else:
                short.append(f"- _{spj.get('status', 'n/a')}: {spj.get('note', 'no VO peaks')}_")
        except json.JSONDecodeError:
            pass
    short += [
        "",
        "## Law",
        "- No publish · video only on Kyle **go**",
        "- Chat blur only if `chat_present=true`",
        "- Feedback: `python3 scripts/record_feedback.py --day-dir <day> --id <id> --verdict KEEP|REJECT --note '…'`",
        "",
    ]
    (pack / "SHORTLIST.md").write_text("\n".join(short) + "\n", encoding="utf-8")
    print(f"review-pack -> {pack}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
