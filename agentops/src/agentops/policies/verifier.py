from agentops.application.config import settings
from agentops.domain.messages import RemediationProposal, SafetyDecision


class DeterministicVerifier:
    """
    Evaluates policy rules deterministically.
    Does NOT use an LLM for safety decisions.
    """

    @staticmethod
    def verify(proposal: RemediationProposal, autonomy_tier: int) -> SafetyDecision:
        # Rule 1: Replica limits
        if proposal.action_type == "simulate_scale":
            replicas = proposal.parameters.get("replicas", 0)
            if replicas > 100:
                return SafetyDecision(
                    run_id=proposal.run_id,
                    trace_id=proposal.trace_id,
                    correlation_id=proposal.message_id,
                    sender="VerifierAgent",
                    recipient="Orchestrator",
                    tenant_id=proposal.tenant_id,
                    environment=proposal.environment,
                    decision="DENY",
                    reason_code="REPLICA_LIMIT_EXCEEDED",
                    details=f"Requested {replicas} exceeds hard limit of 100.",
                )

        # Rule 2: Autonomy Tier Approval
        if autonomy_tier < settings.require_human_approval_tier:
            return SafetyDecision(
                run_id=proposal.run_id,
                trace_id=proposal.trace_id,
                correlation_id=proposal.message_id,
                sender="VerifierAgent",
                recipient="Orchestrator",
                tenant_id=proposal.tenant_id,
                environment=proposal.environment,
                decision="REQUIRE_APPROVAL",
                reason_code="TIER_REQUIRES_APPROVAL",
                details=f"Autonomy tier {autonomy_tier} requires human approval for mutating actions.",
            )

        # Default ALLOW if all invariant checks pass
        return SafetyDecision(
            run_id=proposal.run_id,
            trace_id=proposal.trace_id,
            correlation_id=proposal.message_id,
            sender="VerifierAgent",
            recipient="Orchestrator",
            tenant_id=proposal.tenant_id,
            environment=proposal.environment,
            decision="ALLOW",
            reason_code="POLICY_PASSED",
            details="All deterministic invariant checks passed.",
        )
