from agentops.domain.messages import RemediationProposal, generate_id
from agentops.domain.state import WorkflowState
from agentops.knowledge_graph.graph import KnowledgeGraph


class IOAgent:
    """
    Infrastructure and Operations Agent.
    Proposes remediations based on evidence and graph blast radius.
    """

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def propose(self, state: WorkflowState) -> dict:
        incident = state["incident"]

        # Calculate blast radius from KG
        blast_radius = self.kg.check_blast_radius(incident.service)

        # If the incident is about 5xx, we propose a scale (mock logic based on runbook evidence)
        proposal = RemediationProposal(
            run_id=state["run_id"],
            trace_id=state["trace_id"],
            correlation_id=generate_id(),
            sender="IOAgent",
            recipient="Orchestrator",
            tenant_id=incident.tenant_id,
            environment=incident.environment,
            action_type="simulate_scale",
            service=incident.service,
            parameters={"replicas": 50},
            preconditions=["Confirmed 5xx errors", "Evidence runbook supports scale"],
            estimated_blast_radius=blast_radius,
        )

        return {"remediation_proposal": proposal.model_dump(), "status": "PROPOSING_REMEDIATION"}
