import json

from workflow.classifier import classify_ticket
from workflow.router import route_ticket
from workflow.drafter import draft_response


with open("tickets.json") as f:
    tickets = json.load(f)


ticket = tickets[0]

classification = classify_ticket(ticket)

category = classification["category"]
route = route_ticket(category)

draft = draft_response(ticket, category, route)

print("\n--- TICKET ---")
print(ticket["subject"])

print("\n--- CLASSIFICATION ---")
print(category)

print("\n--- ROUTE ---")
print(route)

print("\n--- DRAFT RESPONSE ---")
print(draft)
