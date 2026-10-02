# Ticket Triage System — Workflow vs Agent

## Overview

This project implements a customer support ticket triage system in two different ways:

1. **Deterministic Workflow**
2. **Agent-Based System**

Both implementations process customer support tickets by:

1. Classifying the ticket
2. Routing the ticket to the appropriate support team
3. Drafting a customer-facing response

The project also demonstrates:

* Deterministic workflow execution
* Agent-based tool orchestration
* A deterministic response-formatting hook
* A specialized classification subagent
* A LangGraph implementation
* Evaluation using 18 sample tickets
* Agent latency measurement
* Workflow vs. agent comparison

---

# 1. Project Goals

The goal of this project is to demonstrate the difference between a deterministic workflow and an agent-based approach.

The deterministic workflow uses a fixed execution sequence:

```text
Classify → Route → Draft
```

The agent-based implementation provides the model with tools and allows the agent to determine how the ticket should be processed.

The project also demonstrates how a narrow subagent can be used for ambiguous classification and how deterministic validation can be applied after an LLM generates a response.

---

# 2. System Architecture

## Deterministic Workflow

The deterministic workflow follows a fixed sequence.

```text
                Support Ticket
                      |
                      v
                 Classifier
                      |
                      v
                  Category
                      |
                      v
                   Router
                      |
                      v
                Support Team
                      |
                      v
                  Drafter
                      |
                      v
             Customer Response
```

The workflow always executes:

```text
Classify → Route → Draft
```

The model does not decide which processing step should happen next.

### Workflow Implementation

```text
workflow/
├── __init__.py
├── classifier.py
├── router.py
├── drafter.py
└── run_workflow.py
```

---

# 3. Agent Architecture

The agent-based implementation gives the LLM access to tools.

Available tools:

* `classify_tool`
* `route_tool`
* `draft_tool`

The agent can determine how to use these tools based on the ticket and its instructions.

```text
                     Support Ticket
                           |
                           v
                    Ticket Triage Agent
                     /       |        \
                    /        |         \
                   v         v          v
             Classifier    Router     Drafter
                   |
                   v
          Classification Subagent
```

### Agent Implementation

```text
agent/
├── __init__.py
├── agent.py
├── tools.py
├── hooks.py
├── classification_subagent.py
└── run_agent.py
```

---

# 4. Workflow vs Agent

## Deterministic Workflow

The workflow always follows:

```text
Classify → Route → Draft
```

### Characteristics

* Fixed execution path
* Predictable behavior
* Easier to test
* Easier to debug
* Lower orchestration complexity
* Suitable for well-defined processes

---

## Agent

The agent receives tools and instructions and can determine how to process the ticket.

### Characteristics

* Flexible execution
* Tool selection controlled by the agent
* Can delegate classification
* Can adapt its processing path
* More suitable for tasks where the execution path may vary

### Trade-offs

Agent-based systems can introduce:

* Additional model calls
* Higher latency
* More complex orchestration
* Less deterministic execution

For a simple fixed process, a deterministic workflow is easier to control. An agent becomes more useful when the task requires flexible decisions, investigation, or delegation.

---

# 5. Ticket Categories

The system supports five ticket categories:

```text
billing
authentication
technical
account
subscription
```

---

# 6. Routing

Routing is deterministic and maps each category to a support team.

| Category       | Support Team            |
| -------------- | ----------------------- |
| billing        | billing_team            |
| authentication | account_support         |
| technical      | technical_support       |
| account        | account_support         |
| subscription   | sales_and_subscriptions |

The routing logic is implemented in:

```text
workflow/router.py
```

Example:

```text
billing
   ↓
billing_team
```

```text
authentication
   ↓
account_support
```

```text
technical
   ↓
technical_support
```

---

# 7. Response Drafting

The drafting component generates a concise customer-facing response.

The drafting instructions require the response to:

* Address the customer's issue
* Be polite and helpful
* Avoid inventing account information
* Avoid promising a specific resolution or timeframe
* Ask for additional information only when necessary
* Remain under 100 words

Implementation:

```text
workflow/drafter.py
```

---

# 8. Deterministic Formatting Hook

The agent includes a deterministic formatting hook.

Implementation:

```text
agent/hooks.py
```

The hook runs after the LLM generates the draft response.

It performs deterministic validation and formatting.

### Responsibilities

The hook:

1. Removes accidental metadata prefixes
2. Trims unnecessary whitespace
3. Enforces the 100-word limit

For example:

```text
Response: Hello, how can I help you?
```

becomes:

```text
Hello, how can I help you?
```

The hook is called from:

```text
agent/tools.py
```

inside `draft_tool`.

This demonstrates an important pattern:

```text
LLM generates response
        |
        v
Deterministic validation
        |
        v
Final response
```

Instead of relying entirely on the LLM to follow formatting requirements, the application enforces the requirement programmatically.

---

# 9. Classification Subagent

The agent includes a specialized classification subagent.

Implementation:

```text
agent/classification_subagent.py
```

The subagent has a deliberately narrow responsibility:

```text
Determine the correct support-ticket category.
```

It does not:

* Route tickets
* Draft responses
* Perform unrelated tasks

The main agent is instructed to use the classification subagent when:

* A ticket is ambiguous
* Multiple categories appear possible
* Classification confidence is uncertain

This demonstrates delegation of a narrow task to a specialized subagent.

---

# 10. LangGraph Implementation

The classification component was also rebuilt using LangGraph.

Implementation:

```text
langgraph_version/classifier.py
```

The LangGraph implementation contains a simple graph:

```text
START
  |
  v
classify
  |
  v
END
```

The graph receives a ticket and returns:

```text
category
confidence
```

### LangGraph Verification

The LangGraph classifier was executed successfully against three sample tickets.

Results:

```text
Ticket 1 → authentication
Ticket 2 → billing
Ticket 3 → technical
```

This verifies that the LangGraph component can execute the classification logic successfully.

---

# 11. Dataset

The evaluation dataset contains **18 sample support tickets**.

The tickets cover different categories and scenarios, including:

* Password reset
* Duplicate billing
* Application crashes
* Plan upgrades
* Payment failures
* Account lockouts
* Refund issues
* API errors
* Invoice requests
* Account changes
* Unexpected charges
* Performance issues
* Premium feature access
* Billing questions
* Login verification
* Webhook failures
* Subscription cancellation
* Incorrect account balance

The dataset is stored in:

```text
tickets.json
```

---

# 12. Evaluation

Both implementations were executed against all 18 tickets.

## Execution Results

```text
Workflow: 18/18
Agent:    18/18
```

Therefore:

* 18 workflow executions completed
* 18 agent executions completed
* No ticket was left unprocessed

---

# 13. Workflow Classification Results

The deterministic workflow produced the following classifications and routes:

| Ticket | Category       | Route                   |
| -----: | -------------- | ----------------------- |
|      1 | authentication | account_support         |
|      2 | billing        | billing_team            |
|      3 | technical      | technical_support       |
|      4 | subscription   | sales_and_subscriptions |
|      5 | billing        | billing_team            |
|      6 | authentication | account_support         |
|      7 | billing        | billing_team            |
|      8 | technical      | technical_support       |
|      9 | billing        | billing_team            |
|     10 | account        | account_support         |
|     11 | billing        | billing_team            |
|     12 | technical      | technical_support       |
|     13 | subscription   | sales_and_subscriptions |
|     14 | billing        | billing_team            |
|     15 | authentication | account_support         |
|     16 | technical      | technical_support       |
|     17 | subscription   | sales_and_subscriptions |
|     18 | technical      | technical_support       |

---

# 14. Agent Latency

Agent execution latency was recorded for every ticket.

Measured results:

```text
Minimum: 5.45 seconds
Maximum: 6.94 seconds
Average: 6.06 seconds
```

Individual measurements:

| Ticket | Latency |
| -----: | ------: |
|      1 |   6.13s |
|      2 |   5.83s |
|      3 |   6.28s |
|      4 |   6.18s |
|      5 |   6.79s |
|      6 |   5.83s |
|      7 |   5.84s |
|      8 |   5.98s |
|      9 |   5.67s |
|     10 |   5.45s |
|     11 |   5.59s |
|     12 |   6.94s |
|     13 |   5.76s |
|     14 |   6.25s |
|     15 |   5.53s |
|     16 |   6.15s |
|     17 |   6.61s |
|     18 |   6.32s |

---

# 15. Divergence Analysis

Both systems completed all 18 tickets.

The workflow results contain deterministic category and route values.

The agent responses were generated as natural-language responses, with multiple Markdown formatting variations.

For example, the agent could return:

```text
- Category: billing
- Route: billing_team
```

or:

```text
- **Category**: billing
- **Route**: billing_team
```

An initial automated parser treated some of these formatting variations as missing values.

Therefore, the initial parser output showing 9 category and 9 route divergences was a **parsing issue**, not evidence that the agent actually selected different categories or routes.

The agent outputs themselves showed the expected category and route values for the evaluated tickets.

To make future automated comparison reliable, the agent instruction was updated to request structured JSON:

```json
{
  "category": "billing",
  "confidence": 0.99,
  "route": "billing_team",
  "draft": "customer-facing response"
}
```

This removes formatting ambiguity and makes the output machine-readable.

---

# 16. Checkpointing and Rate Limits

The project uses the Gemini API free tier for testing.

During the initial 18-ticket runs, the API occasionally returned HTTP `429` rate-limit errors.

To make the evaluation resilient, the runners were implemented with:

* Saved intermediate results
* Completed-ticket detection
* Retry behavior
* Delays after rate-limit errors

This means a temporary API rate limit does not require restarting the entire evaluation from the beginning.

Previously completed tickets are skipped when the runner starts again.

---

# 17. Results Files

The generated results are stored in:

```text
results/
├── workflow_results.json
└── agent_results.json
```

### Workflow Results

Contains:

* Ticket ID
* Subject
* Category
* Confidence
* Route
* Draft response

### Agent Results

Contains:

* Ticket ID
* Subject
* Agent response
* Execution latency

---

# 18. Evaluation Script

The project includes:

```text
evaluate.py
```

Run:

```bash
python evaluate.py
```

The evaluation script checks:

* Number of workflow results
* Number of agent results
* Missing results
* Workflow classifications
* Workflow routes
* Agent latency
* Minimum latency
* Maximum latency
* Average latency

---

# 19. Project Structure

```text
ticket-triage-system/
│
├── agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── tools.py
│   ├── hooks.py
│   ├── classification_subagent.py
│   └── run_agent.py
│
├── workflow/
│   ├── __init__.py
│   ├── classifier.py
│   ├── router.py
│   ├── drafter.py
│   └── run_workflow.py
│
├── langgraph_version/
│   ├── __init__.py
│   └── classifier.py
│
├── results/
│   ├── workflow_results.json
│   └── agent_results.json
│
├── tickets.json
├── evaluate.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# 20. Installation

Create and activate the virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 21. Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

The API key must not be committed to Git.

The repository should contain `.env` in `.gitignore`.

Example:

```text
.env
.venv/
__pycache__/
*.pyc
```

---

# 22. Running the Deterministic Workflow

From the project root:

```bash
python -m workflow.run_workflow
```

The workflow processes the tickets and saves results to:

```text
results/workflow_results.json
```

---

# 23. Running the Agent

Run:

```bash
python -m agent.run_agent
```

The agent processes the tickets and saves results to:

```text
results/agent_results.json
```

---

# 24. Running the LangGraph Classifier

The LangGraph classifier can be tested with:

```bash
python - <<'PY'
import json

from langgraph_version.classifier import classify_with_langgraph

with open("tickets.json") as f:
    tickets = json.load(f)

for ticket in tickets[:3]:
    result = classify_with_langgraph(ticket)

    print(f"\nTicket {ticket['id']}: {ticket['subject']}")
    print(f"Category: {result['category']}")
    print(f"Confidence: {result['confidence']}")
PY
```

---

# 25. Running the Evaluation

After both implementations have been executed:

```bash
python evaluate.py
```

Expected high-level output:

```text
Total tickets:       18
Workflow completed:  18/18
Agent completed:     18/18
```

The evaluation also reports agent latency.

---

# 26. Technology Stack

The implementation uses:

* Python
* Google Gemini
* Google ADK
* LangGraph
* python-dotenv

The project was developed and tested in GitHub Codespaces.

---

# 27. Claude Agent SDK Substitution

The original assignment specifies the **Claude Agent SDK** for the agent implementation.

For this implementation, Google Gemini and Google ADK were used instead because Anthropic API access required billing and a payment method was not available in the development environment.

The architecture still demonstrates the requested agent concepts:

* Agent-controlled tool usage
* Tool-based classification
* Tool-based routing
* Tool-based drafting
* Specialized subagent delegation
* Deterministic post-processing hook
* Workflow vs. agent comparison
* LangGraph component
* Multi-ticket evaluation
* Latency measurement

This substitution should be explicitly disclosed when submitting the project.

---

# 28. Workflow vs Agent — Summary

| Aspect                   | Workflow            | Agent                |
| ------------------------ | ------------------- | -------------------- |
| Execution path           | Fixed               | Agent-controlled     |
| Classification           | Classifier step     | Classification tool  |
| Routing                  | Fixed routing step  | Routing tool         |
| Drafting                 | Fixed drafting step | Drafting tool        |
| Delegation               | No                  | Specialized subagent |
| Determinism              | Higher              | Lower                |
| Flexibility              | Lower               | Higher               |
| Orchestration complexity | Lower               | Higher               |
| Evaluation               | 18/18               | 18/18                |

---

# 29. Key Learnings

### Workflow

A deterministic workflow is appropriate when:

* The sequence is known
* Each step has a clear responsibility
* Predictability is important
* The process does not require dynamic decisions

### Agent

An agent is useful when:

* The execution path can vary
* The system needs to decide which tool to use
* Some tasks require additional investigation
* Tasks can be delegated to specialized agents

### Hooks

Deterministic hooks are useful when an application needs guarantees that an LLM cannot reliably provide on its own.

For example:

```text
LLM response
     |
     v
Deterministic validation
     |
     v
Application-safe response
```

### Subagents

A narrow subagent can isolate a specialized responsibility, such as ambiguous classification, while keeping the main agent focused on overall ticket processing.

---

# 30. Final Results

The final evaluation successfully processed all 18 tickets:

```text
Workflow: 18/18
Agent:    18/18
```

Agent latency:

```text
Minimum: 5.45s
Maximum: 6.94s
Average: 6.06s
```

The LangGraph classifier was also successfully executed against sample tickets, and the deterministic formatting hook was independently tested.

---

# 31. Conclusion

This project demonstrates two approaches to the same ticket-triage problem.

The deterministic workflow provides a predictable:

```text
Classify → Route → Draft
```

pipeline.

The agent-based implementation provides a more flexible architecture in which the model can use tools and delegate specialized classification work to a subagent.

The project also demonstrates that deterministic application logic can be placed around LLM-generated content to enforce requirements such as response formatting and length limits.

Both implementations were successfully evaluated on 18 support tickets, with all tickets processed successfully.
