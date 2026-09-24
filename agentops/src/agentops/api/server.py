import uuid
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agentops.domain.state import IncidentContext
from agentops.orchestration.graph import build_graph
from agentops.persistence.sqlite import init_db

app = FastAPI(title="AgentOps API", version="1.0.0")

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class IncidentRequest(BaseModel):
    description: str
    service: str
    environment: str = "production"
    tenant_id: str = "t-acme-corp"
    requested_autonomy_tier: int = 3

@app.get("/")
def read_root():
    return FileResponse(static_dir / "index.html")

@app.post("/v1/incidents/run")
def run_incident_workflow(request: IncidentRequest):
    """Executes the LangGraph incident workflow and returns the trace."""
    init_db()
    graph = build_graph()
    
    incident_id = f"INC-{uuid.uuid4().hex[:8]}"
    run_id = f"run-{uuid.uuid4().hex[:8]}"
    trace_id = f"trace-{uuid.uuid4().hex[:8]}"
    
    incident = IncidentContext(
        incident_id=incident_id,
        tenant_id=request.tenant_id,
        environment=request.environment,
        service=request.service,
        description=request.description,
        requested_autonomy_tier=request.requested_autonomy_tier
    )
    
    state = {
        "run_id": run_id,
        "trace_id": trace_id,
        "incident": incident,
        "status": "RECEIVED",
        "error_detail": None,
        "retry_count": 0,
        "investigation_task": None,
        "evidence_bundle": None,
        "remediation_proposal": None,
        "safety_decision": None,
        "execution_result": None
    }
    
    trace_events = []
    
    for output in graph.stream(state): # type: ignore
        for node_name, state_update in output.items():
            status = state_update.get("status", "UNKNOWN")
            event = {
                "node": node_name,
                "status": status,
                "details": {}
            }
            if "investigation_task" in state_update and node_name == "planner":
                event["details"]["task"] = state_update["investigation_task"]["objective"]
            if "evidence_bundle" in state_update and node_name == "investigator":
                event["details"]["hypothesis"] = state_update["evidence_bundle"]["hypothesis"]
                event["details"]["citations"] = state_update["evidence_bundle"]["citations"]
            if "remediation_proposal" in state_update and node_name == "io_agent":
                event["details"]["action"] = state_update["remediation_proposal"]["action_type"]
                event["details"]["blast_radius"] = state_update["remediation_proposal"]["estimated_blast_radius"]
            if "safety_decision" in state_update:
                decision = state_update["safety_decision"]
                event["details"]["decision"] = decision["decision"]
                event["details"]["reason"] = decision["reason_code"]
            if "execution_result" in state_update:
                res = state_update["execution_result"]
                event["details"]["execution"] = res["output"]
                event["details"]["success"] = res["success"]
                
            trace_events.append(event)
            
    return {
        "run_id": run_id,
        "trace_id": trace_id,
        "events": trace_events
    }
