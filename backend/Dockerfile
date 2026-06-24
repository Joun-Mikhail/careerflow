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

# Install the project's runtime dependencies straight from pyproject.toml, so
# the image can never drift from the declared dependency set. The application
# source is needed for the build backend to resolve the package.
# (psycopg ships a binary wheel, so no system build deps are needed.)
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install --upgrade "pip>=24.2" "setuptools>=78.1.1" \
    && pip install --no-cache-dir .

# Copy migrations and the entrypoint.
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
# Shell form so ${PORT} (injected by hosts such as Railway) is honoured at
# runtime; falls back to 8000 for local/Compose use.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
