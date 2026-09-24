from agentops.domain.messages import InvestigationTask, generate_id
from agentops.domain.state import WorkflowState


class PlannerAgent:
    """
    Parses intent into an InvestigationTask.
    """

    @staticmethod
    def plan(state: WorkflowState) -> dict:
        incident = state["incident"]

        task = InvestigationTask(
            run_id=state["run_id"],
            trace_id=state["trace_id"],
            correlation_id=generate_id(),
            sender="PlannerAgent",
            recipient="Orchestrator",
            tenant_id=incident.tenant_id,
            environment=incident.environment,
            objective=f"Investigate {incident.description}",
            known_services=[incident.service],
        )

        return {"investigation_task": task.model_dump(), "status": "INVESTIGATING"}
