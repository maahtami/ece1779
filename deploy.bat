@echo off
REM Quick deployment script for IMS (Inventory Management System) on Windows

echo.
echo 🚀 IMS - Inventory Management System
echo ====================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop.
    exit /b 1
)

echo ✅ Docker is installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file with default settings...
    (
        echo # Database Configuration
        echo POSTGRES_USER=ims_user
        echo POSTGRES_PASSWORD=ims_pass
        echo POSTGRES_DB=ims
        echo PG_PORT=5432
        echo ADMINER_PORT=8080
        echo.
        echo # Backend Configuration
        echo DATABASE_URL=postgresql://ims_user:ims_pass@db:5432/ims
        echo SECRET_KEY=your-secret-key-change-me-in-production
        echo.
        echo # Frontend Configuration
        echo REACT_APP_API_URL=http://localhost:8000
    ) > .env
    echo ✅ .env file created
) else (
    echo ✅ .env file already exists
)

echo.
echo 📦 Building Docker images...
docker-compose build

echo.
echo 🚀 Starting services...
docker-compose up -d

echo.
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak

echo.
echo ✅ Services are running!
echo.
echo 📍 Access the application:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    Database Admin (Adminer): http://localhost:8080
echo.
echo 👤 To stop services: docker-compose down
echo 📊 To view logs: docker-compose logs -f
echo.
echo 🎉 IMS is ready to use!
echo.
pause
