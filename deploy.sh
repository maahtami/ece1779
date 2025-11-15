#!/bin/bash
# Quick deployment script for IMS (Inventory Management System)

echo "🚀 IMS - Inventory Management System"
echo "===================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file with default settings..."
    cat > .env << EOF
# Database Configuration
POSTGRES_USER=ims_user
POSTGRES_PASSWORD=ims_pass
POSTGRES_DB=ims
PG_PORT=5432
ADMINER_PORT=8080

# Backend Configuration
DATABASE_URL=postgresql://ims_user:ims_pass@db:5432/ims
SECRET_KEY=your-secret-key-change-me-in-production

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "📦 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "✅ Services are running!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Database Admin (Adminer): http://localhost:8080"
echo ""
echo "👤 To stop services: docker-compose down"
echo "📊 To view logs: docker-compose logs -f"
echo ""
echo "🎉 IMS is ready to use!"
