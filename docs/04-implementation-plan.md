# 04 - Implementation Plan

## Delivery Plan & Milestones (Risk-Ordered)

*We order by technical risk (proving orchestration and safety boundaries) over visual appeal.*

### Milestone 1: Bootstrapping & Domain Primitives (Day 1 - Morning)
**Focus**: Project setup, strict types, and fake models.
*   Initialize `uv` project, linting (Ruff), and typing (Pyright/Mypy).
*   Define core Pydantic domain models (A2A messages, Incident, State).
*   Create Fake/Mock Model Gateway returning deterministic JSON.
*   Setup SQLite persistence configuration.

### Milestone 2: Policy Engine & Tool Gateway (Day 1 - Afternoon)
**Focus**: Proving actions can be gated and safely simulated.
*   Implement `Verifier Agent` (Deterministic Python rules + YAML).
*   Implement Tool Gateway for simulated infrastructure tools.
*   Write unit tests proving `DENY` short-circuits execution.

### Milestone 3: Knowledge Graph & Retrieval Foundation (Day 2 - Morning)
**Focus**: Grounding LLM responses in facts and blast radius.
*   Build JSON-backed NetworkX Graph for dependency resolution.
*   Implement SQLite FTS5 (Lexical) + Qdrant (Semantic) retrieval adapter.
*   Implement Reciprocal Rank Fusion (RRF).
*   Seed mock incidents, logs, and runbooks.

### Milestone 4: Orchestration State Machine (Day 2 - Afternoon)
**Focus**: Wiring agents into the strict graph.
*   Initialize LangGraph `StateGraph`.
*   Implement Planner, Investigator, and I&O Agent nodes.
*   Wire conditional edges routing through the Verifier.
*   Persist checkpoints to SQLite.

### Milestone 5: E2E Tracing & Approval Flow (Day 3)
**Focus**: Auditability and human-in-the-loop.
*   Implement OpenTelemetry spans for Run -> Agent -> Tool.
*   Implement Approval pause/resume logic in Orchestrator.
*   Build SQLite Trace exporter and redactor.

### Milestone 6: CLI & Offline Evaluation (Day 4)
**Focus**: Usability and CI/CD robustness.
*   Build `agentops` Typer CLI (`incident run`, `run approve`, `trace show`).
*   Implement the Offline Pytest Evaluation Harness (Golden Trajectory).
*   Finalize demo script and documentation.

---

## File and Repository Structure

```text
src/agentops/
├── api/                  # FastAPI endpoints (optional wrapper)
├── cli/                  # Typer CLI commands
├── domain/               # Pure Pydantic models (A2A Envelopes, State)
├── agents/               # Planner, Investigator, I&O Agents
├── orchestration/        # LangGraph State Machine, Checkpointer
├── policies/             # Deterministic rules (Verifier) & YAML config
├── retrieval/            # SQLite FTS5, Qdrant adapters, RRF logic
├── knowledge_graph/      # NetworkX implementation
├── tools/                # Tool Gateway, Mock SDKs, JSON Schemas
├── persistence/          # SQLAlchemy Models, Trace Storage
├── observability/        # OTel Spans, Logging, Redaction
└── model_gateway/        # LLM Provider Adapters (Gemini/OpenAI/Fake)

tests/
├── unit/                 # Pure domain, policy, and parser tests
├── integration/          # DB, Retrieval, and Graph integration
├── contract/             # Tool Gateway schema compliance
└── evaluation/           # Offline Trajectory / Invariant tests

examples/
├── incidents/            # Seed JSON files
├── knowledge/            # Seed logs, metrics, runbooks
└── config/               # Policy YAMLs
```

---

## Test Strategy and Acceptance Criteria

### Test Strategy
*   **Unit Tests**: Pytest for domain models, state transitions (mocked LLM), policy rules.
*   **Integration Tests**: Database read/write, Vector DB retrieval checks, Graph traversal correctness.
*   **Contract Tests**: Ensure tools adhere precisely to MCP-style JSON schemas.
*   **Offline Evaluation (Invariant Testing)**: Run full trajectories using a Fake LLM that emits expected JSON. Assert state never enters `EXECUTING` without `ALLOW` or `Operator Approval`.

### Requirements to Acceptance Mapping
| Requirement | Validation |
| :--- | :--- |
| **Strict Agent Duties** | Agents emit typed A2A messages (tested via Pydantic). Planner cannot emit ToolProposals. |
| **Orchestration** | LangGraph compiled state machine graph; transition table verified in unit tests. |
| **Policy/Safety Gate** | Invariant test: Force I&O agent to propose illegal scale -> assert workflow ends in `DENIED`. |
| **Hybrid Retrieval** | Integration test: Query combining exact log ID (Lexical) and vague symptom (Semantic) returns correctly ranked chunk. |
| **Simulated Execution** | Verify mock tool execution returns structured success and persists outcome. |
| **Trace/Replay** | E2E Test: Run workflow, fetch trace by ID, assert redaction. Trigger replay, assert timeline matches. |

---

## Definition of Done and Demo Checklist

### Definition of Done
1.  All code strictly typed (Pyright/Mypy passing).
2.  CI pipeline executes format, lint, unit tests, and offline evaluations successfully.
3.  No live API keys required to run the default test suite.
4.  Documentation accurately reflects the deployed codebase.

### Demo Checklist
- [ ] `agentops incident run` starts workflow and outputs to CLI.
- [ ] Logs show Planner delegating to Investigator.
- [ ] Investigator retrieves citations (Hybrid Search).
- [ ] I&O Agent proposes action; Verifier runs Knowledge Graph blast-radius check.
- [ ] Verifier pauses workflow for Tier 2 action.
- [ ] Operator runs `agentops run approve <run-id>`.
- [ ] Tool Gateway executes simulation.
- [ ] Operator runs `agentops trace show <run-id>` to view redacted audit log.
- [ ] Operator runs `agentops run replay <run-id> --mode audit`.
