#!/usr/bin/env python3
"""Original, dependency-free training service. Use only with synthetic data."""

import json
import os
from pathlib import Path
import signal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


def response_for(path: str, data_dir: Path) -> tuple[int, dict]:
    """Keep route behavior testable without opening a network listener."""
    if path == "/healthz":
        return 200, {"status": "alive"}
    if path == "/readyz":
        ready = data_dir.is_dir() and not (data_dir / "maintenance").exists()
        return (200 if ready else 503), {"status": "ready" if ready else "not-ready"}
    if path in ("/", "/version"):
        return 200, {
            "service": "onboarding-status",
            "version": os.environ.get("APP_VERSION", "1.0.0"),
            "environment": os.environ.get("APP_ENV", "sandbox"),
            "message": os.environ.get("MESSAGE", "Hello from a disposable training environment."),
        }
    if path == "/note":
        note = data_dir / "note.txt"
        try:
            value = note.read_text(encoding="utf-8") if note.exists() else "No synthetic note yet."
        except OSError:
            return 503, {"error": "note-unavailable"}
        return 200, {"note": value}
    return 404, {"error": "not-found"}


def make_handler(data_dir: Path):
    class Handler(BaseHTTPRequestHandler):
        server_version = "OnboardingStatus/1"
        sys_version = ""

        def do_GET(self):
            self.respond(send_body=True)

        def do_HEAD(self):
            self.respond(send_body=False)

        def respond(self, send_body: bool):
            status, document = response_for(urlsplit(self.path).path, data_dir)
            payload = (json.dumps(document, sort_keys=True) + "\n").encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if send_body:
                self.wfile.write(payload)

        def log_request(self, code="-", size="-"):
            # Do not log headers, bodies, credentials, or query strings.
            print(json.dumps({"method": self.command, "path": urlsplit(self.path).path,
                              "status": code}), flush=True)

    return Handler


def main():
    data_dir = Path(os.environ.get("DATA_DIR", "/tmp/onboarding-status"))
    host = os.environ.get("BIND_HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "18080"))
    signal.signal(signal.SIGTERM, lambda *_: raise_exit())
    with ThreadingHTTPServer((host, port), make_handler(data_dir)) as server:
        print(json.dumps({"event": "listening", "host": host, "port": port}), flush=True)
        server.serve_forever(poll_interval=0.2)


def raise_exit():
    raise SystemExit(0)


if __name__ == "__main__":
    main()
