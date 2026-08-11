#!/usr/bin/env python3
"""Idempotently append the VibeCast Windows parity gate to the existing hook."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path


START = "# BEGIN GCS_VIBECAST_WINDOWS_PARITY_V1"
END = "# END GCS_VIBECAST_WINDOWS_PARITY_V1"
BLOCK = f'''\n{START}
PARITY="$ROOT/Games/WoW/wow-roster-tracker/scripts/pre_commit_windows_parity.py"
if [[ -f "$PARITY" ]]; then
  python3 "$PARITY"
fi
{END}
'''


def main() -> int:
    root = Path(
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    )
    hook = Path(
        subprocess.check_output(
            ["git", "rev-parse", "--git-path", "hooks/pre-commit"],
            cwd=root,
            text=True,
        ).strip()
    )
    text = hook.read_text(encoding="utf-8") if hook.is_file() else "#!/bin/zsh\nset -euo pipefail\nROOT=\"$(git rev-parse --show-toplevel)\"\n"
    if START not in text:
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(text.rstrip() + "\n" + BLOCK, encoding="utf-8")
    os.chmod(hook, 0o755)
    print(f"HOOK_INSTALLED {hook} marker={START}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
