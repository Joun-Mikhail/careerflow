#!/usr/bin/env sh
# Wait for the database, apply migrations, optionally seed demo data, then
# start the API. Managed hosts can make private networking available a few
# seconds after the container starts, so startup must tolerate a cold database.
set -e

# Normalize DATABASE_URL once, before anything (this probe, Alembic, the app)
# uses it. Managed Postgres providers (Render, Heroku, Supabase, ...) hand out
# bare "postgresql://..." / "postgres://..." DSNs; SQLAlchemy then loads the
# psycopg2 dialect, which the image does NOT ship — we use psycopg v3 instead.
# Rewriting the scheme picks the right driver and prevents the classic
# "ModuleNotFoundError: No module named 'psycopg2'" crash at startup.
if [ -n "${DATABASE_URL:-}" ]; then
  case "$DATABASE_URL" in
    postgres://*)
      DATABASE_URL="postgresql+psycopg://${DATABASE_URL#postgres://}"
      ;;
    postgresql://*)
      DATABASE_URL="postgresql+psycopg://${DATABASE_URL#postgresql://}"
      ;;
  esac
  export DATABASE_URL
fi

python - <<'PY'
import os
import sys
import time

from sqlalchemy import create_engine, text

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise SystemExit("DATABASE_URL is required")

engine = create_engine(database_url, pool_pre_ping=True)
for attempt in range(1, 31):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database connection ready.")
        break
    except Exception as exc:
        print(f"Database not ready (attempt {attempt}/30): {exc}", flush=True)
        time.sleep(2)
else:
    print("Database did not become ready in time.", file=sys.stderr)
    raise SystemExit(1)
PY

echo "Applying database migrations..."
alembic upgrade head

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
  echo "Seeding demo data..."
  python -m app.seed
fi

echo "Starting API..."
exec "$@"
