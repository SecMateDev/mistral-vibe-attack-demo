from __future__ import annotations

import unittest

from poc.collector import validate_event


class ValidateEventTests(unittest.TestCase):
    def test_accepts_masked_controlled_event(self) -> None:
        event = {
            "event": "host_compromised",
            "credential": "MISTRAL_API_KEY=********93a2",
            "credential_masked": True,
            "installed_path": "/tmp/demo/marker",
        }
        self.assertIs(validate_event(event), event)

    def test_rejects_unmasked_credential(self) -> None:
        with self.assertRaises(ValueError):
            validate_event(
                {
                    "event": "host_compromised",
                    "credential": "MISTRAL_API_KEY=demo_secret",
                    "credential_masked": False,
                    "installed_path": "/tmp/demo/marker",
                }
            )


if __name__ == "__main__":
    unittest.main()
