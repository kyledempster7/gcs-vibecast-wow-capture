#!/usr/bin/env python3
"""Bundled no-write advisor fixture for the VibeCast plugin contract."""
from __future__ import annotations

import argparse
import json


def advise(context: dict) -> dict:
    if context.get("schema") != "gcs_extension_context/v1":
        raise ValueError("context schema must be gcs_extension_context/v1")
    signals = context.get("signals") if isinstance(context.get("signals"), dict) else {}
    suggestions: list[str] = []
    if not signals.get("zone_hint"):
        suggestions.append("capture one readable zone-label frame")
    if float(signals.get("chat_ratio") or 0) > 0.5:
        suggestions.append("prefer gather or cinematic UI mode")
    if not suggestions:
        suggestions.append("retain current capture mix for human taste")
    return {
        "schema": "gcs_ai_suggestions/v1",
        "plugin": "local-ai-advisor",
        "suggestions": suggestions,
        "suggestion_only": True,
        "media_created": False,
        "may_publish": False,
        "provider_effects": False
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--context-json", required=True)
    args = ap.parse_args()
    print(json.dumps(advise(json.loads(args.context_json))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
