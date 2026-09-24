# AgentOps: Mini Agentic AI Platform

A deterministic, bounds-checked Agentic workflow platform for safe production incident analysis and remediation.

## 🏗️ Architecture at a Glance

Unlike standard open-ended chatbots, AgentOps relies on a strict **LangGraph state machine** combined with a **Deterministic Safety Verifier**. 

1. **A2A Messages**: Agents do not pass raw text. They exchange versioned Pydantic schemas (e.g., `RemediationProposal`).
2. **Hybrid Retrieval**: Evidence is gathered using Lexical + Semantic fusion before any action is proposed.
3. **Safety Sandbox**: LLMs cannot execute infrastructure code. They generate proposals which are intercepted by a deterministic Python Policy engine. If a proposal violates blast-radius thresholds or autonomy tier limits, it is halted.
4. **Append-Only Audit**: Every node transition and safety decision is logged to SQLite for offline compliance and replayability.

*(See the `docs/` directory for detailed ADRs, Mermaid state diagrams, and the full implementation plan).*

---

## ⏱️ Five-Minute Quick Start

### 1. Prerequisites
Ensure you have Python 3.12+ and `uv` installed.

### 2. Setup
Clone the repository and install dependencies using our Makefile:
```bash
make install
```

### 3. Run the Evaluation Tests
Run the offline Pytest trajectory tests to prove the state-machine transitions and invariant safety gates work without live LLM API keys:
```bash
make test
```

### 4. Run the CLI Demo
Execute a predefined incident end-to-end via the terminal:
```bash
make demo
```

### 5. Launch the Web UI
Start the FastAPI background server to interact with the platform visually:
```bash
make serve
# Open http://localhost:8000 in your browser
```

---

## 🔍 CI Pipeline & Rollback Strategy

**CI Pipeline**
The repository includes a GitHub Actions pipeline (`.github/workflows/ci.yml`) that runs on every Pull Request. It enforces:
1. Code formatting and linting via `ruff`.
2. Static type checking via `pyright`.
3. Execution of the deterministic Pytest evaluation harness.

**Rollback Explanation**
AgentOps is designed with forward-only schema migrations in mind:
* **Code Rollback**: Because state is managed via discrete Pydantic messages logged to SQLite, rolling back a deployment simply means reverting the Git SHA. Older versions of the agents will safely ignore newer optional fields in the JSON payloads.
* **Audit Trail Recovery**: The `event_log` in SQLite is append-only. If a bad remediation policy is deployed and executes incorrectly, the timeline can be reconstructed by running `uv run agentops trace-show <run-id>`, and the previous version of the code can be re-run against the old checkpoints.
