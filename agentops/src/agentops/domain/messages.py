import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


def generate_id() -> str:
    return str(uuid.uuid4())


def now_utc() -> str:
    return datetime.now(UTC).isoformat()


class BaseEnvelope(BaseModel):
    """
    Base contract for all Agent-to-Agent messages.
    """

    schema_version: str = Field(default="v1")
    message_id: str = Field(default_factory=generate_id)
    run_id: str
    trace_id: str
    correlation_id: str
    causation_id: str | None = None
    sender: str
    recipient: str
    tenant_id: str
    environment: str
    created_at: str = Field(default_factory=now_utc)
    message_type: str


class InvestigationTask(BaseEnvelope):
    message_type: Literal["InvestigationTask"] = "InvestigationTask"
    objective: str
    known_services: list[str]


class EvidenceBundle(BaseEnvelope):
    message_type: Literal["EvidenceBundle"] = "EvidenceBundle"
    citations: list[dict[str, str]] = Field(description="List of cited evidence IDs and content")
    hypothesis: str
    confidence: float


class RemediationProposal(BaseEnvelope):
    message_type: Literal["RemediationProposal"] = "RemediationProposal"
    action_type: Literal["simulate_restart", "simulate_scale"]
    service: str
    parameters: dict[str, Any]
    preconditions: list[str]
    estimated_blast_radius: str
    idempotency_key: str = Field(default_factory=generate_id)


class SafetyDecision(BaseEnvelope):
    message_type: Literal["SafetyDecision"] = "SafetyDecision"
    decision: Literal["ALLOW", "REQUIRE_APPROVAL", "DENY"]
    reason_code: str
    details: str


class ExecutionResult(BaseEnvelope):
    message_type: Literal["ExecutionResult"] = "ExecutionResult"
    success: bool
    output: str
    retryable: bool = False
