#!/usr/bin/env python3
"""Executable, fail-closed brand-pack and plugin surface for VibeCast."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


TRACKER = Path(__file__).resolve().parents[1]
EXTENSIONS = TRACKER / "extensions"
BRAND_PACKS = EXTENSIONS / "brand-packs"
PLUGINS = EXTENSIONS / "plugins"
PIPELINE_STAGES = (
    "soft_poll",
    "harvest",
    "score",
    "review",
    "archive_keep",
    "package_not_armed"
)


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object")
    return data


def validate_brand_pack(path: Path) -> dict:
    data = load_json(path)
    required = {
        "id",
        "brand_key",
        "game_key",
        "media_root_key",
        "product",
        "package_state",
        "allowed_hooks"
    }
    if data.get("schema") != "gcs_vibecast_brand_pack/v1":
        raise ValueError(f"{path}: unsupported brand-pack schema")
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"{path}: missing {missing}")
    if data.get("package_state") != "NOT_ARMED" or data.get("may_publish") is not False:
        raise ValueError(f"{path}: brand packs must be NOT_ARMED and may_publish=false")
    if not isinstance(data.get("allowed_hooks"), list):
        raise ValueError(f"{path}: allowed_hooks must be a list")
    return data


def validate_plugin(path: Path) -> dict:
    data = load_json(path)
    if data.get("schema") != "gcs_vibecast_plugin/v1":
        raise ValueError(f"{path}: unsupported plugin schema")
    capabilities = set(data.get("capabilities") or [])
    forbidden = set(data.get("forbidden_capabilities") or [])
    if capabilities != {"suggestion_only"}:
        raise ValueError(f"{path}: only suggestion_only plugins are admitted")
    if not {"invent_media", "publish", "arm", "provider_write"}.issubset(forbidden):
        raise ValueError(f"{path}: forbidden capabilities incomplete")
    hooks = data.get("hooks")
    if not isinstance(hooks, dict) or not hooks:
        raise ValueError(f"{path}: hooks missing")
    for hook_name, contract in hooks.items():
        if hook_name not in {"after_score", "after_review"} or not isinstance(contract, dict):
            raise ValueError(f"{path}: unsupported hook {hook_name}")
        entrypoint = (EXTENSIONS / str(contract.get("entrypoint") or "")).resolve()
        try:
            entrypoint.relative_to(EXTENSIONS.resolve())
        except ValueError as exc:
            raise ValueError(f"{path}: entrypoint escapes extension root") from exc
        if not entrypoint.is_file() or entrypoint.suffix != ".py":
            raise ValueError(f"{path}: invalid entrypoint {entrypoint}")
        if contract.get("input_schema") != "gcs_extension_context/v1":
            raise ValueError(f"{path}: invalid input schema")
        if not str(contract.get("output_schema") or "").startswith("gcs_"):
            raise ValueError(f"{path}: invalid output schema")
        timeout_s = int(contract.get("timeout_s") or 0)
        if timeout_s < 1 or timeout_s > 30:
            raise ValueError(f"{path}: timeout outside 1..30 seconds")
    return data


def registry() -> tuple[dict[str, dict], dict[str, dict]]:
    brands: dict[str, dict] = {}
    plugins: dict[str, dict] = {}
    for path in sorted(BRAND_PACKS.glob("*.json")):
        item = validate_brand_pack(path)
        if item["id"] in brands:
            raise ValueError(f"duplicate brand pack {item['id']}")
        brands[item["id"]] = item
    for path in sorted(PLUGINS.glob("*.json")):
        item = validate_plugin(path)
        if item["id"] in plugins:
            raise ValueError(f"duplicate plugin {item['id']}")
        plugins[item["id"]] = item
    if not brands or not plugins:
        raise ValueError("at least one brand pack and plugin are required")
    return brands, plugins


def portable_plan(brand_id: str) -> dict:
    brands, _ = registry()
    if brand_id not in brands:
        raise KeyError(f"unknown brand pack: {brand_id}")
    brand = brands[brand_id]
    return {
        "schema": "gcs_portable_pipeline_plan/v1",
        "brand_pack": brand_id,
        "brand_key": brand["brand_key"],
        "game_key": brand["game_key"],
        "media_root_key": brand["media_root_key"],
        "stages": list(PIPELINE_STAGES),
        "package_state": "NOT_ARMED",
        "may_publish": False,
        "provider_effects": False
    }


def run_hook(plugin_id: str, hook_name: str, context: dict) -> dict:
    _, plugins = registry()
    plugin = plugins.get(plugin_id)
    if plugin is None or plugin.get("enabled") is not True:
        raise KeyError(f"plugin unavailable: {plugin_id}")
    contract = (plugin.get("hooks") or {}).get(hook_name)
    if not isinstance(contract, dict):
        raise KeyError(f"hook unavailable: {plugin_id}:{hook_name}")
    if context.get("schema") != contract["input_schema"]:
        raise ValueError("context schema rejected")
    entrypoint = (EXTENSIONS / contract["entrypoint"]).resolve()
    result = subprocess.run(
        [sys.executable, str(entrypoint), "--context-json", json.dumps(context)],
        cwd=EXTENSIONS,
        capture_output=True,
        text=True,
        timeout=int(contract["timeout_s"]),
        check=False
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout)[-500:])
    output = json.loads(result.stdout)
    if output.get("schema") != contract["output_schema"]:
        raise ValueError("plugin output schema rejected")
    if output.get("suggestion_only") is not True or output.get("may_publish") is not False:
        raise ValueError("plugin output violated suggestion-only contract")
    return output


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    plan = sub.add_parser("plan")
    plan.add_argument("--brand", required=True)
    hook = sub.add_parser("run-hook")
    hook.add_argument("--plugin", required=True)
    hook.add_argument("--hook", required=True)
    hook.add_argument("--context-json", required=True)
    args = ap.parse_args()
    if args.command == "validate":
        brands, plugins = registry()
        print(json.dumps({
            "schema": "gcs_extension_registry_validation/v1",
            "status": "PASS",
            "brand_packs": sorted(brands),
            "plugins": sorted(plugins),
            "may_publish": False
        }, indent=2))
    elif args.command == "plan":
        print(json.dumps(portable_plan(args.brand), indent=2))
    else:
        print(json.dumps(
            run_hook(args.plugin, args.hook, json.loads(args.context_json)),
            indent=2
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
