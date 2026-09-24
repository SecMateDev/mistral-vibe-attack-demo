from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Any

MAX_BODY_BYTES = 64 * 1024
DASHBOARD = Path(__file__).with_name("dashboard.html").read_bytes()
EVENTS: list[dict[str, Any]] = []
EVENTS_LOCK = Lock()


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "SecMateDemo/1.0"

    def _write_json(self, value: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(DASHBOARD)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(DASHBOARD)
            return
        if self.path == "/api/events":
            with EVENTS_LOCK:
                events = list(EVENTS)
            self._write_json({"events": events})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path == "/api/reset":
            with EVENTS_LOCK:
                EVENTS.clear()
            self._write_json({"ok": True})
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
            event = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_error(HTTPStatus.BAD_REQUEST)
            return
        if not isinstance(event, dict) or event.get("event") != "host_compromised":
            self.send_error(HTTPStatus.BAD_REQUEST)
            return
        credential = event.get("credential")
        if (
            event.get("credential_masked") is not True
            or not isinstance(credential, str)
            or not credential.startswith("MISTRAL_API_KEY=")
            or "*" not in credential
        ):
            self.send_error(HTTPStatus.BAD_REQUEST)
            return

        event["received_at"] = datetime.now(UTC).isoformat()
        with EVENTS_LOCK:
            EVENTS.append(event)
        self._write_json({"ok": True}, HTTPStatus.CREATED)

    def log_message(self, format: str, *args: object) -> None:
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SecMate demo event dashboard")
    parser.add_argument("--listen", default="127.0.0.1")
    parser.add_argument("--port", default=8787, type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.listen, args.port), DemoHandler)
    print(f"SecMate attacker dashboard: http://{args.listen}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
