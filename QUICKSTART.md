# Quick Start - Project RDx 00 (Local Setup)

## 🚀 First Time Setup

### 1. Install Services
```powershell
.\setup_local.ps1
```
Follow the interactive guide to install:
- PostgreSQL 16 + pgvector
- Redis
- RabbitMQ
- MinIO
- Temporal
- Ollama

### 2. Initialize Database
```powershell
.\init_database.ps1
```

### 3. Install Dependencies
```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### 4. Download LLM Model
```powershell
ollama pull llama3.1:8b
```

## 🎯 Daily Development

### Start Services (Terminal 1)
```powershell
.\start_services.ps1
```

### Start Backend (Terminal 2)
```powershell
cd backend
.\start_backend.ps1
```

### Start Frontend (Terminal 3)
```powershell
cd frontend
.\start_frontend.ps1
```

## 🔗 Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Temporal UI | http://localhost:8080 | - |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| RabbitMQ Mgmt | http://localhost:15672 | rabbitmq / rabbitmq_password |

## 🛠️ Common Commands

```powershell
# Health check
make health-check

# Generate ideas
make generate-ideas

# Run tests
make test

# Stop all services
.\stop_services.ps1

# Clean up
make clean
```

## 🐛 Quick Troubleshooting

**Service won't start?**
```powershell
Get-Service <service-name>
Start-Service <service-name>
```

**Port already in use?**
```powershell
netstat -ano | findstr :<port>
taskkill /PID <PID> /F
```

**Database issues?**
```powershell
.\init_database.ps1
```

## 📚 Documentation

- Full README: [README.md](README.md)
- Setup Guide: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Walkthrough: See artifacts

## 🎉 You're Ready!

Visit http://localhost:3000 to start generating ideas!
