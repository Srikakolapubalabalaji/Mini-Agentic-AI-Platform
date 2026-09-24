from typing import Literal

from langgraph.graph import END, StateGraph

from agentops.agents.investigator import InvestigatorAgent
from agentops.agents.io_agent import IOAgent
from agentops.agents.planner import PlannerAgent
from agentops.domain.messages import ExecutionResult, RemediationProposal
from agentops.domain.state import WorkflowState
from agentops.knowledge_graph.graph import KnowledgeGraph
from agentops.policies.verifier import DeterministicVerifier
from agentops.retrieval.hybrid import HybridRetriever
from agentops.tools.gateway import ToolGateway


def build_graph(data_dir: str = "examples/knowledge"):
    workflow = StateGraph(WorkflowState)

    # Initialize static agents
    retriever = HybridRetriever(f"{data_dir}/runbooks.json")
    kg = KnowledgeGraph(f"{data_dir}/dependencies.json")

    investigator = InvestigatorAgent(retriever)
    io_agent = IOAgent(kg)

    def receive_incident(state: WorkflowState) -> dict:
        return {"status": "VALIDATING_INPUT"}

    def verifier_node(state: WorkflowState) -> dict:
        proposal = RemediationProposal(**state["remediation_proposal"])
        decision = DeterministicVerifier.verify(proposal, state["incident"].requested_autonomy_tier)
        return {"safety_decision": decision.model_dump()}

    def route_after_verification(
        state: WorkflowState,
    ) -> Literal["WAITING_FOR_APPROVAL", "EXECUTING", "DENIED"]:
        decision = state["safety_decision"]["decision"]
        if decision == "ALLOW":
            return "EXECUTING"
        elif decision == "REQUIRE_APPROVAL":
            return "WAITING_FOR_APPROVAL"
        else:
            return "DENIED"

    def execution_node(state: WorkflowState) -> dict:
        proposal = state["remediation_proposal"]
        if proposal["action_type"] == "simulate_scale":
            res = ToolGateway.simulate_scale(
                service=proposal["service"],
                replicas=proposal["parameters"]["replicas"],
                idempotency_key=proposal["idempotency_key"],
                tenant_id=proposal["tenant_id"],
            )
        else:
            res = {"success": False, "output": "Unknown action", "retryable": False}

        result = ExecutionResult(
            run_id=state["run_id"],
            trace_id=state["trace_id"],
            correlation_id=proposal["message_id"],
            sender="Gateway",
            recipient="Orchestrator",
            tenant_id=proposal["tenant_id"],
            environment=proposal["environment"],
            success=res["success"],
            output=res["output"],
        )
        return {"execution_result": result.model_dump(), "status": "COMPLETED"}

    workflow.add_node("receive", receive_incident)
    workflow.add_node("planner", PlannerAgent.plan)
    workflow.add_node("investigator", investigator.investigate)
    workflow.add_node("io_agent", io_agent.propose)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("execute", execution_node)

    workflow.add_node("waiting", lambda state: {"status": "WAITING_FOR_APPROVAL"})
    workflow.add_node("denied", lambda state: {"status": "DENIED"})

    workflow.set_entry_point("receive")
    workflow.add_edge("receive", "planner")
    workflow.add_edge("planner", "investigator")
    workflow.add_edge("investigator", "io_agent")
    workflow.add_edge("io_agent", "verifier")

    workflow.add_conditional_edges(
        "verifier",
        route_after_verification,
        {"EXECUTING": "execute", "WAITING_FOR_APPROVAL": "waiting", "DENIED": "denied"},
    )

    workflow.add_edge("execute", END)
    workflow.add_edge("waiting", END)
    workflow.add_edge("denied", END)

    return workflow.compile()
