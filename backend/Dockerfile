# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# CareerFlow backend image
# ---------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS base

# Keep Python lean and predictable inside the container.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install runtime dependencies first for better layer caching. Only the
# project metadata is copied so the dependency layer is reused unless it
# changes. (psycopg ships a binary wheel, so no system build deps are needed.)
COPY pyproject.toml README.md ./
RUN pip install --upgrade "pip>=24.2" "setuptools>=78.1.1" \
    && pip install "fastapi>=0.111,<1.0" "uvicorn[standard]>=0.30,<1.0" \
       "sqlalchemy>=2.0.30,<2.1" "alembic>=1.13,<2.0" "pydantic>=2.7,<3.0" \
       "pydantic-settings>=2.3,<3.0" "psycopg[binary]>=3.1,<4.0" \
       "bcrypt>=4.1,<5.0" "pyjwt>=2.8,<3.0" "python-multipart>=0.0.9,<1.0" \
       "email-validator>=2.1,<3.0"

# Copy the application source and migrations.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY docker-entrypoint.sh ./

# Run as a non-root user.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/var/uploads \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
