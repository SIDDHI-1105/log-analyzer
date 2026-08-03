#!/bin/bash
set -e

# Log Analyzer Deployment Script
# Usage: ./deploy.sh [dev|prod]

ENV=${1:-dev}

echo "🚀 Log Analyzer Deployment"
echo "=========================="
echo "Environment: $ENV"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Determine which compose file to use
if [ "$ENV" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo "📦 Using production configuration: $COMPOSE_FILE"
else
    COMPOSE_FILE="docker-compose.yml"
    echo "📦 Using development configuration: $COMPOSE_FILE"
fi

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Compose file not found: $COMPOSE_FILE"
    exit 1
fi

# Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker compose -f "$COMPOSE_FILE" down 2>/dev/null || true

# Build and start
echo ""
echo "🔨 Building and starting containers..."
docker compose -f "$COMPOSE_FILE" up --build -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check health
echo ""
echo "🏥 Checking service health..."
docker compose -f "$COMPOSE_FILE" ps

# Get local IP for LAN access
LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "unknown")
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📱 Access the application:"
echo "   Local:       http://localhost"
echo "   LAN/Wi-Fi:   http://$LOCAL_IP"
echo ""
echo "🔧 API Documentation:"
echo "   Local:       http://localhost:8001/docs"
echo "   LAN/Wi-Fi:   http://$LOCAL_IP:8001/docs"
echo ""
echo "🛑 To stop:    docker compose -f $COMPOSE_FILE down"
echo "📊 To view logs: docker compose -f $COMPOSE_FILE logs -f"
echo ""
