
from collections import defaultdict


def detect_suspicious_activity(records):

    failed_attempts = defaultdict(list)
    alerts = []

    for record in records:

        if record["event_type"] == "LOGIN_FAILED":
            failed_attempts[record["username"]].append(record)

    for username, events in failed_attempts.items():

        if len(events) >= 3:

            alerts.append({
                "username": username,
                "failed_attempts": len(events),
                "source_ip": events[0]["source_ip"],
                "severity": "HIGH",
                "alert_type": "POSSIBLE_BRUTE_FORCE",
                "evidence_ids": [
                    event["event_id"] for event in events
                ]
            })

    return alerts
