# 03 - Architecture Decisions

## Summary of Key Decisions

| Decision | Selected Option | Reason | Prototype Simplification vs Production |
| :--- | :--- | :--- | :--- |
| **Orchestration** | LangGraph | Explicit state management with checkpointing natively mapped to Python. | Prototype: In-memory/SQLite checkpoints. Production: Redis/Postgres checkpointer with HA worker nodes. |
| **Model Boundary** | Pydantic v2 + Lightweight Gateway | Native JSON Schema generation and validation. Strict enforcement without Langchain bloat. | Prototype: Single provider (Gemini/OpenAI) + Fake Model for tests. Production: Multi-provider routing, fallbacks, token budget quotas. |
| **Persistence** | SQLite (SQLAlchemy) | Zero-infrastructure local setup. Native JSON support. | Prototype: Single SQLite DB file. Production: Postgres with read replicas, dedicated audit trail DB. |
| **Safety Policy** | Python Rules + YAML Config | Simple, fast, deterministic. Easily unit tested. | Prototype: In-code rules + YAML. Production: OPA/Rego for cross-organization decentralized policy enforcement. |
| **Retrieval** | SQLite FTS5 + Local Qdrant | RRF hybrid search. Qdrant runs locally (in-memory or Docker). | Prototype: Local/Memory Qdrant. Production: Dedicated Qdrant/Pinecone cluster, streaming embedding pipelines. |
| **Knowledge Graph** | NetworkX (JSON Backed) | Sufficient for small-to-medium topologies (1000s of nodes) to calculate blast radius via BFS/DFS. | Prototype: JSON persisted NetworkX graph. Production: Neo4j or Amazon Neptune. |
| **Tool Protocol** | Local Python Function Gateway (MCP-style schema) | Fast to implement, direct validation via Pydantic. | Prototype: Local function routing. Production: Dedicated out-of-process MCP Server sidecars via HTTPS/stdio. |

---

## Architectural Decision Records (ADRs)

### ADR-001: Orchestration using LangGraph
*   **Alternatives Considered**: LangChain Agents, AutoGen, pure Python State Machine.
*   **Decision**: Use LangGraph.
*   **Reason**: We need strict transition tables (A -> B conditionally), built-in checkpointing for pauses (Approval step), and deterministic boundaries. Pure LLM-driven loops (Langchain AgentExecutor) are unsafe. Pure Python State Machine lacks built-in resume/checkpoint visualization.
*   **Trade-off/Risk**: LangGraph has a learning curve and can feel magical. We mitigate this by using strictly typed `WorkflowState` objects, never loose dictionaries.

### ADR-002: Model Abstraction via Pydantic v2
*   **Alternatives Considered**: Instructor, raw SDKs, LangChain output parsers.
*   **Decision**: Define a minimal `ModelGateway` interface relying entirely on Pydantic v2 JSON Schema and validation.
*   **Reason**: Centralizes model temperature, retries, and token budgets. Pydantic provides rigorous schema validation (e.g., rejecting an action without an `idempotency_key`).
*   **Trade-off/Risk**: Writing explicit Pydantic schemas for every A2A message is verbose. However, verbosity equals auditability.

### ADR-003: Hybrid Retrieval
*   **Alternatives Considered**: Pure Semantic (ChromaDB), Pure Lexical (Elasticsearch).
*   **Decision**: SQLite FTS5 for Lexical, Local Qdrant for Semantic, Reciprocal Rank Fusion (RRF) for merge.
*   **Reason**: Incident logs and metrics contain exact identifiers (Lexical necessity), while runbooks require intent matching (Semantic necessity).
*   **Trade-off/Risk**: Running two indices increases complexity. Qdrant local keeps it manageable without Docker for the default path.

### ADR-004: Knowledge Graph for Blast Radius
*   **Alternatives Considered**: Relational DB joins, Neo4j, LLM intuition.
*   **Decision**: NetworkX backed by JSON.
*   **Reason**: LLMs are terrible at deterministic graph traversal. Relational DBs struggle with variable-depth upstream/downstream resolution. NetworkX provides instant in-memory pathfinding for dependency analysis.
*   **Trade-off/Risk**: In-memory graph won't scale to millions of nodes. Production requires a graph database.

### ADR-005: Persistence and Audit
*   **Alternatives Considered**: JSON lines, Postgres.
*   **Decision**: SQLite via SQLAlchemy.
*   **Reason**: The 3-4 day timebox and local deployment constraint make Postgres too heavy to mandate. SQLite allows easy sharing and resetting of the prototype state.
*   **Trade-off/Risk**: SQLite lacks high concurrency, which is acceptable for a single-operator local prototype.

### ADR-006: Deterministic Safety Policy
*   **Alternatives Considered**: LLM as a Judge, Open Policy Agent (OPA).
*   **Decision**: Typed Python rules and versioned YAML config.
*   **Reason**: LLM-as-judge violates the deterministic safety constraint. OPA requires learning Rego and adds infrastructural cost. Python rules ensure the verifier is simple, strict, and fast.
*   **Trade-off/Risk**: Hardcoded rules require code changes for complex new policies.

### ADR-007: Tool Protocol Gateway
*   **Alternatives Considered**: Direct SDK invocation by agents.
*   **Decision**: A structured Python gateway applying MCP-style JSON Schema contracts.
*   **Reason**: Direct SDK access is a severe security vulnerability. Agents must propose an action; the Gateway authenticates, validates, and simulates.
*   **Trade-off/Risk**: Adds boilerplate to wrap every SDK call.

### ADR-008: Observability
*   **Alternatives Considered**: LangSmith, pure standard library logging.
*   **Decision**: OpenTelemetry span hierarchy + JSON structured logging.
*   **Reason**: LangSmith violates the "runnable without paid SaaS" constraint. OTel spans (`Workflow` -> `Agent` -> `Tool`) provide industry-standard tracing.
*   **Trade-off/Risk**: OTel instrumentation is verbose. We will wrap it in a lightweight internal tracer utility.

### ADR-009: Offline Evaluation
*   **Alternatives Considered**: LLM-based evaluation (RAGAS), manual clicking.
*   **Decision**: Local Pytest evaluation suite with fake model adapters.
*   **Reason**: A CI-gated prototype requires deterministic tests. We evaluate trajectory milestones (e.g., "Did it cite evidence?") rather than brittle exact prompt text.
*   **Trade-off/Risk**: Requires building fake adapters, but ensures the core logic works without API keys.
