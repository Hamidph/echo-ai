#!/bin/bash
# Development startup script
# Starts all services needed for local development

set -e

echo "🚀 Starting Echo AI Local Development Environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Start Docker services
echo "📦 Starting PostgreSQL and Redis..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from env.example..."
    cp env.example .env
    echo "⚠️  Please add your API keys to .env file"
fi

# Check if frontend/.env.local exists
if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend/.env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
fi

# Run migrations
echo "🗄️  Running database migrations..."
uv run alembic upgrade head

# Seed test data
echo "🌱 Seeding test data..."
uv run python backend/scripts/seed_test_data.py || echo "Test data already exists"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo ""
echo "Terminal 1 (Backend):"
echo "  uv run uvicorn backend.app.main:app --reload --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend && pnpm dev"
echo ""
echo "Terminal 3 (Celery - Optional):"
echo "  uv run celery -A backend.app.worker worker --loglevel=info"
echo ""
echo "🌐 URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/api/v1/docs"
echo ""
echo "🔑 Test Account:"
echo "  Email:    test@echoai.com"
echo "  Password: password123"
echo ""
