#!/usr/bin/env python3
"""
Local path resolver for Games/WoW doors — bypass AIOS named-role registry misses.

Reads 00-Index/ROLE_PATH_MAP.json (+ optional media_roots.json).
Prints vault-relative + Mac abs + Windows abs + exists-on-this-host.

Usage:
  python3 resolve_wow_door.py --role windows_hello
  python3 resolve_wow_door.py --list
  python3 resolve_wow_door.py --probe-all
  python3 resolve_wow_door.py --role WINDOWS_HELLO   # alias ok
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

WOW = Path(__file__).resolve().parents[2]
MAP = WOW / "00-Index" / "ROLE_PATH_MAP.json"
MEDIA = WOW / "00-Index" / "media_roots.json"


def load_map() -> dict:
    if not MAP.is_file():
        print(f"ERROR missing {MAP}", file=sys.stderr)
        sys.exit(2)
    return json.loads(MAP.read_text(encoding="utf-8"))


def roots(data: dict) -> tuple[str, str]:
    r = data.get("roots") or {}
    mac = r.get("mac_vault") or "/Users/kyle/Kyles_Vault/kyles_corner"
    win = r.get("windows_vault") or r"D:\KyleData\KnownFolders\Documents\kyles_corner"
    if MEDIA.is_file():
        try:
            m = json.loads(MEDIA.read_text(encoding="utf-8"))
            mac = (m.get("mac") or {}).get("vault") or mac
            win = (m.get("windows") or {}).get("vault") or win
        except Exception:
            pass
    return mac, win


def resolve_role(data: dict, key: str) -> dict | None:
    roles = data.get("roles") or {}
    aliases = data.get("aliases") or {}
    k = key.strip()
    if k in roles:
        role_id = k
    elif k in aliases:
        role_id = aliases[k]
    elif k.upper() in aliases:
        role_id = aliases[k.upper()]
    elif k.lower() in aliases:
        role_id = aliases[k.lower()]
    else:
        # fuzzy: strip .md
        bare = k.replace(".md", "").replace("-", "_")
        if bare in roles:
            role_id = bare
        elif bare.upper() in aliases:
            role_id = aliases[bare.upper()]
        else:
            return None
    info = dict(roles[role_id])
    info["role_id"] = role_id
    return info


def abs_paths(rel: str, mac_root: str, win_root: str) -> tuple[Path, Path]:
    rel_norm = rel.replace("\\", "/").lstrip("/")
    mac = Path(mac_root) / rel_norm
    # Windows path for display + optional local check
    win = Path(win_root) / Path(*rel_norm.split("/"))
    return mac, win


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve WoW vault doors without AIOS registry")
    ap.add_argument("--role", default=None, help="role id or alias (windows_hello, WINDOWS_HELLO, …)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--probe-all", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    data = load_map()
    mac_root, win_root = roots(data)
    host = platform.system().lower()

    if args.list:
        for rid, info in sorted((data.get("roles") or {}).items()):
            print(f"{rid}\t{info.get('rel')}")
        for a, t in sorted((data.get("aliases") or {}).items()):
            print(f"alias:{a}\t->\t{t}")
        return 0

    if args.probe_all:
        rows = []
        for rid in sorted((data.get("roles") or {}).keys()):
            info = resolve_role(data, rid)
            assert info
            mac_p, win_p = abs_paths(info["rel"], mac_root, win_root)
            local = mac_p if host == "darwin" else win_p
            # On Mac, only probe Mac path; on Windows only Windows
            exists = local.is_file() or local.is_dir()
            rows.append(
                {
                    "role": rid,
                    "rel": info["rel"],
                    "local_exists": exists,
                    "local": str(local),
                    "mac": str(mac_p),
                    "windows": str(win_p),
                }
            )
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            ok = sum(1 for r in rows if r["local_exists"])
            print(f"probe host={host} local_ok={ok}/{len(rows)} map={MAP}")
            for r in rows:
                flag = "OK" if r["local_exists"] else "MISS"
                print(f"{flag}\t{r['role']}\t{r['local']}")
        return 0 if all(r["local_exists"] for r in rows) else 1

    if not args.role:
        ap.print_help()
        return 2

    info = resolve_role(data, args.role)
    if not info:
        print(f"ERROR unknown role/alias: {args.role!r}", file=sys.stderr)
        print("Try --list", file=sys.stderr)
        return 3

    mac_p, win_p = abs_paths(info["rel"], mac_root, win_root)
    local = mac_p if host == "darwin" else win_p
    out = {
        "role_id": info["role_id"],
        "rel": info["rel"],
        "wikilink": info.get("wikilink"),
        "mac_abs": str(mac_p),
        "windows_abs": str(win_p),
        "this_host": host,
        "local_path": str(local),
        "local_exists": local.is_file() or local.is_dir(),
        "workaround": (data.get("workaround") or [])[:3],
        "map": str(MAP),
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"role={out['role_id']}")
        print(f"rel={out['rel']}")
        print(f"wikilink={out['wikilink']}")
        print(f"mac={out['mac_abs']}")
        print(f"windows={out['windows_abs']}")
        print(f"local_exists={out['local_exists']} path={out['local_path']}")
        if not out["local_exists"]:
            print("HINT: file missing on this host — scp from peer or wait Obsidian Sync", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
