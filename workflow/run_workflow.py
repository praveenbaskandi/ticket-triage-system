import json
import time

from workflow.classifier import classify_ticket
from workflow.router import route_ticket
from workflow.drafter import draft_response


RESULTS_FILE = "results/workflow_results.json"


def process_ticket(ticket):
    # Step 1: Classify
    classification = classify_ticket(ticket)

    category = classification["category"]
    confidence = classification["confidence"]

    # Step 2: Route
    route = route_ticket(category)

    # Step 3: Draft response
    draft = draft_response(
        ticket=ticket,
        category=category,
        route=route,
    )

    return {
        "ticket_id": ticket["id"],
        "subject": ticket["subject"],
        "category": category,
        "confidence": confidence,
        "route": route,
        "draft": draft,
    }


def is_rate_limit_error(error):
    return "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error)


def load_existing_results():
    try:
        with open(RESULTS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_results(results):
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)


def main():
    with open("tickets.json") as f:
        tickets = json.load(f)

    results = load_existing_results()

    completed_ids = {
        result["ticket_id"]
        for result in results
    }

    print(f"Already completed: {len(completed_ids)} tickets")

    for ticket in tickets:

        ticket_id = ticket["id"]

        # Skip tickets that already succeeded
        if ticket_id in completed_ids:
            print(
                f"\nSkipping ticket {ticket_id}: "
                f"{ticket['subject']} (already completed)"
            )
            continue

        print(
            f"\nProcessing ticket {ticket_id}: "
            f"{ticket['subject']}"
        )

        while True:
            try:
                result = process_ticket(ticket)

                results.append(result)

                save_results(results)

                print(f"Category: {result['category']}")
                print(f"Confidence: {result['confidence']}")
                print(f"Route: {result['route']}")
                print("Saved successfully.")

                break

            except Exception as e:

                if is_rate_limit_error(e):

                    print("\nGemini rate limit reached.")
                    print("Waiting 50 seconds before retrying...\n")

                    time.sleep(50)

                else:

                    print(
                        f"Error processing ticket "
                        f"{ticket_id}: {e}"
                    )

                    break

        # Small delay between tickets
        time.sleep(5)

    print("\n================================")
    print("Workflow completed.")
    print(f"Processed {len(results)} tickets.")
    print(f"Expected: {len(tickets)} tickets")
    print(f"Remaining: {len(tickets) - len(results)}")
    print(f"Results saved to {RESULTS_FILE}")
    print("================================")


if __name__ == "__main__":
    main()