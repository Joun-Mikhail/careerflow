# Common backend tasks. Run from the backend/ directory: `make check`.
.PHONY: install dev migrate seed test cov lint fmt typecheck security check

install:  ## Install the package with dev extras
	pip install -e ".[dev]"

dev:  ## Run the API with autoreload
	uvicorn app.main:app --reload

migrate:  ## Apply database migrations
	alembic upgrade head

seed:  ## Seed the demo dataset
	python -m app.seed

test:  ## Run the test suite
	pytest

cov:  ## Run tests with a coverage report
	pytest --cov --cov-report=term-missing

lint:  ## Lint with ruff
	ruff check .

fmt:  ## Format with ruff
	ruff format .

typecheck:  ## Static type checking
	mypy app

security:  ## Static + dependency security scans
	bandit -r app -q
	pip-audit

# Run everything CI runs, in order.
check: lint typecheck security cov
	ruff format --check .
