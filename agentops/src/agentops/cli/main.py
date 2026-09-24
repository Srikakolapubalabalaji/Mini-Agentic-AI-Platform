import json
import sys
import uuid
from pathlib import Path

import typer
from rich.console import Console

from agentops.domain.state import IncidentContext
from agentops.orchestration.graph import build_graph
from agentops.persistence.sqlite import init_db

app = typer.Typer()
console = Console()


@app.command("incident-run")
def run_incident(file: str = typer.Option(..., "--file", "-f", help="Path to incident JSON")):
    """Run an incident workflow from a JSON file."""
    path = Path(file)
    if not path.exists():
        console.print(f"[red]File {file} not found.[/red]")
        sys.exit(1)

    with open(path) as f:
        data = json.load(f)

    incident = IncidentContext(**data)
    run_id = f"run-{uuid.uuid4().hex[:8]}"
    trace_id = f"trace-{uuid.uuid4().hex[:8]}"

    console.print(f"[bold blue]Starting Run:[/bold blue] {run_id} (Trace: {trace_id})")
    console.print(f"[bold]Incident:[/bold] {incident.description}")

    # Init DB for this run
    init_db()

    # Build graph
    graph = build_graph()

    # Initial state
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
        "execution_result": None,
    }

    console.print("\n[bold]Execution Trace:[/bold]")

    # Run the graph
    for output in graph.stream(state):  # type: ignore
        for node_name, state_update in output.items():
            status = state_update.get("status", "UNKNOWN")
            console.print(f"[{node_name}] -> {status}")
            if "safety_decision" in state_update:
                decision = state_update["safety_decision"]["decision"]
                console.print(
                    f"    Safety Decision: [bold {'green' if decision == 'ALLOW' else 'yellow' if decision == 'REQUIRE_APPROVAL' else 'red'}]{decision}[/]"
                )
            if "execution_result" in state_update:
                success = state_update["execution_result"]["success"]
                out = state_update["execution_result"]["output"]
                console.print(f"    Execution: [{'green' if success else 'red'}]{out}[/]")

    console.print(
        f"\n[bold green]Workflow finished.[/bold green] Use `trace show {run_id}` to view details."
    )


@app.command("trace-show")
def show_trace(run_id: str):
    """Show the redacted audit trace for a given run."""
    import sqlite3

    from agentops.application.config import settings

    # We strip the sqlite:/// prefix for standard sqlite3 library connection
    db_path = settings.database_url.replace("sqlite:///", "")
    if not Path(db_path).exists():
        console.print("[red]Database not found. Has a run completed?[/red]")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT message_type, payload FROM event_log WHERE run_id = ?", (run_id,))

    console.print(f"\n[bold]Audit Trace for {run_id}[/bold]")
    for row in cur.fetchall():
        console.print(f"[cyan]{row[0]}[/cyan]: {row[1][:100]}...")


if __name__ == "__main__":
    app()
