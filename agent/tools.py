from workflow.classifier import classify_ticket
from workflow.router import route_ticket
from workflow.drafter import draft_response

from agent.hooks import enforce_draft_format


def classify_tool(ticket: dict) -> dict:
    """
    Classify a support ticket into a support category.
    """

    result = classify_ticket(ticket)

    return {
        "category": result["category"],
        "confidence": result["confidence"],
    }


def route_tool(category: str) -> dict:
    """
    Route a ticket category to the appropriate support team.
    """

    route = route_ticket(category)

    return {
        "route": route,
    }


def draft_tool(
    ticket: dict,
    category: str,
    route: str,
) -> dict:
    """
    Draft a customer-facing first response.
    """

    draft = draft_response(
        ticket=ticket,
        category=category,
        route=route,
    )

    # Deterministic hook:
    # enforce formatting after the LLM generates the draft.
    draft = enforce_draft_format(draft)

    return {
        "draft": draft,
    }