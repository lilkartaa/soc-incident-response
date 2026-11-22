
import json
from pathlib import Path


def load_evidence():
    path = Path("data/evidence.json")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)["records"]


def search_evidence(query, limit=5):
    records = load_evidence()
    query_terms = query.lower().split()

    results = []

    for record in records:
        searchable_text = record["raw_line"].lower()

        score = sum(
            1 for term in query_terms
            if term in searchable_text
        )

        if score > 0:
            results.append((score, record))

    results.sort(key=lambda item: item[0], reverse=True)

    return [record for score, record in results[:limit]]


def get_alert_evidence(alert):
    """
    Retrieve the exact evidence records associated with an alert.
    """
    query = f"{alert['username']} LOGIN_FAILED"

    # Retrieve potentially relevant records.
    results = search_evidence(query, limit=10)

    # Keep only records explicitly linked to this alert.
    required_ids = set(alert["evidence_ids"])

    return [
        record for record in results
        if record["event_id"] in required_ids
    ]


if __name__ == "__main__":
    with open("data/alerts.json", "r", encoding="utf-8") as file:
        alerts = json.load(file)

    # Investigate the admin alert.
    alert = alerts[1]

    print(f"\nInvestigating: {alert['username']}")
    print(f"Alert type: {alert['alert_type']}")
    print(f"Severity: {alert['severity']}")
    print("\nRetrieved evidence:")

    evidence = get_alert_evidence(alert)

    for record in evidence:
        print(f"{record['event_id']} | {record['raw_line']}")

    print(f"\nTotal evidence records: {len(evidence)}")
