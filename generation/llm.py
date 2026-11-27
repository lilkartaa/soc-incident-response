import os
import time

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "openai/gpt-oss-20b"

_client = None


def get_client():
    """Create the Groq client only when first needed."""
    global _client

    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY not found. "
                "Add it to the project's .env file."
            )

        _client = Groq(
            api_key=api_key,
            timeout=60.0,
            max_retries=0
        )

    return _client


def generate_response(prompt, max_retries=3):
    """Send a prompt to Groq and return generated text."""

    client = get_client()

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a careful cybersecurity SOC analyst. "
                            "Use only supplied evidence for factual claims. "
                            "Distinguish observations from hypotheses. "
                            "Never invent evidence or event IDs."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=1500,
                temperature=0.2
            )

            content = response.choices[0].message.content

            if not content:
                raise RuntimeError("Groq returned an empty response.")

            return content.strip()

        except Exception as error:
            message = str(error).lower()

            temporary_error = any(
                term in message
                for term in (
                    "429",
                    "500",
                    "502",
                    "503",
                    "504",
                    "rate limit",
                    "timeout",
                    "temporarily unavailable"
                )
            )

            if not temporary_error or attempt == max_retries - 1:
                raise

            wait_seconds = 2 ** (attempt + 1)

            print(
                f"Groq temporarily unavailable. "
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError("Groq request failed after retries.")


def format_evidence(records):
    """Format evidence records, including optional retrieval scores."""

    formatted = []

    for item in records:
        score = None

        # Semantic search results have the form:
        # {"score": 0.8, "record": {...}}
        if isinstance(item, dict) and "record" in item:
            record = item["record"]
            score = item.get("score")
        else:
            record = item

        event_id = record.get("event_id", "UNKNOWN")
        raw_line = record.get("raw_line", "")

        if score is not None:
            formatted.append(
                f"{event_id} | Similarity score: {score:.3f} | "
                f"{raw_line}"
            )
        else:
            formatted.append(
                f"{event_id} | {raw_line}"
            )

    return "\n".join(formatted) if formatted else "No evidence provided."


def analyze_incident(alert, evidence, retrieved_evidence=None):
    """
    Generate an evidence-grounded incident analysis.

    evidence:
        Original evidence explicitly linked to the alert.

    retrieved_evidence:
        Additional context returned by semantic retrieval.
        Optional for backward compatibility.
    """

    if retrieved_evidence is None:
        retrieved_evidence = []

    linked_text = format_evidence(evidence)
    retrieved_text = format_evidence(retrieved_evidence)

    prompt = f"""
You are a cybersecurity SOC analyst.

Analyse the security alert using ONLY the supplied evidence.

ALERT DETAILS:
Username: {alert['username']}
Alert type: {alert['alert_type']}
Severity: {alert['severity']}
Failed attempts: {alert['failed_attempts']}
Source IP: {alert['source_ip']}

DETECTOR-LINKED EVIDENCE:
These records were explicitly associated with the alert by
the deterministic detection pipeline.

{linked_text}

ADDITIONAL SEMANTICALLY RETRIEVED CONTEXT:
These records were retrieved from the wider evidence corpus
using semantic similarity. They provide context but were
not necessarily used to trigger the alert.

{retrieved_text}

Write an incident analysis containing:

1. Incident summary.
2. Observed suspicious behaviour.
3. Evidence supporting the findings.
4. Relevant contextual activity and its significance.
5. What cannot be concluded from the evidence.
6. Recommended defensive actions.

EVIDENCE RULES:
- Use only the supplied evidence.
- Reference specific event IDs when making factual claims.
- Distinguish detector-linked evidence from retrieved context.
- Do not invent events, timestamps, users, IP addresses, or actions.
- Do not claim an account was compromised without sufficient evidence.
- Do not treat similarity scores as probabilities or confidence levels.
- Do not assume retrieved records are causally related merely
  because they have high similarity scores.
- The supplied IP addresses may be reserved documentation
  addresses. Do not treat them as confirmed real attackers.
- Recommendations must be advisory, not automatic actions.
"""

    return generate_response(prompt)


if __name__ == "__main__":
    import json
    from retrieval.search import get_alert_evidence

    with open("data/alerts.json", "r", encoding="utf-8") as file:
        alerts = json.load(file)

    alert = alerts[1]
    evidence = get_alert_evidence(alert)

    print("\nGENERATING INCIDENT ANALYSIS...\n")
