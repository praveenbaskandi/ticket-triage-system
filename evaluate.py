import json
import statistics


WORKFLOW_FILE = "results/workflow_results.json"
AGENT_FILE = "results/agent_results.json"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def main():
    workflow_results = load_json(WORKFLOW_FILE)
    agent_results = load_json(AGENT_FILE)

    workflow = {
        item["ticket_id"]: item
        for item in workflow_results
    }

    agent = {
        item["ticket_id"]: item
        for item in agent_results
    }

    latencies = [
        item["latency_seconds"]
        for item in agent_results
        if "latency_seconds" in item
    ]

    print("================================")
    print("TICKET TRIAGE EVALUATION")
    print("================================")

    print(f"Total tickets:       {len(workflow)}")
    print(f"Workflow completed:  {len(workflow)}/18")
    print(f"Agent completed:     {len(agent)}/18")

    missing_from_agent = [
        ticket_id
        for ticket_id in workflow
        if ticket_id not in agent
    ]

    missing_from_workflow = [
        ticket_id
        for ticket_id in agent
        if ticket_id not in workflow
    ]

    print("\n--------------------------------")
    print("Execution completeness")
    print("--------------------------------")

    if not missing_from_agent:
        print("All workflow tickets have agent results.")
    else:
        print("Missing agent results:")
        print(missing_from_agent)

    if not missing_from_workflow:
        print("No unexpected agent ticket results.")
    else:
        print("Unexpected agent results:")
        print(missing_from_workflow)

    print("\n--------------------------------")
    print("Workflow classification results")
    print("--------------------------------")

    for ticket_id in sorted(workflow):
        result = workflow[ticket_id]

        print(
            f"Ticket {ticket_id}: "
            f"{result['category']} -> "
            f"{result['route']}"
        )

    print("\n--------------------------------")
    print("Agent latency")
    print("--------------------------------")

    if latencies:
        print(f"Minimum: {min(latencies):.2f}s")
        print(f"Maximum: {max(latencies):.2f}s")
        print(f"Average: {statistics.mean(latencies):.2f}s")

    print("\n--------------------------------")
    print("Agent execution results")
    print("--------------------------------")

    for ticket_id in sorted(agent):
        result = agent[ticket_id]

        print(
            f"Ticket {ticket_id}: "
            f"{result['latency_seconds']:.2f}s"
        )

    print("\n================================")
    print("EVALUATION COMPLETE")
    print("================================")


if __name__ == "__main__":
    main()
