from agentops.domain.state import IncidentContext
from agentops.orchestration.graph import build_graph


def test_golden_trajectory_autonomous_allow():
    """
    Test the golden path:
    A high tier (autonomy tier 3) incident flows completely through.
    """
    incident = IncidentContext(
        incident_id="test-1",
        tenant_id="t-test",
        environment="prod",
        service="checkout-api",
        description="High latency and 5xx errors",
        requested_autonomy_tier=3,
    )

    graph = build_graph(data_dir="examples/knowledge")

    state = {
        "run_id": "test-run",
        "trace_id": "test-trace",
        "incident": incident,
        "status": "RECEIVED",
        "error_detail": None,
        "retry_count": 0,
        "investigation_task": None,
        "evidence_bundle": None,
        "remediation_proposal": None,
        "safety_decision": None,
        "execution_result": None,
    }

    # Run graph fully
    final_state = graph.invoke(state)  # type: ignore

    # Assertions
    assert final_state["status"] == "COMPLETED"
    assert final_state["remediation_proposal"]["service"] == "checkout-api"
    assert final_state["safety_decision"]["decision"] == "ALLOW"
    assert final_state["execution_result"]["success"] is True


def test_trajectory_requires_approval():
    """
    Test that a Tier 2 request properly halts at WAITING_FOR_APPROVAL.
    """
    incident = IncidentContext(
        incident_id="test-2",
        tenant_id="t-test",
        environment="prod",
        service="checkout-api",
        description="High latency",
        requested_autonomy_tier=1,  # Tier 1 requires approval for execution
    )

    graph = build_graph(data_dir="examples/knowledge")

    state = {
        "run_id": "test-run-2",
        "trace_id": "test-trace-2",
        "incident": incident,
        "status": "RECEIVED",
        "error_detail": None,
        "retry_count": 0,
        "investigation_task": None,
        "evidence_bundle": None,
        "remediation_proposal": None,
        "safety_decision": None,
        "execution_result": None,
    }

    final_state = graph.invoke(state)  # type: ignore

    assert final_state["status"] == "WAITING_FOR_APPROVAL"
    assert final_state["safety_decision"]["decision"] == "REQUIRE_APPROVAL"
    assert "execution_result" not in final_state or final_state["execution_result"] is None
