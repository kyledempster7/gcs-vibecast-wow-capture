#!/usr/bin/env python3
"""Assert this process is not about to write Factory / Social-Workflow paths.

Exit 0 OK, 2 fence violation. Call from harvest/post_play.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HOME = Path.home()
FORBIDDEN_PREFIXES = [
    HOME / ".codex" / "saturday-fleet-readiness",
    HOME / "Movies" / "WoW-Social-Workflow",
]


def main() -> int:
    # Check cwd and any GCS_WRITE_TARGET env
    suspects = [Path.cwd().resolve()]
    env_t = os.environ.get("GCS_WRITE_TARGET")
    if env_t:
        suspects.append(Path(env_t).expanduser().resolve())
    for arg in sys.argv[1:]:
        if arg.startswith("-"):
            continue
        p = Path(arg).expanduser()
        if p.exists() or str(p).startswith(str(HOME)):
            try:
                suspects.append(p.resolve())
            except OSError:
                suspects.append(p)

    violations = []
    for s in suspects:
        for ban in FORBIDDEN_PREFIXES:
            try:
                s.relative_to(ban.resolve())
                violations.append(str(s))
            except (ValueError, OSError):
                # also string prefix for non-existing
                if str(s).startswith(str(ban)):
                    violations.append(str(s))

    if violations:
        print("FENCE_VIOLATION VibeCast must not write Factory paths:", *violations, sep="\n  ")
        return 2
    print("FENCE_OK vibecast_write_surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
