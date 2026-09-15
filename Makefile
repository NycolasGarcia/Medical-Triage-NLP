.PHONY: setup lint test run train stack-up stack-down bench load-test

setup:
	uv sync
	uv run pre-commit install

lint:
	uv run ruff check .

test:
	uv run pytest

run:
	uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

train:
	uv run python -m src.models.train

stack-up:
	docker compose up -d

stack-down:
	docker compose down

bench:
	uv run python -m scripts.benchmark

load-test:
	uv run python -m scripts.load_test
