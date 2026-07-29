#!/bin/sh

set -e


echo "Running migrations..."

alembic upgrade head


echo "Running database seed..."


if [ -z "$DATABASE_PSQL_URL" ]; then
    echo "ERROR: DATABASE_PSQL_URL is not defined"
    exit 1
fi


psql "$DATABASE_PSQL_URL" \
    -v ON_ERROR_STOP=1 \
    -f /app/db-init/seed-init.sql


echo "Seed completed."


echo "Starting backend..."


exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000