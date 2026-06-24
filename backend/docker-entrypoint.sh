#!/usr/bin/env sh
# Wait for the database, apply migrations, optionally seed demo data, then
# start the API. Managed hosts can make private networking available a few
# seconds after the container starts, so startup must tolerate a cold database.
set -e

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
