ROUTE_MAP = {
    "billing": "billing_team",
    "authentication": "account_support",
    "technical": "technical_support",
    "account": "account_support",
    "subscription": "sales_and_subscriptions",
}


def route_ticket(category):
    return ROUTE_MAP.get(category, "general_support")