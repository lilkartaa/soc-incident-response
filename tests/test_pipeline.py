

import tempfile
import unittest
from pathlib import Path

from ingestion.parser import parse_logs
from ingestion.detector import detect_suspicious_activity
from verification.checker import verify_claims


class TestLogParser(unittest.TestCase):

    def test_parses_valid_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "auth.log"
            path.write_text(
                "2026-11-22T10:01:12 alice LOGIN_FAILED 192.0.2.50 -\n",
                encoding="utf-8"
            )

            records = parse_logs(path)

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["event_id"], "EVT001")
            self.assertEqual(records[0]["username"], "alice")
            self.assertIsNone(records[0]["resource"])

    def test_skips_blank_and_malformed_lines(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "auth.log"
            path.write_text(
                "\nmalformed log line\n"
                "2026-11-22T10:01:12 alice LOGIN_FAILED 192.0.2.50 -\n",
                encoding="utf-8"
            )

            records = parse_logs(path)

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["event_id"], "EVT001")


class TestAlertDetector(unittest.TestCase):

    def make_record(self, event_id, username, event_type, source_ip):
        return {
            "event_id": event_id,
            "username": username,
            "event_type": event_type,
            "source_ip": source_ip
        }

    def test_detects_three_failed_attempts(self):
        records = [
            self.make_record("EVT001", "alice", "LOGIN_FAILED", "192.0.2.50"),
            self.make_record("EVT002", "alice", "LOGIN_FAILED", "192.0.2.50"),
            self.make_record("EVT003", "alice", "LOGIN_FAILED", "192.0.2.50")
        ]

        alerts = detect_suspicious_activity(records)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["failed_attempts"], 3)

    def test_ignores_two_failed_attempts(self):
        records = [
            self.make_record("EVT001", "alice", "LOGIN_FAILED", "192.0.2.50"),
            self.make_record("EVT002", "alice", "LOGIN_FAILED", "192.0.2.50")
        ]

        self.assertEqual(detect_suspicious_activity(records), [])

    def test_ignores_successful_logins(self):
        records = [
            self.make_record("EVT001", "alice", "LOGIN_SUCCESS", "192.0.2.50"),
            self.make_record("EVT002", "alice", "LOGIN_SUCCESS", "192.0.2.50"),
            self.make_record("EVT003", "alice", "LOGIN_SUCCESS", "192.0.2.50")
        ]

        self.assertEqual(detect_suspicious_activity(records), [])


class TestClaimVerification(unittest.TestCase):

    def setUp(self):
        self.alert = {
            "username": "alice",
            "failed_attempts": 3,
            "source_ip": "192.0.2.50"
        }

        self.evidence = [
            {"event_id": "EVT001", "source_ip": "192.0.2.50"},
            {"event_id": "EVT002", "source_ip": "192.0.2.50"},
            {"event_id": "EVT003", "source_ip": "192.0.2.50"}
        ]

    def test_all_failed_attempts_are_supported(self):
        claims = verify_claims(self.alert, self.evidence)

        self.assertEqual(claims[0]["status"], "SUPPORTED")
        self.assertEqual(claims[0]["evidence_ids"], [
            "EVT001", "EVT002", "EVT003"
        ])

    def test_partial_evidence_is_partially_supported(self):
        claims = verify_claims(self.alert, self.evidence[:1])

        self.assertEqual(claims[0]["status"], "PARTIALLY_SUPPORTED")

    def test_missing_evidence_is_unsupported(self):
        claims = verify_claims(self.alert, [])

        self.assertEqual(claims[0]["status"], "UNSUPPORTED")
        self.assertEqual(claims[1]["status"], "UNSUPPORTED")

    def test_mismatched_ip_is_unsupported(self):
        evidence = [
            {"event_id": "EVT001", "source_ip": "198.51.100.20"}
        ]

        claims = verify_claims(self.alert, evidence)

        self.assertEqual(claims[1]["status"], "UNSUPPORTED")

    def test_compromise_claim_is_not_assumed(self):
        claims = verify_claims(self.alert, self.evidence)

        self.assertEqual(claims[2]["status"], "UNSUPPORTED")
        self.assertEqual(claims[2]["evidence_ids"], [])


if __name__ == "__main__":
    unittest.main()
