import asyncio
import json
import time
import uuid

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent.agent import root_agent


APP_NAME = "ticket_triage"
USER_ID = "test_user"

RESULTS_FILE = "results/agent_results.json"


def load_existing_results():
    try:
        with open(RESULTS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_results(results):
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)


def is_rate_limit_error(error):
    error_text = str(error)

    return (
        "429" in error_text
        or "RESOURCE_EXHAUSTED" in error_text
        or "rate limit" in error_text.lower()
    )


async def run_agent(ticket):
    session_service = InMemorySessionService()

    session_id = str(uuid.uuid4())

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    prompt = f"""
Process this support ticket.

Ticket ID: {ticket["id"]}
Subject: {ticket["subject"]}
Description: {ticket["description"]}

Follow the ticket triage instructions.

Return the final result with:
- category
- confidence
- route
- draft response
"""

    content = types.Content(
        role="user",
        parts=[
            types.Part.from_text(text=prompt)
        ],
    )

    final_response = None

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content,
    ):

        if event.is_final_response():

            if event.content and event.content.parts:

                final_response = "\n".join(
                    part.text
                    for part in event.content.parts
                    if part.text
                )

    return final_response


async def main():

    with open("tickets.json") as f:
        tickets = json.load(f)

    results = load_existing_results()

    completed_ids = {
        result["ticket_id"]
        for result in results
    }

    print("================================")
    print("Ticket Triage Agent")
    print("================================")
    print(f"Total tickets: {len(tickets)}")
    print(f"Already completed: {len(completed_ids)}")
    print(
        f"Remaining: "
        f"{len(tickets) - len(completed_ids)}"
    )

    for ticket in tickets:

        ticket_id = ticket["id"]

        # Skip completed tickets.
        if ticket_id in completed_ids:

            print(
                f"\nSkipping ticket {ticket_id}: "
                f"{ticket['subject']} "
                f"(already completed)"
            )

            continue

        print("\n================================")
        print(
            f"Processing ticket {ticket_id}: "
            f"{ticket['subject']}"
        )
        print("================================")

        while True:

            try:

                start_time = time.time()

                response = await run_agent(ticket)

                latency = time.time() - start_time

                result = {
                    "ticket_id": ticket_id,
                    "subject": ticket["subject"],
                    "agent_response": response,
                    "latency_seconds": round(
                        latency,
                        2,
                    ),
                }

                results.append(result)

                save_results(results)

                print("\nAgent response:")
                print(response)

                print(
                    f"\nLatency: "
                    f"{result['latency_seconds']} seconds"
                )

                print("Saved successfully.")

                break

            except Exception as e:

                if is_rate_limit_error(e):

                    print("\nGemini rate limit reached.")
                    print(
                        "Waiting 50 seconds before retrying..."
                    )

                    await asyncio.sleep(50)

                else:

                    print(
                        f"\nError processing ticket "
                        f"{ticket_id}: {e}"
                    )

                    break

        # Small delay between tickets.
        await asyncio.sleep(5)

    print("\n================================")
    print("Agent processing completed")
    print("================================")
    print(f"Processed: {len(results)} tickets")
    print(f"Expected: {len(tickets)} tickets")
    print(
        f"Remaining: "
        f"{len(tickets) - len(results)}"
    )
    print(f"Results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    asyncio.run(main())