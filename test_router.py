from workflow.router import route_ticket


categories = [
    "billing",
    "authentication",
    "technical",
    "account",
    "subscription",
    "unknown",
]


for category in categories:
    route = route_ticket(category)
    print(f"{category} -> {route}")
