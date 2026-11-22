
import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


def generate_response(prompt, max_retries=4):
    for attempt in range(max_retries):
        try:
            response = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt
            )
            return response.output_text

        except Exception as error:
            message = str(error).lower()

            temporary_error = (
                "503" in message
                or "high demand" in message
                or "429" in message
                or "500" in message
            )

            if not temporary_error or attempt == max_retries - 1:
                raise

            wait_seconds = 5 * (2 ** attempt)
            print(
                f"Gemini is temporarily unavailable. "
                f"Retrying in {wait_seconds} seconds..."
            )
            time.sleep(wait_seconds)

    raise RuntimeError("Gemini request failed after retries.")


def analyze_incident(alert, evidence):
    evidence_text = "\n".join(
        record["raw_line"] for record in evidence
    )

    prompt = f"""
You are a cybersecurity SOC analyst.

Analyse the following security alert using ONLY the
provided evidence.

ALERT:
Username: {alert['username']}
Alert type: {alert['alert_type']}
Severity: {alert['severity']}
Failed attempts: {alert['failed_attempts']}
Source IP: {alert['source_ip']}

EVIDENCE:
{evidence_text}

Write an incident analysis containing:

1. Incident summary.
2. Observed suspicious behaviour.
3. Evidence supporting the findings.
4. What cannot be concluded from the evidence.
5. Recommended defensive actions.

RULES:
- Do not invent facts.
- Do not claim the account was compromised without evidence.
- Reference evidence using its event information.
- Clearly distinguish observations from assumptions.
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
    print(analyze_incident(alert, evidence))
