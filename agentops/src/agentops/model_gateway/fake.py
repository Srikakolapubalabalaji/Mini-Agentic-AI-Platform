from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class FakeModelGateway:
    """
    Deterministic fake model for testing and offline evaluation.
    Bypasses LLM API keys and returns expected JSON schemas directly.
    """

    def __init__(self):
        self.call_history = []
        self.canned_responses = {}

    def set_canned_response(self, response_type: type[T], response: T):
        self.canned_responses[response_type.__name__] = response

    def generate_structured(self, prompt: str, schema: type[T]) -> T:
        """
        Simulate a structured generation call to an LLM.
        """
        self.call_history.append({"prompt": prompt, "schema": schema.__name__})

        # Return canned response if configured
        if schema.__name__ in self.canned_responses:
            return self.canned_responses[schema.__name__]

        # Fallback to an empty/default instantiated schema if possible
        # In a real test, canned_responses should be seeded
        try:
            return schema.model_construct()
        except Exception as e:
            raise RuntimeError(
                f"FakeModelGateway lacks a canned response for {schema.__name__} and failed to construct default: {e}"
            )
