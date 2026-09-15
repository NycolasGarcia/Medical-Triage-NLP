.PHONY: setup lint test run train train-onnx stack-up stack-down bench load-test

setup:
	uv sync --group training
	uv run pre-commit install

lint:
	uv run ruff check .

test:
	uv run pytest

run:
	uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

train:
	uv run python -m src.models.train

train-onnx:
	uv run python -m src.optimization.onnx_export

stack-up:
	docker compose up -d

stack-down:
	docker compose down

bench:
	uv run python -m scripts.benchmark

load-test:
	uv run python -m scripts.load_test
