#!/usr/bin/env python3
"""
World of Warcraft / WoW — Thrall multi-character roster poller.

Modes:
  --ssr          Public Armory HTML SSR (no secrets) — good for suite rebuild
  --live         Profile API client-credentials (requires .env)
  --dry-run      Print URLs/curls only; no network POST token
  --write-sample Emit sample-shaped tables from roster.yaml notes only

Exit: 0 ok | 1 error | 2 fail-closed (live without secrets)
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "roster.yaml"
OUTPUT = ROOT / "output"
ENV_PATH = ROOT / ".env"
UA = "kyle-wow-roster-tracker/2.0 (+local personal tooling)"


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def load_roster(path: Path) -> dict:
    """Minimal YAML subset for our config (no PyYAML required)."""
    text = path.read_text(encoding="utf-8")
    data: dict = {
        "region": "us",
        "realm": "thrall",
        "locale": "en_US",
        "namespace": "profile-us",
        "characters": [],
        "not_in_roster": [],
        "fetch_mounts": False,
        "fetch_equipment": True,
        "fetch_specializations": True,
    }
    section = None
    current_char: dict | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*:", line) and not line.startswith(" "):
            key, _, rest = line.partition(":")
            key = key.strip()
            rest = rest.strip()
            section = None
            current_char = None
            if key in ("characters", "not_in_roster"):
                section = key
                data[key] = []
            elif rest in ("true", "false"):
                data[key] = rest == "true"
            elif rest:
                data[key] = rest.strip('"').strip("'")
            continue
        if section and line.strip().startswith("- name:"):
            name = line.split(":", 1)[1].strip().strip('"').strip("'")
            current_char = {"name": name}
            data[section].append(current_char)
            continue
        if section and current_char and ":" in line:
            k, _, v = line.strip().partition(":")
            current_char[k.strip()] = v.strip().strip('"').strip("'")
    return data


def http_get(url: str, headers: dict | None = None, timeout: int = 30) -> tuple[int, str]:
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body


def extract_ssr_state(html: str) -> dict | None:
    idx = html.find("characterProfileInitialState")
    if idx < 0:
        return None
    j = html.find("{", idx)
    if j < 0:
        return None
    depth = 0
    end = None
    in_str = False
    esc = False
    for i, ch in enumerate(html[j:], j):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        return None
    try:
        return json.loads(html[j:end])
    except json.JSONDecodeError:
        return None


def parse_ssr_character(name: str, state: dict) -> dict:
    ch = state.get("character") or {}
    race = ch.get("race")
    if isinstance(race, dict):
        race = race.get("name")
    klass = ch.get("class")
    if isinstance(klass, dict):
        klass = klass.get("name")
    faction = ch.get("faction")
    if isinstance(faction, dict):
        faction = faction.get("name")
    spec = ch.get("spec")
    if isinstance(spec, dict):
        spec = spec.get("name")
    elif isinstance(spec, str):
        pass
    else:
        specs = ch.get("specs") or []
        if isinstance(specs, list):
            for s in specs:
                if isinstance(s, dict) and s.get("isActive"):
                    spec = s.get("name")
                    break
            if not spec and specs and isinstance(specs[0], dict):
                spec = specs[0].get("name")
    title = ch.get("title")
    if isinstance(title, dict):
        title = title.get("name") or title.get("display") or title.get("title")
    if isinstance(title, str) and "{name}" in title:
        title = title.replace("{name}", "").strip() or "—"
    if not title:
        title = "—"

    def _item_level(item: dict):
        for key in ("itemLevel", "level", "timewalker_level"):
            v = item.get(key)
            if isinstance(v, dict):
                if "value" in v:
                    return v["value"]
                if "display_string" in v:
                    m = re.search(r"(\d+)", str(v["display_string"]))
                    if m:
                        return m.group(1)
            elif v is not None and v != "":
                return v
        return ""

    gear_rows = []
    gear = ch.get("gear") or {}
    if isinstance(gear, dict):
        for slot_key, item in gear.items():
            if not isinstance(item, dict):
                continue
            slot = item.get("slot") or {}
            slot_name = slot.get("type") or slot_key.upper()
            item_name = item.get("name") or "—"
            item_id = item.get("id") or ""
            gear_rows.append(
                {
                    "slot": str(slot_name),
                    "name": str(item_name),
                    "id": item_id,
                    "level": _item_level(item),
                }
            )
    avatar = ""
    av = ch.get("avatar") or {}
    if isinstance(av, dict):
        avatar = av.get("url") or ""
    return {
        "name": ch.get("name") or name,
        "realm": "Thrall",
        "faction": faction or "—",
        "race": race or "—",
        "class": klass or "—",
        "active_spec": spec or "—",
        "level": ch.get("level") or "—",
        "avg_ilvl": ch.get("averageItemLevel") or "—",
        "equipped_ilvl": ch.get("equippedItemLevel") or ch.get("averageItemLevel") or "—",
        "achievement_points": ch.get("achievement") or "—",
        "title": title or "—",
        "guild": "—",
        "source": "ssr",
        "mode": "ssr",
        "http": {"armory_html": 200},
        "equipment": gear_rows,
        "avatar": avatar,
        "armory_url": f"https://worldofwarcraft.blizzard.com/en-us/character/us/thrall/{name.lower()}",
        "notes": "",
        "error": None,
    }


def fetch_ssr(name: str) -> dict:
    url = f"https://worldofwarcraft.blizzard.com/en-us/character/us/thrall/{name.lower()}"
    code, body = http_get(url)
    if code == 404:
        return {
            "name": name,
            "source": "ssr",
            "mode": "ssr",
            "error": "HTTP 404 — character not found on Armory (not created or wrong realm/name)",
            "http": {"armory_html": 404},
            "equipment": [],
            "armory_url": url,
        }
    if code != 200:
        return {
            "name": name,
            "source": "ssr",
            "mode": "ssr",
            "error": f"HTTP {code}",
            "http": {"armory_html": code},
            "equipment": [],
            "armory_url": url,
        }
    state = extract_ssr_state(body)
    if not state:
        return {
            "name": name,
            "source": "ssr",
            "mode": "ssr",
            "error": "SSR state not found in HTML",
            "http": {"armory_html": code},
            "equipment": [],
            "armory_url": url,
        }
    row = parse_ssr_character(name, state)
    row["http"] = {"armory_html": code}
    return row


def get_token() -> str | None:
    cid = os.environ.get("BLIZZARD_CLIENT_ID", "").strip()
    sec = os.environ.get("BLIZZARD_CLIENT_SECRET", "").strip()
    if not cid or not sec:
        return None
    auth = base64.b64encode(f"{cid}:{sec}".encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(
        "https://oauth.battle.net/token",
        data=data,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": UA,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode())
    return payload.get("access_token")


def api_get(path: str, token: str, namespace: str, locale: str) -> tuple[int, dict | None]:
    q = urllib.parse.urlencode({"namespace": namespace, "locale": locale})
    url = f"https://us.api.blizzard.com{path}?{q}"
    code, body = http_get(url, headers={"Authorization": f"Bearer {token}"})
    if code != 200:
        return code, None
    try:
        return code, json.loads(body)
    except json.JSONDecodeError:
        return code, None


def fetch_live(name: str, cfg: dict, token: str) -> dict:
    realm = cfg.get("realm", "thrall")
    ns = cfg.get("namespace", "profile-us")
    locale = cfg.get("locale", "en_US")
    base = f"/profile/wow/character/{realm}/{name.lower()}"
    codes = {}
    c_sum, summary = api_get(base, token, ns, locale)
    codes["summary"] = c_sum
    c_eq, equipment = (None, None)
    if cfg.get("fetch_equipment", True):
        c_eq, equipment = api_get(f"{base}/equipment", token, ns, locale)
        codes["equipment"] = c_eq
    c_sp, specs = (None, None)
    if cfg.get("fetch_specializations", True):
        c_sp, specs = api_get(f"{base}/specializations", token, ns, locale)
        codes["specializations"] = c_sp

    if c_sum != 200 or not summary:
        return {
            "name": name,
            "source": "api",
            "mode": "live",
            "error": f"summary HTTP {c_sum}",
            "http": codes,
            "equipment": [],
            "armory_url": f"https://worldofwarcraft.blizzard.com/en-us/character/us/{realm}/{name.lower()}",
        }

    race = (summary.get("race") or {}).get("name", "—")
    klass = (summary.get("character_class") or {}).get("name", "—")
    faction = (summary.get("faction") or {}).get("name", "—")
    active = summary.get("active_spec") or {}
    spec = active.get("name", "—") if isinstance(active, dict) else "—"
    guild = summary.get("guild") or {}
    guild_name = guild.get("name", "—") if isinstance(guild, dict) else "—"

    gear_rows = []
    if equipment and isinstance(equipment.get("equipped_items"), list):
        for it in equipment["equipped_items"]:
            slot = (it.get("slot") or {}).get("type", "—")
            gear_rows.append(
                {
                    "slot": slot,
                    "name": it.get("name", "—"),
                    "id": it.get("item", {}).get("id", ""),
                    "level": it.get("level", {}).get("value", "")
                    if isinstance(it.get("level"), dict)
                    else it.get("level", ""),
                }
            )

    return {
        "name": summary.get("name") or name,
        "realm": (summary.get("realm") or {}).get("name", "Thrall"),
        "faction": faction,
        "race": race,
        "class": klass,
        "active_spec": spec,
        "level": summary.get("level", "—"),
        "avg_ilvl": summary.get("average_item_level", "—"),
        "equipped_ilvl": summary.get("equipped_item_level", "—"),
        "achievement_points": summary.get("achievement_points", "—"),
        "title": "—",
        "guild": guild_name or "—",
        "source": "api",
        "mode": "live",
        "http": codes,
        "equipment": gear_rows,
        "avatar": "",
        "armory_url": f"https://worldofwarcraft.blizzard.com/en-us/character/us/{realm}/{name.lower()}",
        "notes": "",
        "error": None,
        "last_login_timestamp": summary.get("last_login_timestamp"),
    }


def render_markdown(chars: list[dict], mode: str, stamp: str, not_in: list[dict]) -> str:
    lines = [
        f"# WoW roster readout — {stamp}",
        "",
        f"**Mode:** `{mode}`  ",
        f"**Realm:** Thrall (us)  ",
        f"**Generated:** {stamp}  ",
        f"**Tool:** `Games/WoW/wow-roster-tracker` (care suite)  ",
        "",
    ]
    if not_in:
        lines.append("## Not in this roster")
        lines.append("")
        for n in not_in:
            lines.append(f"- **{n.get('name','?')}** — {n.get('reason','')}")
        lines.append("")

    # summary table first
    lines += [
        "## Suite board (all polled)",
        "",
        "| Name | Level | Class | Spec | Avg ilvl | Source | Status |",
        "|------|------:|-------|------|---------:|--------|--------|",
    ]
    for c in chars:
        if c.get("error"):
            lines.append(
                f"| **{c['name']}** | — | — | — | — | {c.get('source','—')} | {c['error'][:40]} |"
            )
        else:
            lines.append(
                f"| **{c['name']}** | {c.get('level','—')} | {c.get('class','—')} | "
                f"{c.get('active_spec','—')} | {c.get('avg_ilvl','—')} | `{c.get('source','—')}` | ok |"
            )
    lines.append("")

    for c in chars:
        lines.append(f"## {c['name']}")
        lines.append("")
        if c.get("error"):
            lines.append(f"*{c['error']}*")
            lines.append("")
            if c.get("armory_url"):
                lines.append(f"Armory: {c['armory_url']}")
                lines.append("")
            continue
        lines.append(f"*{c.get('mode')} | source `{c.get('source')}`*")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        for k, label in [
            ("name", "Name"),
            ("realm", "Realm"),
            ("faction", "Faction"),
            ("race", "Race"),
            ("class", "Class"),
            ("active_spec", "Active spec"),
            ("level", "Level"),
            ("avg_ilvl", "Avg ilvl"),
            ("equipped_ilvl", "Equipped ilvl"),
            ("achievement_points", "Achievement points"),
            ("title", "Title"),
            ("guild", "Guild"),
            ("source", "Source"),
            ("mode", "Mode"),
        ]:
            lines.append(f"| {label} | {c.get(k, '—')} |")
        lines.append(f"| HTTP | `{json.dumps(c.get('http') or {})}` |")
        if c.get("armory_url"):
            lines.append(f"| Armory | {c['armory_url']} |")
        if c.get("avatar"):
            lines.append(f"| Avatar | {c['avatar']} |")
        lines.append("")
        eq = c.get("equipment") or []
        if eq:
            lines.append("### Equipment (notable / equipped)")
            lines.append("")
            lines.append("| Slot | Item | ID | Level |")
            lines.append("|------|------|----|-------|")
            for e in eq:
                lines.append(
                    f"| {e.get('slot','—')} | {e.get('name','—')} | {e.get('id','')} | {e.get('level','')} |"
                )
            lines.append("")
    return "\n".join(lines) + "\n"


def render_html_suite(chars: list[dict], stamp: str) -> str:
    cards = []
    for c in chars:
        if c.get("error"):
            body = f"<p class='err'>{c['error']}</p>"
            meta = ""
        else:
            meta = f"""
            <div class="meta">
              <span>{c.get('race','')}</span> |
              <span>{c.get('class','')}</span> |
              <span>{c.get('active_spec','')}</span>
            </div>
            <div class="stats">
              <div><b>Level</b><br>{c.get('level','—')}</div>
              <div><b>Avg ilvl</b><br>{c.get('avg_ilvl','—')}</div>
              <div><b>Equipped</b><br>{c.get('equipped_ilvl','—')}</div>
              <div><b>AP</b><br>{c.get('achievement_points','—')}</div>
            </div>
            <p class="src">Source: <code>{c.get('source')}</code> | {c.get('faction','')} | Thrall</p>
            """
            if c.get("armory_url"):
                meta += f"<p><a href=\"{c['armory_url']}\" target=\"_blank\" rel=\"noopener\">Open official Armory</a></p>"
            eq = c.get("equipment") or []
            if eq:
                rows = "".join(
                    f"<tr><td>{e.get('slot')}</td><td>{e.get('name')}</td><td>{e.get('level')}</td></tr>"
                    for e in eq[:20]
                )
                meta += f"<table class='gear'><thead><tr><th>Slot</th><th>Item</th><th>ilvl</th></tr></thead><tbody>{rows}</tbody></table>"
            body = meta
        av = ""
        if c.get("avatar"):
            av = f"<img class='av' src=\"{c['avatar']}\" alt=\"\"/>"
        cards.append(
            f"<article class='card'><header>{av}<h2>{c['name']}</h2></header>{body}</article>"
        )
    cards_html = "\n".join(cards)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>WoW Care Suite — Thrall — {stamp}</title>
<style>
  :root {{ color-scheme: dark; --bg:#0f1419; --card:#1a2332; --text:#e7ecf3; --muted:#8b9bb4; --accent:#c9a227; --ok:#3d9a6a; }}
  body {{ margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; background:var(--bg); color:var(--text); }}
  header.page {{ padding:1.5rem 1.25rem 0.5rem; border-bottom:1px solid #2a3548; }}
  header.page h1 {{ margin:0 0 0.25rem; font-size:1.35rem; }}
  header.page p {{ margin:0; color:var(--muted); font-size:0.9rem; }}
  .grid {{ display:grid; gap:1rem; padding:1.25rem; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }}
  .card {{ background:var(--card); border-radius:12px; padding:1rem 1.1rem 1.2rem; border:1px solid #2a3548; }}
  .card h2 {{ margin:0; font-size:1.15rem; color:var(--accent); }}
  .card header {{ display:flex; gap:0.75rem; align-items:center; margin-bottom:0.6rem; }}
  .av {{ width:48px; height:48px; border-radius:8px; object-fit:cover; background:#000; }}
  .meta {{ color:var(--muted); font-size:0.9rem; margin-bottom:0.75rem; }}
  .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:0.5rem; margin-bottom:0.75rem; }}
  .stats div {{ background:#121a24; border-radius:8px; padding:0.45rem; text-align:center; font-size:0.85rem; }}
  .src {{ color:var(--muted); font-size:0.8rem; }}
  a {{ color:#7eb6ff; }}
  .gear {{ width:100%; border-collapse:collapse; font-size:0.75rem; margin-top:0.5rem; }}
  .gear th, .gear td {{ border-bottom:1px solid #2a3548; padding:0.25rem 0.2rem; text-align:left; }}
  .err {{ color:#f0a0a0; }}
  footer {{ padding:1rem 1.25rem 2rem; color:var(--muted); font-size:0.8rem; }}
</style>
</head>
<body>
<header class="page">
  <h1>World of Warcraft — Care suite (Thrall)</h1>
  <p>Generated {stamp} | Public Armory-aligned fields | Source tagged per card</p>
</header>
<main class="grid">
{cards_html}
</main>
<footer>
  Local personal board | Games/WoW/wow-roster-tracker | Not a Blizzard product | Secrets never shown here
</footer>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="WoW Thrall roster poller")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ssr", action="store_true", help="Public Armory SSR (no secrets)")
    g.add_argument("--live", action="store_true", help="Profile API (requires .env)")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write-sample", action="store_true")
    ap.add_argument("--vault-sync", action="store_true")
    ap.add_argument(
        "--scorecard",
        dest="scorecard",
        action="store_true",
        default=True,
        help="Write Characters/scorecards after pull (SCH-2; default on)",
    )
    ap.add_argument(
        "--no-scorecard",
        dest="scorecard",
        action="store_false",
        help="Skip scorecard write after pull",
    )
    ap.add_argument("--mounts", action="store_true")
    ap.add_argument("--kind", default="full", choices=["full", "light"])
    args = ap.parse_args()

    load_dotenv(ENV_PATH)
    if not CONFIG_PATH.is_file():
        print(f"ERROR: missing {CONFIG_PATH}", file=sys.stderr)
        return 1
    cfg = load_roster(CONFIG_PATH)
    chars_cfg = cfg.get("characters") or []
    not_in = cfg.get("not_in_roster") or []
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print("DRY-RUN — no token POST")
        for c in chars_cfg:
            n = c["name"].lower()
            realm = cfg.get("realm", "thrall")
            print(f"API summary: https://us.api.blizzard.com/profile/wow/character/{realm}/{n}?namespace=profile-us&locale=en_US")
            print(f"SSR armory:  https://worldofwarcraft.blizzard.com/en-us/character/us/{realm}/{n}")
        return 0

    results: list[dict] = []
    mode = "ssr"

    if args.write_sample:
        mode = "sample"
        for c in chars_cfg:
            results.append(
                {
                    "name": c["name"],
                    "realm": "Thrall",
                    "faction": "Horde",
                    "race": "—",
                    "class": "—",
                    "active_spec": "—",
                    "level": "—",
                    "avg_ilvl": "—",
                    "equipped_ilvl": "—",
                    "achievement_points": "—",
                    "title": "—",
                    "guild": "—",
                    "source": "sample",
                    "mode": "sample",
                    "http": {},
                    "equipment": [],
                    "notes": c.get("notes", ""),
                    "error": None,
                    "armory_url": f"https://worldofwarcraft.blizzard.com/en-us/character/us/thrall/{c['name'].lower()}",
                }
            )
    elif args.ssr:
        mode = "ssr"
        for c in chars_cfg:
            print(f"SSR {c['name']}…", flush=True)
            row = fetch_ssr(c["name"])
            row["notes"] = c.get("notes", "")
            results.append(row)
    elif args.live:
        mode = "live"
        token = get_token()
        if not token:
            print("FAIL-CLOSED: BLIZZARD_CLIENT_ID / BLIZZARD_CLIENT_SECRET missing.")
            print(f"Create client at https://develop.battle.net/access/clients")
            print(f"Copy {ENV_PATH}.example -> {ENV_PATH} and fill values (never commit).")
            print("Until then: python scripts/fetch_roster.py --ssr")
            return 2
        for c in chars_cfg:
            print(f"API {c['name']}…", flush=True)
            row = fetch_live(c["name"], cfg, token)
            row["notes"] = c.get("notes", "")
            results.append(row)

    md = render_markdown(results, mode, stamp, not_in)
    out_md = OUTPUT / f"roster_readout_{stamp}.md"
    latest = OUTPUT / "latest.md"
    out_md.write_text(md, encoding="utf-8")
    latest.write_text(md, encoding="utf-8")

    snap = {
        "mode": mode,
        "stamp": stamp,
        "realm": "thrall",
        "characters": results,
        "not_in_roster": not_in,
    }
    out_json = OUTPUT / f"roster_snapshot_{stamp}.json"
    latest_json = OUTPUT / "latest.json"
    out_json.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    latest_json.write_text(json.dumps(snap, indent=2), encoding="utf-8")

    suite_dir = ROOT.parent / "Characters" / "armory-suite"
    suite_dir.mkdir(parents=True, exist_ok=True)
    html = render_html_suite(results, stamp)
    (suite_dir / "index.html").write_text(html, encoding="utf-8")
    (suite_dir / "latest.md").write_text(md, encoding="utf-8")
    (suite_dir / f"suite_{stamp}.md").write_text(md, encoding="utf-8")
    (suite_dir / "README.md").write_text(
        f"""# WoW Armory care suite (Thrall)

**Generated:** {stamp}  
**Mode:** `{mode}`  
**Open for Kyle:** [index.html](index.html) (browser) | [latest.md](latest.md)

Pull command:

```bash
cd Games/WoW/wow-roster-tracker
python3 scripts/fetch_roster.py --ssr          # public Armory, no secrets
# or
python3 scripts/fetch_roster.py --live         # Profile API when .env present
```

Care six in `config/roster.yaml`. Crimson Rage not owned until created (404).
""",
        encoding="utf-8",
    )

    if args.vault_sync:
        # ROOT = <vault>/Games/WoW/wow-roster-tracker -> parents[2] = vault root
        vault_root = ROOT.parents[2]
        vault_dir = (
            vault_root
            / "Kyle's Notes"
            / "Research"
            / "World of Warcraft"
            / "Thrall Roster Readouts"
        )
        vault_dir.mkdir(parents=True, exist_ok=True)
        day = datetime.now().strftime("%Y-%m-%d")
        dest = vault_dir / f"{day}-tool-{mode}.md"
        dest.write_text(md, encoding="utf-8")
        print(f"vault-sync -> {dest}")

    if args.scorecard and mode in ("live", "ssr"):
        try:
            import importlib.util

            sc_path = Path(__file__).resolve().parent / "write_scorecard.py"
            spec = importlib.util.spec_from_file_location("write_scorecard", sc_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                sc_rc = mod.main()
                print(f"scorecard rc={sc_rc}")
            else:
                print("scorecard skip: cannot load write_scorecard.py", file=sys.stderr)
        except Exception as e:
            # Non-fatal: roster pull already succeeded
            print(f"scorecard skip: {e}", file=sys.stderr)

    ok = sum(1 for r in results if not r.get("error"))
    print(f"Wrote {out_md}")
    print(f"Wrote {latest}")
    print(f"Wrote suite HTML -> {suite_dir / 'index.html'}")
    print(f"OK {ok}/{len(results)} characters mode={mode}")
    return 0 if ok == len(results) else (0 if ok > 0 else 1)


if __name__ == "__main__":
    sys.exit(main())
