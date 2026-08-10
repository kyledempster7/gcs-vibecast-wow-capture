#!/usr/bin/env python3
"""Local one-tap KEEP/REJECT for review-pack (localhost only). No publish.

Serves day review-pack/ with POST /verdict → record_feedback + human_verdicts.json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


SCRIPTS = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    day_dir: Path = Path(".")
    pack_dir: Path = Path(".")

    def translate_path(self, path: str) -> str:  # noqa: A003
        # serve from pack_dir
        from urllib.parse import unquote
        import os
        path = unquote(urlparse(path).path)
        if path.startswith("/"):
            path = path[1:]
        full = (self.pack_dir / path).resolve()
        if not str(full).startswith(str(self.pack_dir.resolve())):
            return str(self.pack_dir / "index.html")
        if full.is_dir():
            return str(full / "index.html") if (full / "index.html").is_file() else str(full)
        return str(full)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8") if length else ""
        ctype = self.headers.get("Content-Type") or ""
        data: dict = {}
        if "application/json" in ctype:
            try:
                data = json.loads(body or "{}")
            except json.JSONDecodeError:
                data = {}
        else:
            q = parse_qs(body)
            data = {k: (v[0] if v else "") for k, v in q.items()}

        cid = str(data.get("id") or "").strip()
        verdict = str(data.get("verdict") or "").strip().upper()
        note = str(data.get("note") or "one_tap_board")
        if verdict not in {"KEEP", "REJECT", "REVIEW", "PRIDE_PICK"} or not cid:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"ok":false,"error":"id+verdict required"}')
            return

        r = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "record_feedback.py"),
                "--day-dir",
                str(self.day_dir),
                "--id",
                cid,
                "--verdict",
                verdict,
                "--note",
                note,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        payload = {
            "ok": r.returncode == 0,
            "id": cid,
            "verdict": verdict,
            "stdout": (r.stdout or "").strip(),
            "stderr": (r.stderr or "").strip(),
        }
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(200 if payload["ok"] else 500)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def inject_buttons(index: Path) -> None:
    """Idempotent inject KEEP/REJECT buttons into review-pack index.html."""
    if not index.is_file():
        return
    html = index.read_text(encoding="utf-8")
    if "gcs-one-tap-verdict" in html:
        return
    js = """
<style>
.gcs-one-tap-verdict button { margin:4px 4px 0 0; padding:6px 10px; border-radius:6px; border:0; cursor:pointer; font-weight:600; }
.gcs-one-tap-verdict .keep { background:#2d6a4f; color:#fff; }
.gcs-one-tap-verdict .reject { background:#9b2226; color:#fff; }
.gcs-one-tap-verdict .msg { font-size:12px; color:#9bdeac; min-height:1em; }
</style>
<script>
async function gcsVerdict(id, verdict, el) {
  const msg = el.parentElement.querySelector('.msg');
  try {
    const r = await fetch('/verdict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({id, verdict, note: 'one_tap_board'})
    });
    const j = await r.json();
    msg.textContent = j.ok ? (verdict + ' saved') : ('err ' + (j.stderr||j.error||''));
  } catch (e) {
    msg.textContent = 'server offline — run review_pack_feedback_server.py';
  }
}
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.card').forEach(card => {
    const strong = card.querySelector('strong');
    if (!strong) return;
    let id = strong.textContent.trim().split('·')[0].trim();
    // pride ids keep full name; strip second-play suffix already via ·
    const box = document.createElement('div');
    box.className = 'gcs-one-tap-verdict';
    box.innerHTML = '<button class="keep" type="button">KEEP</button>'
      + '<button class="reject" type="button">REJECT</button>'
      + '<div class="msg"></div>';
    box.querySelector('.keep').onclick = (ev) => gcsVerdict(id, 'KEEP', ev.target);
    box.querySelector('.reject').onclick = (ev) => gcsVerdict(id, 'REJECT', ev.target);
    card.appendChild(box);
  });
});
</script>
"""
    if "</body>" in html:
        html = html.replace("</body>", js + "\n</body>")
    else:
        html += js
    index.write_text(html, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day-dir", type=Path, required=True)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--inject-only", action="store_true")
    args = ap.parse_args()
    day = args.day_dir.expanduser().resolve()
    pack = day / "review-pack"
    if not pack.is_dir():
        print(f"missing review-pack: {pack}", file=sys.stderr)
        return 2
    inject_buttons(pack / "index.html")
    if args.inject_only:
        print(f"INJECT_OK {pack / 'index.html'}")
        return 0
    Handler.day_dir = day
    Handler.pack_dir = pack
    # POST /verdict routing: override path
    class H(Handler):
        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path.rstrip("/") == "/verdict":
                return super().do_POST()
            self.send_response(404)
            self.end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), H)
    print(f"REVIEW_BOARD http://127.0.0.1:{args.port}/index.html day={day}")
    print("Ctrl-C to stop. No publish.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("stop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
