#!/usr/bin/env python3
"""Loopback E2E proof for review-pack one-tap feedback.

Uses an isolated temporary day directory. It never changes real candidate
verdicts, never opens a browser, and has no publish/provider path.
"""
from __future__ import annotations

import http.client
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlparse

from review_pack_feedback_server import Handler


SCRIPTS = Path(__file__).resolve().parent
RECEIPT = (
    Path.home()
    / "Library/Application Support/UAH/butler/control-plane/receipts/gcs-vibecast"
    / "REVIEW_FEEDBACK_SERVER_TEST_LATEST.json"
)


class TestHandler(Handler):
    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path.rstrip("/") == "/verdict":
            return super().do_POST()
        self.send_response(404)
        self.end_headers()


def request(
    port: int,
    method: str,
    path: str,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, bytes]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request(method, path, body=body, headers=headers or {})
    response = conn.getresponse()
    raw = response.read()
    status = response.status
    conn.close()
    return status, raw


def main() -> int:
    checks: list[str] = []
    with TemporaryDirectory(prefix="gcs-review-feedback-") as td:
        root = Path(td)
        day = root / "returner-daily-test"
        pack = day / "review-pack"
        analysis = day / "analysis"
        sibling = day / "review-pack-private"
        pack.mkdir(parents=True)
        analysis.mkdir(parents=True)
        sibling.mkdir(parents=True)
        (pack / "index.html").write_text("<html>review fixture</html>\n", encoding="utf-8")
        (sibling / "secret.txt").write_text("DO_NOT_SERVE\n", encoding="utf-8")
        verdicts = analysis / "human_verdicts.json"
        verdicts.write_text(
            json.dumps(
                {
                    "schema": "gcs_human_verdicts/v1",
                    "verdicts": {
                        "existing-id": {
                            "verdict": "KEEP",
                            "reason": "fixture",
                            "source": "test",
                        }
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        TestHandler.day_dir = day
        TestHandler.pack_dir = pack
        server = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
        port = int(server.server_address[1])
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, raw = request(port, "GET", "/index.html")
            assert status == 200 and b"review fixture" in raw, (status, raw)
            checks.append("GET_INDEX_200")

            status, raw = request(port, "GET", "/healthz")
            health = json.loads(raw)
            assert status == 200 and health.get("ok") is True, (status, health)
            assert health.get("may_publish") is False
            checks.append("GET_HEALTH_200")

            status, raw = request(
                port,
                "GET",
                "/%2e%2e/review-pack-private/secret.txt",
            )
            assert b"DO_NOT_SERVE" not in raw, (status, raw)
            checks.append("TRAVERSAL_DENIED")

            invalid = json.dumps({"id": "new-id", "verdict": "PUBLISH"}).encode()
            status, _ = request(
                port,
                "POST",
                "/verdict",
                invalid,
                {"Content-Type": "application/json"},
            )
            assert status == 400
            checks.append("INVALID_VERDICT_400")

            payload = json.dumps(
                {"id": "new-id", "verdict": "REJECT", "note": "fixture_e2e"}
            ).encode()
            status, raw = request(
                port,
                "POST",
                "/verdict",
                payload,
                {"Content-Type": "application/json"},
            )
            response = json.loads(raw)
            assert status == 200 and response.get("ok") is True, (status, response)
            checks.append("POST_VERDICT_200")

            after = json.loads(verdicts.read_text(encoding="utf-8"))
            assert after["verdicts"]["existing-id"]["verdict"] == "KEEP"
            assert after["verdicts"]["new-id"]["verdict"] == "REJECT"
            checks.append("MERGE_PRESERVES_EXISTING")

            def concurrent_post(index: int) -> tuple[int, dict]:
                item = json.dumps(
                    {
                        "id": f"concurrent-{index:02d}",
                        "verdict": "KEEP" if index % 2 == 0 else "REJECT",
                        "note": f"concurrency_fixture_{index}",
                    }
                ).encode()
                code, response_raw = request(
                    port,
                    "POST",
                    "/verdict",
                    item,
                    {"Content-Type": "application/json"},
                )
                return code, json.loads(response_raw)

            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(concurrent_post, range(16)))
            assert all(code == 200 and payload.get("ok") is True for code, payload in results)
            concurrent_after = json.loads(verdicts.read_text(encoding="utf-8"))
            assert all(
                f"concurrent-{index:02d}" in concurrent_after["verdicts"]
                for index in range(16)
            )
            checks.append("CONCURRENT_POSTS_PRESERVED")
            assert concurrent_after.get("schema") == "gcs_human_verdicts/v1"
            assert isinstance(concurrent_after.get("updated_at_utc"), str)
            checks.append("ATOMIC_JSON_VALID")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    body = {
        "schema": "gcs_review_feedback_server_test/v1",
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "PASS",
        "checks": checks,
        "source": str(SCRIPTS / "review_pack_feedback_server.py"),
        "test": str(Path(__file__).resolve()),
        "real_verdicts_touched": False,
        "may_publish": False,
        "provider_effects": False,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    print("ALL_PASS", " ".join(checks))
    print(f"RECEIPT {RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
