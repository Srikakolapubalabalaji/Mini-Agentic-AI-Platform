from agentops.persistence.sqlite import append_event


class OTelTracer:
    """
    Minimal observability tracer for the prototype.
    Exports to SQLite as append-only event log.
    Redacts sensitive fields before logging.
    """

    @staticmethod
    def _redact(payload: dict) -> dict:
        # Shallow redact for prototype
        redacted = payload.copy()
        for k in ["api_key", "token", "password"]:
            if k in redacted:
                redacted[k] = "***REDACTED***"
        return redacted

    @staticmethod
    def record_span(run_id: str, trace_id: str, span_name: str, payload: dict):
        safe_payload = OTelTracer._redact(payload)

        # In a real OTel setup, we'd use OpenTelemetry SDK
        # Here we just route to SQLite for auditability
        append_event(
            run_id=run_id,
            trace_id=trace_id,
            message_type=span_name,
            created_at=payload.get("created_at", ""),
            payload_dict=safe_payload,
        )
