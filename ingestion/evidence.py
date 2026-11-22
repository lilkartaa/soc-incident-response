
import hashlib
import json
from pathlib import Path

from ingestion.parser import parse_logs


def sha256_file(file_path):
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            digest.update(chunk)

    return digest.hexdigest()


def build_evidence_store():
    log_path = Path("data/raw/auth.log")
    records = parse_logs(log_path)

    evidence = {
        "source_file": str(log_path),
        "sha256": sha256_file(log_path),
        "records": records
    }

    output_path = Path("data/evidence.json")

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(evidence, file, indent=4)

    print(f"Stored {len(records)} evidence records.")
    print(f"SHA-256: {evidence['sha256']}")
    print(f"Saved evidence to {output_path}")


if __name__ == "__main__":
    build_evidence_store()
