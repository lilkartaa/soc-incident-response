
import json
from pathlib import Path

from retrieval.search import get_alert_evidence


def generate_report(alert, evidence):
    usernames = alert["username"]
    source_ip = alert["source_ip"]
    failed_attempts = alert["failed_attempts"]

    evidence_ids = [
        record["event_id"] for record in evidence
    ]

    report = f"""
INCIDENT REPORT
===============

Alert Type: {alert['alert_type']}
Severity: {alert['severity']}

SUMMARY
-------
Detected {failed_attempts} failed login attempts
for user '{usernames}' from IP address {source_ip}.

EVIDENCE
--------
"""

    for record in evidence:
        report += (
            f"- {record['event_id']}: "
            f"{record['raw_line']}\n"
        )

    report += f"""
EVIDENCE VERIFICATION
---------------------
The alert references {len(evidence_ids)} retrieved
evidence records.

Evidence IDs: {', '.join(evidence_ids)}

ASSESSMENT
----------
The records support the claim that multiple failed
login attempts occurred for this user.

This activity is suspicious but does not, by itself,
prove that an account was compromised.

RECOMMENDED ACTIONS
-------------------
1. Review the user's subsequent login activity.
2. Check whether the source IP is expected.
3. Review access to sensitive resources.
4. Escalate to a security analyst for investigation.

"""

    return report


def main():
    with open("data/alerts.json", "r", encoding="utf-8") as file:
        alerts = json.load(file)

    alert = alerts[1]

    evidence = get_alert_evidence(alert)

    report = generate_report(alert, evidence)

    output_path = Path("data/incident_report.txt")
    output_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
