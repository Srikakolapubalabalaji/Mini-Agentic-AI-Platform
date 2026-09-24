from agentops.domain.messages import EvidenceBundle, generate_id
from agentops.domain.state import WorkflowState
from agentops.retrieval.hybrid import HybridRetriever


class InvestigatorAgent:
    """
    Retrieves evidence and forms a hypothesis.
    """

    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever

    def investigate(self, state: WorkflowState) -> dict:
        incident = state["incident"]

        # Retrieve evidence
        results = self.retriever.search(query=incident.description, service=incident.service)

        citations = []
        hypothesis = "No evidence found."

        if results:
            citations = [{"id": r["id"], "content": r["content"]} for r in results]
            hypothesis = f"Found runbook evidence suggesting scale or restart based on '{results[0]['title']}'"

        bundle = EvidenceBundle(
            run_id=state["run_id"],
            trace_id=state["trace_id"],
            correlation_id=generate_id(),
            sender="InvestigatorAgent",
            recipient="Orchestrator",
            tenant_id=incident.tenant_id,
            environment=incident.environment,
            citations=citations,
            hypothesis=hypothesis,
            confidence=0.85,
        )

        return {"evidence_bundle": bundle.model_dump(), "status": "SYNTHESIZING_EVIDENCE"}
