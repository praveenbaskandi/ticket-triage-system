from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from workflow.classifier import classify_ticket


class TicketState(TypedDict):
    ticket: dict
    category: str
    confidence: float


def classify_node(state: TicketState):
    result = classify_ticket(state["ticket"])

    return {
        "category": result["category"],
        "confidence": result["confidence"],
    }


builder = StateGraph(TicketState)

builder.add_node("classify", classify_node)

builder.add_edge(START, "classify")
builder.add_edge("classify", END)

classifier_graph = builder.compile()


def classify_with_langgraph(ticket: dict):
    result = classifier_graph.invoke({
        "ticket": ticket,
    })

    return {
        "category": result["category"],
        "confidence": result["confidence"],
    }
