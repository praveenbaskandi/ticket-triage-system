import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.5-flash-lite"


def classify_ticket(ticket):
    prompt = f"""
You are a support ticket classifier.

Classify the following ticket into exactly ONE of these categories:

- billing
- authentication
- technical
- account
- subscription

Ticket:
Subject: {ticket["subject"]}
Description: {ticket["description"]}

Return ONLY valid JSON in this exact format:

{{
  "category": "one_category",
  "confidence": 0.0
}}

The confidence must be a number between 0 and 1.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )


    result = json.loads(response.text)

    return result
