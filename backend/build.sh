#!/usr/bin/env bash
# Render build script for backend
# Runs after dependencies are installed, before startCommand

set -e

echo "🔧 Backend build starting..."

# Install dependencies
pip install -r requirements.txt

echo "✅ Backend build complete!"
