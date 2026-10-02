import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.5-flash-lite"


def draft_response(ticket, category, route):
    prompt = f"""
You are a customer support agent.

Write a concise and professional first-response to the customer.

Ticket:
Subject: {ticket["subject"]}
Description: {ticket["description"]}

Category: {category}
Assigned team: {route}

Requirements:
- Address the customer's issue directly.
- Be polite and helpful.
- Do not invent specific account information.
- Do not promise a specific resolution or timeframe.
- Ask for additional information only if necessary.
- Keep the response under 100 words.
- Return only the customer-facing response.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    return response.text.strip()
