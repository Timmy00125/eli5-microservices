#!/bin/bash

# ELI5 Microservices Development Setup
# This script starts the backend services in Docker and provides instructions for the frontend

echo "🚀 Starting ELI5 Microservices Development Environment"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start backend services
echo "📦 Starting backend services in Docker..."
docker compose up --build -d auth-service history-service eli5-service

# Wait a moment for services to start
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check service health
echo "🔍 Checking service health..."
echo "Auth Service: http://localhost:8001/docs"
echo "History Service: http://localhost:8002/docs"
echo "ELI5 Service: http://localhost:8000/docs"

# Instructions for frontend
echo ""
echo "🎨 Frontend Development Setup:"
echo "1. Open a new terminal"
echo "2. cd ELI5_frontend/eli5"
echo "3. npm install (if not done already)"
echo "4. npm run dev"
echo "5. Open http://localhost:3000"
echo ""
echo "Backend APIs will be available at:"
echo "- Auth API: http://localhost:8001"
echo "- History API: http://localhost:8002"
echo "- ELI5 API: http://localhost:8000"
echo ""
echo "To stop backend services: docker compose down"
echo "To view logs: docker compose logs -f [service-name]"
