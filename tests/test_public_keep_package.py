#!/usr/bin/env python3
"""Drive real shipped public package + sample media (no invent, no hardcoded green)."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "samples" / "keep-2026-08-09"
PKG_PATH = SAMPLE_DIR / "PRODUCT_PACKAGE.json"
VIDEO = SAMPLE_DIR / "c-pride-15s-start-vertical.mp4"
STILL = SAMPLE_DIR / "still-WoWScrnShot.jpg"


class PublicKeepPackage(unittest.TestCase):
    def test_package_json_product_ready_with_real_files(self) -> None:
        self.assertTrue(PKG_PATH.is_file(), f"missing {PKG_PATH}")
        pkg = json.loads(PKG_PATH.read_text(encoding="utf-8"))
        self.assertTrue(pkg.get("product_ready") is True)
        self.assertEqual(pkg.get("status"), "NOT_ARMED")
        self.assertFalse(pkg.get("kyle_go"))
        self.assertFalse(pkg.get("publishNow"))
        media = pkg.get("media") or []
        self.assertGreaterEqual(len(media), 1)
        found_existing = 0
        for m in media:
            rel = m.get("path")
            self.assertTrue(rel, m)
            p = ROOT / rel
            self.assertTrue(p.is_file(), f"media missing on disk: {p}")
            self.assertGreater(p.stat().st_size, 1000)
            self.assertTrue(m.get("exists") is True)
            # sha must match real file if provided
            if m.get("sha256"):
                import hashlib

                h = hashlib.sha256()
                with p.open("rb") as f:
                    for chunk in iter(lambda: f.read(1 << 20), b""):
                        h.update(chunk)
                self.assertEqual(m["sha256"], h.hexdigest(), rel)
            found_existing += 1
        self.assertGreaterEqual(found_existing, 1)

    def test_keep_sample_video_is_real_mp4(self) -> None:
        self.assertTrue(VIDEO.is_file())
        self.assertGreater(VIDEO.stat().st_size, 100_000)
        head = VIDEO.read_bytes()[:12]
        # ISO BMFF / ftyp
        self.assertIn(b"ftyp", head[4:12] if len(head) >= 12 else head)

    def test_readme_states_laws(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for needle in (
            "VibeCast",
            "No invent FOOTAGE",
            "No silent publish",
            "Human KEEP",
            "ARM default deny",
            "samples/keep-2026-08-09",
        ):
            self.assertIn(needle, readme)


if __name__ == "__main__":
    # Also exercise archive_keep load_verdicts if present in scripts/
    scripts = ROOT / "scripts" / "archive_keep_to_moments.py"
    if scripts.is_file():
        import importlib.util

        spec = importlib.util.spec_from_file_location("archive_keep_to_moments", scripts)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        # synthetic envelope like production
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            day = Path(td)
            (day / "analysis").mkdir()
            (day / "analysis" / "human_verdicts.json").write_text(
                json.dumps(
                    {
                        "schema": "gcs_human_verdicts/v1",
                        "verdicts": {
                            "c": {"verdict": "KEEP", "reason": "t"},
                            "a": {"verdict": "REJECT", "reason": "t"},
                        },
                    }
                ),
                encoding="utf-8",
            )
            v = mod.load_verdicts(day)
            assert "c" in v and v["c"]["verdict"] == "KEEP"
            assert "schema" not in v
            print("LOAD_VERDICTS_SHIPPED_OK")

    r = unittest.main(verbosity=2, exit=False)
    sys.exit(0 if r.result.wasSuccessful() else 1)
