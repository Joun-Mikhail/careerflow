#!/usr/bin/env sh
# Apply database migrations (and optionally seed demo data) before starting
# the API. Fails fast if migrations cannot be applied.
set -e

echo "Applying database migrations…"
alembic upgrade head

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
  echo "Seeding demo data…"
  python -m app.seed
fi

echo "Starting API…"
exec "$@"
