
import json
from pathlib import Path

from ingestion.parser import parse_logs
from ingestion.detector import detect_suspicious_activity


def run_pipeline():
    records = parse_logs("data/raw/auth.log")
    alerts = detect_suspicious_activity(records)

    output_path = Path("data/alerts.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(alerts, file, indent=4)

    print(f"Processed {len(records)} log records.")
    print(f"Detected {len(alerts)} alerts.")
    print(f"Saved alerts to {output_path}")


if __name__ == "__main__":
    run_pipeline()
