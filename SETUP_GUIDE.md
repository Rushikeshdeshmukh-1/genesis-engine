# Local Setup Guide for Project RDx 00

This guide provides detailed instructions for setting up the Project RDx 00 development environment on Windows without Docker.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Service Installation](#service-installation)
3. [Database Setup](#database-setup)
4. [Application Setup](#application-setup)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have:

- **Windows 10 or 11** (64-bit)
- **Administrator access** for installing services
- **16GB+ RAM** (32GB recommended)
- **50GB+ free disk space**
- **Stable internet connection** for downloads

### Install Base Requirements

1. **Python 3.11+**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: `python --version`

2. **Node.js 20+**
   - Download from: https://nodejs.org/
   - Use the LTS version
   - Verify: `node --version` and `npm --version`

3. **Git** (optional, for version control)
   - Download from: https://git-scm.com/download/win

## Service Installation

### 1. PostgreSQL 16 with pgvector

**Installation:**

1. Download PostgreSQL 16 from: https://www.postgresql.org/download/windows/
2. Run the installer
3. During installation:
   - Set password for `postgres` user: `postgres_password`
   - Port: `5432` (default)
   - Locale: Default
4. Complete the installation

**Install pgvector extension:**

Option A - Using winget (Windows 11):
```powershell
winget install pgvector.pgvector
```

Option B - Manual installation:
1. Download from: https://github.com/pgvector/pgvector/releases
2. Extract to PostgreSQL installation directory
3. Follow the README instructions

**Verify:**
```powershell
# Check if PostgreSQL service is running
Get-Service postgresql*

# Test connection
psql -U postgres -d postgres
# Enter password: postgres_password
# Type \q to exit
```

**Add to PATH:**
Add PostgreSQL bin directory to your PATH:
- Default location: `C:\Program Files\PostgreSQL\16\bin`
- System Properties → Environment Variables → Path → Edit → New

### 2. Redis

**Installation:**

Option A - Using winget:
```powershell
winget install Redis.Redis
```

Option B - Manual installation:
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Download the latest `.msi` file
3. Run the installer
4. Default port: `6379`

**Install as Windows Service:**
```powershell
# Navigate to Redis directory (e.g., C:\Program Files\Redis)
cd "C:\Program Files\Redis"

# Install service
redis-server --service-install

# Start service
redis-server --service-start
```

**Verify:**
```powershell
# Check if service is running
Get-Service Redis

# Test connection
redis-cli ping
# Should return: PONG
```

### 3. RabbitMQ

**Installation:**

1. **Install Erlang first** (RabbitMQ dependency):
   - Download from: https://www.erlang.org/downloads
   - Run the installer
   - Default installation is fine

2. **Install RabbitMQ**:
   - Download from: https://www.rabbitmq.com/download.html
   - Run the installer
   - Default port: `5672` (AMQP), `15672` (Management UI)

**Configure RabbitMQ:**
```powershell
# Enable management plugin
rabbitmq-plugins enable rabbitmq_management

# Create user
rabbitmqctl add_user rabbitmq rabbitmq_password

# Set user as administrator
rabbitmqctl set_user_tags rabbitmq administrator

# Set permissions
rabbitmqctl set_permissions -p / rabbitmq ".*" ".*" ".*"
```

**Verify:**
```powershell
# Check if service is running
Get-Service RabbitMQ

# Access management UI
# Open browser: http://localhost:15672
# Login: rabbitmq / rabbitmq_password
```

### 4. MinIO

**Installation:**

1. Download MinIO for Windows from: https://min.io/download
2. Create directory for MinIO:
   ```powershell
   mkdir C:\minio
   mkdir C:\minio\data
   ```
3. Move `minio.exe` to `C:\minio\`

**Create Start Script:**

Create `C:\minio\start-minio.bat`:
```batch
@echo off
cd C:\minio
minio.exe server C:\minio\data --console-address :9001
```

**Run MinIO:**
```powershell
# Start MinIO
cd C:\minio
.\start-minio.bat

# Or run directly
.\minio.exe server C:\minio\data --console-address :9001
```

**Verify:**
- API: http://localhost:9000
- Console: http://localhost:9001
- Default credentials: `minioadmin` / `minioadmin`

**Optional - Install as Service:**

Use NSSM (Non-Sucking Service Manager):
1. Download from: https://nssm.cc/download
2. Extract `nssm.exe`
3. Install service:
   ```powershell
   nssm install MinIO "C:\minio\minio.exe" "server C:\minio\data --console-address :9001"
   nssm start MinIO
   ```

### 5. Temporal

**Installation:**

Using winget:
```powershell
winget install Temporal.CLI
```

Manual installation:
1. Download from: https://docs.temporal.io/cli#install
2. Extract to a directory (e.g., `C:\temporal`)
3. Add to PATH

**Verify:**
```powershell
temporal --version
```

**Note**: Temporal doesn't need to be installed as a service. You'll start it when needed.

### 6. Ollama

**Installation:**

1. Download Ollama for Windows from: https://ollama.ai/download
2. Run the installer
3. Ollama will start automatically as a service

**Download LLM Model:**
```powershell
# This will download ~4.7GB
ollama pull llama3.1:8b
```

**Verify:**
```powershell
# Check if Ollama is running
curl http://localhost:11434

# List installed models
ollama list
```

## Database Setup

After installing PostgreSQL, initialize the database:

```powershell
# Navigate to project directory
cd "C:\Users\RUSHIKESH\Desktop\Project RDx 00"

# Run initialization script
.\init_database.ps1
```

This script will:
- Create the `idea_engine` database
- Install `pgvector` and `uuid-ossp` extensions
- Create the schema
- Set up permissions

## Application Setup

### 1. Configure Environment

```powershell
# Copy environment file
copy .env.example .env

# Edit .env if you changed any default settings
notepad .env
```

### 2. Install Backend Dependencies

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

cd ..
```

### 3. Install Frontend Dependencies

```powershell
cd frontend

# Install dependencies
npm install

cd ..
```

## Running the Application

### Start All Services

```powershell
# Start infrastructure services
.\start_services.ps1
```

This will start:
- PostgreSQL
- Redis
- RabbitMQ
- MinIO
- Temporal
- Ollama

### Start Backend (in new terminal)

```powershell
cd backend
.\start_backend.ps1
```

Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Start Temporal Worker (in new terminal)

```powershell
cd backend
.\start_worker.ps1
```

### Start Frontend (in new terminal)

```powershell
cd frontend
.\start_frontend.ps1
```

Frontend will be available at: http://localhost:3000

## Troubleshooting

### PostgreSQL Issues

**Service won't start:**
```powershell
# Check service status
Get-Service postgresql*

# Start service manually
Start-Service postgresql-x64-16

# Check logs
# Location: C:\Program Files\PostgreSQL\16\data\log
```

**Connection refused:**
- Verify PostgreSQL is running
- Check if port 5432 is available: `netstat -ano | findstr :5432`
- Verify `pg_hba.conf` allows local connections

**pgvector not found:**
- Reinstall pgvector extension
- Verify installation: `SELECT * FROM pg_available_extensions WHERE name = 'vector';`

### Redis Issues

**Service won't start:**
```powershell
# Check service
Get-Service Redis

# Start manually
redis-server

# Check configuration
# Location: C:\Program Files\Redis\redis.windows.conf
```

### RabbitMQ Issues

**Management UI not accessible:**
```powershell
# Enable management plugin
rabbitmq-plugins enable rabbitmq_management

# Restart service
Restart-Service RabbitMQ
```

**User authentication failed:**
```powershell
# Reset user
rabbitmqctl delete_user rabbitmq
rabbitmqctl add_user rabbitmq rabbitmq_password
rabbitmqctl set_user_tags rabbitmq administrator
rabbitmqctl set_permissions -p / rabbitmq ".*" ".*" ".*"
```

### MinIO Issues

**Console not accessible:**
- Verify MinIO is running
- Check if ports 9000 and 9001 are available
- Try accessing: http://localhost:9001

**Permission denied:**
- Run MinIO with administrator privileges
- Check directory permissions for `C:\minio\data`

### Temporal Issues

**Server won't start:**
```powershell
# Kill existing processes
Get-Process temporal | Stop-Process -Force

# Start fresh
temporal server start-dev
```

**Database connection failed:**
- Temporal dev server uses SQLite by default
- For PostgreSQL, check connection string in config

### Ollama Issues

**Model not found:**
```powershell
# List models
ollama list

# Pull model again
ollama pull llama3.1:8b
```

**Service not responding:**
```powershell
# Restart Ollama service
Restart-Service Ollama

# Or run manually
ollama serve
```

### Backend Issues

**Import errors:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Database migration errors:**
```powershell
# Reset migrations
alembic downgrade base
alembic upgrade head
```

**Port 8000 already in use:**
```powershell
# Find process
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### Frontend Issues

**Module not found:**
```powershell
# Clear cache and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item -Recurse -Force .next
npm install
```

**Port 3000 already in use:**
```powershell
# Find and kill process
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

## Performance Tips

1. **Use SSD**: Install services on SSD for better performance
2. **Increase RAM**: 32GB recommended for running all services
3. **GPU for Ollama**: Use NVIDIA GPU for faster LLM inference
4. **Disable Antivirus**: Temporarily disable for development directories
5. **Close Unused Apps**: Free up system resources

## Security Notes

⚠️ **Warning**: Default passwords are used for development. Change them for production:

- PostgreSQL: `postgres_password`
- RabbitMQ: `rabbitmq_password`
- MinIO: `minioadmin` / `minioadmin`

## Next Steps

After successful setup:

1. Generate your first ideas: `make generate-ideas`
2. Explore the dashboard: http://localhost:3000
3. Check API docs: http://localhost:8000/docs
4. Monitor workflows: http://localhost:8080

## Getting Help

If you encounter issues:

1. Check service logs
2. Verify all services are running: `make health-check`
3. Review error messages in terminal
4. Check port availability
5. Ensure all dependencies are installed

---

**Happy Coding!** 🚀
