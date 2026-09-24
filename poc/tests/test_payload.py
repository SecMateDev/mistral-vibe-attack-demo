from __future__ import annotations

import json
import os
import types
import unittest
from contextlib import AbstractContextManager
from importlib.machinery import SourceFileLoader
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Self
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[2]
PAYLOAD = REPOSITORY / ".ci/bin/cat"


def load_payload() -> types.ModuleType:
    module = types.ModuleType("secmate_demo_payload")
    module.__file__ = str(PAYLOAD)
    SourceFileLoader(module.__name__, str(PAYLOAD)).exec_module(module)
    return module


class Response(AbstractContextManager["Response"]):
    def __enter__(self) -> Self:
        return self

    def read(self) -> bytes:
        return b'{"ok":true}'

    def __exit__(self, *args: object) -> bool:
        return False


class PayloadTests(unittest.TestCase):
    def test_unarmed_payload_has_no_side_effect(self) -> None:
        module = load_payload()
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(module._send_controlled_callback())

    def test_collector_must_be_loopback(self) -> None:
        module = load_payload()
        self.assertTrue(module._collector_is_loopback("http://localhost:8787"))
        self.assertTrue(module._collector_is_loopback("http://127.0.0.1:8787"))
        self.assertTrue(module._collector_is_loopback("http://[::1]:8787"))
        self.assertFalse(module._collector_is_loopback("https://127.0.0.1:8787"))
        self.assertFalse(module._collector_is_loopback("http://192.168.1.2:8787"))
        self.assertFalse(module._collector_is_loopback("http://example.com"))

    def test_callback_masks_demo_token_and_creates_marker(self) -> None:
        module = load_payload()
        captured: dict[str, object] = {}

        def fake_urlopen(request: object, timeout: int) -> Response:
            captured["url"] = request.full_url
            captured["body"] = json.loads(request.data)
            captured["timeout"] = timeout
            return Response()

        with TemporaryDirectory() as temp:
            root = Path(temp)
            secret = root / "credentials.env"
            secret.write_text("MISTRAL_API_KEY=demo_mistral_fixture_7f93a2\n")
            install = root / "installed"
            environment = {
                "SECMATE_DEMO_ARMED": module.ARM_VALUE,
                "SECMATE_DEMO_COLLECTOR": "http://127.0.0.1:8787",
                "SECMATE_DEMO_SECRET_FILE": str(secret),
                "SECMATE_DEMO_INSTALL_DIR": str(install),
            }
            with patch.dict(os.environ, environment, clear=True):
                module.urlopen = fake_urlopen
                self.assertTrue(module._send_controlled_callback())

            marker = install / "secmate-demo-agent"
            self.assertEqual(marker.read_bytes(), PAYLOAD.read_bytes())
            body = captured["body"]
            self.assertTrue(body["credential_masked"])
            self.assertTrue(body["credential"].endswith("93a2"))
            self.assertNotIn("demo_mistral_fixture_7f93a2", json.dumps(body))

    def test_rejects_non_demo_token(self) -> None:
        module = load_payload()
        with TemporaryDirectory() as temp:
            root = Path(temp)
            secret = root / "credentials.env"
            secret.write_text("MISTRAL_API_KEY=real-looking-secret\n")
            environment = {
                "SECMATE_DEMO_ARMED": module.ARM_VALUE,
                "SECMATE_DEMO_COLLECTOR": "http://127.0.0.1:8787",
                "SECMATE_DEMO_SECRET_FILE": str(secret),
                "SECMATE_DEMO_INSTALL_DIR": str(root / "installed"),
            }
            with (
                patch.dict(os.environ, environment, clear=True),
                self.assertRaises(ValueError),
            ):
                module._send_controlled_callback()

    def test_status_file_records_result(self) -> None:
        module = load_payload()
        with TemporaryDirectory() as temp:
            status = Path(temp) / "status.txt"
            with patch.dict(
                os.environ, {"SECMATE_DEMO_STATUS_FILE": str(status)}, clear=True
            ):
                module._write_status("callback_sent")
            self.assertEqual(status.read_text(), "callback_sent\n")


if __name__ == "__main__":
    unittest.main()
