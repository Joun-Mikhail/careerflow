# CareerFlow Backend

FastAPI service for CareerFlow. Layered architecture (routers → services →
repositories → models) with PostgreSQL, SQLAlchemy 2.0, and Alembic.

## Requirements

- Python ≥ 3.11
- PostgreSQL (for local non-Docker runs); the test suite uses in-memory SQLite.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env             # then edit secrets
```

## Running

```bash
alembic upgrade head             # apply migrations
uvicorn app.main:app --reload    # http://localhost:8000
```

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- Health: `http://localhost:8000/health`

## Quality checks

```bash
ruff check . && ruff format --check .
mypy app
pytest --cov --cov-report=term-missing
```

## Migrations

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
alembic downgrade -1
```

## Layout

See [`../docs/06-folder-structure.md`](../docs/06-folder-structure.md) for the
full structure and the conventions each layer follows.
