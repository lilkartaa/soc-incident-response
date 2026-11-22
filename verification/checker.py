
import json
from pathlib import Path

from retrieval.search import get_alert_evidence


def verify_claims(alert, evidence):
    evidence_ids = {
        record["event_id"] for record in evidence
    }

    verified_claims = []

    # Claim 1: Failed login attempts occurred.
    if len(evidence_ids) >= alert["failed_attempts"]:
        failed_login_status = "SUPPORTED"
    elif evidence_ids:
        failed_login_status = "PARTIALLY_SUPPORTED"
    else:
        failed_login_status = "UNSUPPORTED"

    verified_claims.append({
        "claim": (
            f"{alert['failed_attempts']} failed login "
            f"attempts occurred for {alert['username']}."
        ),
        "status": failed_login_status,
        "evidence_ids": sorted(evidence_ids)
    })

    # Claim 2: Activity originated from the reported IP.
    matching_ip = [
        record for record in evidence
        if record["source_ip"] == alert["source_ip"]
    ]

    if matching_ip:
        ip_status = "SUPPORTED"
    else:
        ip_status = "UNSUPPORTED"

    verified_claims.append({
        "claim": (
            f"Activity originated from {alert['source_ip']}."
        ),
        "status": ip_status,
        "evidence_ids": [
            record["event_id"] for record in matching_ip
        ]
    })

    # Claim 3: The account was compromised.
    # Failed login records alone cannot establish compromise.
    verified_claims.append({
        "claim": (
            f"The account {alert['username']} was compromised."
        ),
        "status": "UNSUPPORTED",
        "evidence_ids": []
    })

    return verified_claims


def main():
    input_path = Path("data/alerts.json")

    with input_path.open("r", encoding="utf-8") as file:
        alerts = json.load(file)

    all_results = []

    for alert in alerts:
        evidence = get_alert_evidence(alert)
        claims = verify_claims(alert, evidence)

        all_results.append({
            "alert": alert,
            "verified_claims": claims
        })

    output_path = Path("data/verification.json")

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(all_results, file, indent=4)

    print(f"Verified claims for {len(all_results)} alerts.")
    print(f"Saved results to {output_path}")


if __name__ == "__main__":
    main()
