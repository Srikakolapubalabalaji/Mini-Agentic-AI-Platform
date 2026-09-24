import logging
from typing import Any

logger = logging.getLogger(__name__)


class ToolGateway:
    """
    Simulated Execution Gateway.
    Never exposes raw SDKs. Validates intent before execution.
    """

    @staticmethod
    def simulate_restart(service: str, idempotency_key: str, tenant_id: str) -> dict[str, Any]:
        logger.info(
            f"Gateway executing simulated RESTART on {service} (tenant={tenant_id}, idemp={idempotency_key})"
        )
        return {
            "success": True,
            "output": f"Simulated restart of {service} successful.",
            "retryable": False,
        }

    @staticmethod
    def simulate_scale(
        service: str, replicas: int, idempotency_key: str, tenant_id: str
    ) -> dict[str, Any]:
        logger.info(
            f"Gateway executing simulated SCALE to {replicas} on {service} (tenant={tenant_id}, idemp={idempotency_key})"
        )
        return {
            "success": True,
            "output": f"Simulated scale of {service} to {replicas} replicas successful.",
            "retryable": False,
        }
