#!/usr/bin/env python3
"""In-memory loopback receiver for the controlled Mistral Vibe PoC."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from typing import Any

MAX_BODY_BYTES = 16 * 1024
EVENTS: list[dict[str, Any]] = []
EVENTS_LOCK = Lock()


def validate_event(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("event") != "host_compromised":
        raise ValueError("unexpected event")
    credential = value.get("credential")
    if (
        value.get("credential_masked") is not True
        or not isinstance(credential, str)
        or not credential.startswith("MISTRAL_API_KEY=")
        or "*" not in credential
    ):
        raise ValueError("credential must be masked")
    if not isinstance(value.get("installed_path"), str):
        raise TypeError("installed_path must be a string")
    return value


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "SecMatePoC/1.0"

    def _json(self, value: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/api/events":
            with EVENTS_LOCK:
                events = list(EVENTS)
            self._json({"events": events})
            return
        if self.path == "/":
            body = (
                b"<!doctype html><meta charset=utf-8>"
                b"<title>SecMate Vibe PoC</title>"
                b"<h1>SecMate Vibe PoC receiver</h1>"
                b"<p>Events are available at <a href=/api/events>/api/events</a>.</p>"
            )
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path == "/api/reset":
            with EVENTS_LOCK:
                EVENTS.clear()
            self._json({"ok": True})
            return
        if self.path != "/api/events":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return
        if not 0 < length <= MAX_BODY_BYTES:
            self.send_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        try:
            event = validate_event(json.loads(self.rfile.read(length)))
        except (json.JSONDecodeError, TypeError, UnicodeDecodeError, ValueError):
            self.send_error(HTTPStatus.BAD_REQUEST)
            return
        with EVENTS_LOCK:
            EVENTS.append(event)
        self._json({"ok": True}, HTTPStatus.CREATED)

    def log_message(self, format: str, *args: object) -> None:
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8787)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), DemoHandler)
    print(f"PoC receiver: http://127.0.0.1:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
