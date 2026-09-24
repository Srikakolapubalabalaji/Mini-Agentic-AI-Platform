from typing import Any, TypedDict

from pydantic import BaseModel


class IncidentContext(BaseModel):
    incident_id: str
    tenant_id: str
    environment: str
    service: str
    description: str
    requested_autonomy_tier: int


class WorkflowState(TypedDict):
    """
    Strict state object for LangGraph orchestration.
    """

    run_id: str
    trace_id: str

    # Context
    incident: IncidentContext

    # Workflow Progression
    status: str  # e.g. RECEIVED, VERIFYING_SAFETY, COMPLETED, FAILED
    error_detail: str | None

    # A2A payloads (stored as dicts for langgraph serializability, validated as Pydantic)
    investigation_task: dict[str, Any] | None
    evidence_bundle: dict[str, Any] | None
    remediation_proposal: dict[str, Any] | None
    safety_decision: dict[str, Any] | None
    execution_result: dict[str, Any] | None

    # Counters
    retry_count: int
