import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_compliance(evidence: str) -> str:
    prompt = f"""
You are an enterprise procurement compliance analyst.

Analyze the following deterministic procurement evidence.

Do not invent facts.
Do not change numerical values.
Do not contradict the supplied evidence.

Provide your response using exactly these sections:

1. Compliance Summary
2. Key Violations
3. Financial Impact
4. Recommended Procurement Action
5. Reasoning

Procurement Evidence:
{evidence}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    return response.text