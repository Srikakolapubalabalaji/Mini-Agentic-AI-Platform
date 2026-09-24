.PHONY: install format lint typecheck test clean demo

install:
	uv sync

format:
	uv run ruff format src tests

lint:
	uv run ruff check src tests

typecheck:
	uv run pyright src tests

test:
	uv run pytest tests/evaluation -v

test-eval:
	uv run pytest tests/evaluation -v

check: format lint test

clean:
	rm -rf .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -f agentops.db

demo:
	uv run agentops incident-run --file examples/incidents/checkout-api.json

serve:
	uv run uvicorn agentops.api.server:app --reload --port 8000
