import json

from workflow.classifier import classify_ticket


with open("tickets.json") as f:
    tickets = json.load(f)


ticket = tickets[0]

result = classify_ticket(ticket)

print("Ticket:", ticket["subject"])
print("Classification:", result)
