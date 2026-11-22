
from pathlib import Path


def parse_logs(file_path):
    """
    Read raw authentication logs and convert
    each line into a structured dictionary.
    """

    records = []

    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:

        for line_number, line in enumerate(file, start=1):

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) != 5:
                print(f"Skipping malformed line: {line_number}")
                continue

            timestamp, username, event_type, source_ip, resource = parts

            record = {
                "event_id": f"EVT{len(records) + 1:03d}",
                "timestamp": timestamp,
                "username": username,
                "event_type": event_type,
                "source_ip": source_ip,
                "resource": None if resource == "-" else resource,
                "raw_line": line
            }

            records.append(record)

    return records
