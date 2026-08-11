#!/usr/bin/env python3
"""Resolve VibeCast machine paths from the versioned media-roots contract."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


WOW = Path(__file__).resolve().parents[2]
CONFIG = WOW / "00-Index" / "media_roots.json"


def load_config(path: Path = CONFIG) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "gcs_media_roots/v2" or int(data.get("version") or 0) < 2:
        raise ValueError(f"unsupported media-roots contract: {path}")
    windows = data.get("windows")
    mac = data.get("mac")
    if not isinstance(windows, dict) or not isinstance(mac, dict):
        raise ValueError("media-roots requires windows and mac objects")
    ssh = str(windows.get("ssh") or "").strip()
    if "@" not in ssh or any(char.isspace() for char in ssh):
        raise ValueError("windows.ssh must be a user@host token")
    return data


def ssh_host(path: Path = CONFIG) -> str:
    override = os.environ.get("WINDOWS_SSH_HOST", "").strip()
    if override:
        return override
    return str(load_config(path)["windows"]["ssh"])


def drive_offload(path: Path = CONFIG) -> str:
    override = os.environ.get("GCS_VIBECAST_DRIVE", "").strip()
    if override:
        return override
    return str(load_config(path)["mac"]["google_drive_offload"])


def main() -> int:
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--ssh", action="store_true")
    group.add_argument("--tailscale-ip", action="store_true")
    group.add_argument("--host-hints", action="store_true")
    group.add_argument("--drive-offload", action="store_true")
    group.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    data = load_config()
    if args.ssh:
        print(ssh_host())
    elif args.tailscale_ip:
        print(data["windows"]["tailscale_ip"])
    elif args.host_hints:
        print("\n".join(data["windows"].get("host_hints") or []))
    elif args.drive_offload:
        print(drive_offload())
    else:
        print(f"CONFIG_OK schema={data['schema']} version={data['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
