#!/bin/sh
set -e

echo "⏳ Waiting for PostgreSQL to be ready..."
while ! python -c "import socket; socket.create_connection(('postgres', 5432), timeout=1)" 2>/dev/null; do
  sleep 1
done
echo "✅ PostgreSQL is ready!"

echo "🔄 Running database migrations..."
PYTHONPATH=/app/src alembic upgrade head
echo "✅ Migrations complete!"

echo "🚀 Starting FastAPI server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
