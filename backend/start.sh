#!/usr/bin/env bash
# Render start script for backend
# Runs migrations and starts the FastAPI server

set -e

echo "🚀 Starting Log Analyzer Backend..."

# Wait for database to be ready (Render handles this, but good to be safe)
echo "⏳ Waiting for database..."
sleep 3

# Run Alembic migrations
echo "🔄 Running database migrations..."
PYTHONPATH=/opt/render/project/src/backend/src alembic upgrade head

# Start the server
echo "✅ Starting FastAPI server on port $PORT..."
PYTHONPATH=/opt/render/project/src/backend/src uvicorn src.main:app --host 0.0.0.0 --port $PORT
