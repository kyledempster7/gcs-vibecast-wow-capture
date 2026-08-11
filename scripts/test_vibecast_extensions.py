#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from vibecast_extensions import EXTENSIONS, portable_plan, registry, run_hook


RECEIPT = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast"
    / "EXTENSION_SURFACE_LATEST.json"
)


def extension_snapshot() -> dict[str, str]:
    return {
        str(path.relative_to(EXTENSIONS)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(EXTENSIONS.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def main() -> int:
    checks: list[str] = []
    brands, plugins = registry()
    assert set(brands) == {"twe-wow", "tde-default", "tfe-default"}
    assert set(plugins) == {"local-ai-advisor"}
    checks.append("REGISTRY_VALID")

    tde = portable_plan("tde-default")
    tfe = portable_plan("tfe-default")
    assert tde["stages"] == tfe["stages"]
    assert tde["brand_key"] != tfe["brand_key"]
    assert tde["package_state"] == tfe["package_state"] == "NOT_ARMED"
    assert tde["may_publish"] is tfe["may_publish"] is False
    checks.append("TDE_TFE_PORTABLE_PLAN")

    context = {
        "schema": "gcs_extension_context/v1",
        "day": "fixture",
        "signals": {"zone_hint": None, "chat_ratio": 0.75}
    }
    before = extension_snapshot()
    output = run_hook("local-ai-advisor", "after_score", context)
    after = extension_snapshot()
    assert before == after
    assert output["schema"] == "gcs_ai_suggestions/v1"
    assert output["suggestion_only"] is True
    assert output["media_created"] is False
    assert output["may_publish"] is False
    assert output["provider_effects"] is False
    checks.append("AI_SUGGESTION_ONLY")

    body = {
        "schema": "gcs_extension_surface_test/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "checks": checks,
        "brand_packs": sorted(brands),
        "plugins": sorted(plugins),
        "tde_tfe_runtime_media_e2e": False,
        "may_publish": False,
        "provider_effects": False
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    print("ALL_PASS", " ".join(checks))
    print(f"RECEIPT {RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
