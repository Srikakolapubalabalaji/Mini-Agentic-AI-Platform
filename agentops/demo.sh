#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "🤖 AGENTOPS DEMO SCRIPT"
echo "=========================================================="
echo ""

# 1. Run the incident
echo "▶️  STEP 1: Triggering Incident & Agent Execution"
echo "Incident: High latency on checkout-api"
echo "This will demonstrate Planning, Retrieval, Verification, and Action."
echo "----------------------------------------------------------"
# We extract the run_id from the output to use in the trace review later
OUTPUT=$(uv run agentops incident-run --file examples/incidents/checkout-api.json)
echo "$OUTPUT"

RUN_ID=$(echo "$OUTPUT" | grep "Starting Run:" | awk '{print $3}')

echo ""
echo "----------------------------------------------------------"
echo "▶️  STEP 2: Trace Review & Audit Replay"
echo "The workflow has completed. All steps, safety decisions,"
echo "and blast-radius checks were logged to our local SQLite db."
echo "Now, replaying the audit trace for Run ID: $RUN_ID"
echo "----------------------------------------------------------"
echo ""

uv run agentops trace-show "$RUN_ID"

echo ""
echo "=========================================================="
echo "✅ DEMO COMPLETE"
echo "Demonstrated: Planning, Retrieval, Verification, Action, Trace review."
echo "=========================================================="
