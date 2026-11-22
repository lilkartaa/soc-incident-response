

import json
from pathlib import Path

from generation.llm import analyze_incident
from retrieval.vector_store import semantic_search


def get_semantic_alert_evidence(alert):
    username = alert["username"]
    source_ip = alert["source_ip"]

    query = (
        f"Authentication activity and repeated failed login attempts "
        f"for user {username} from IP address {source_ip}"
    )

    # Retrieve the full current evidence corpus, then restrict it
    # to evidence explicitly associated with this alert.
    results = semantic_search(query, top_k=1000)

    allowed_ids = set(alert["evidence_ids"])

    ranked_evidence = [
        item
        for item in results
        if item["record"]["event_id"] in allowed_ids
    ]

    return [
        item["record"]
        for item in ranked_evidence
    ]


def main():
    alerts_path = Path("data/alerts.json")
    output_path = Path("data/llm_analysis.json")

    with alerts_path.open("r", encoding="utf-8") as file:
        alerts = json.load(file)

    results = []

    for alert in alerts:
        print(f"\nAnalyzing incident for: {alert['username']}")

        evidence = get_semantic_alert_evidence(alert)

        if not evidence:
            print("No evidence found. Skipping.")
            continue

        print(
            f"Retrieved {len(evidence)} semantically ranked "
            f"evidence records: "
            f"{', '.join(record['event_id'] for record in evidence)}"
        )

        analysis = analyze_incident(alert, evidence)

        results.append({
            "username": alert["username"],
            "alert_type": alert["alert_type"],
            "analysis": analysis,
            "evidence_ids": [
                record["event_id"] for record in evidence
            ]
        })

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print(f"\nCompleted analysis for {len(results)} incidents.")
    print(f"Saved results to {output_path}")


if __name__ == "__main__":
    main()
