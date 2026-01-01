# Unlimited Tech Business Idea Generator & Research Engine

A simplified, autonomous system that generates tech business ideas, performs research, scores them, and presents everything through a modern web dashboard.

## 🚀 Features

- **AI-Powered Idea Generation**: Generate business ideas using Google Gemini API
- **Research Agent**: Automated web research and competitor analysis
- **Comprehensive Scoring**: Multi-factor evaluation system
- **Modern Dashboard**: Next.js 14 frontend with real-time updates
- **100% Local**: Runs entirely on your machine with minimal dependencies

## 🏗️ Simplified Architecture

### Backend
- **FastAPI**: Async Python API server
- **SQLite**: Lightweight database with async support
- **Google Gemini**: LLM for idea generation and analysis
- **Simple File Storage**: Local filesystem for reports and artifacts

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS + shadcn/ui**: Modern UI components

## 📋 Prerequisites

- **Windows 10/11**
- **Python 3.11+**
- **Node.js 20+**
- **8GB+ RAM**
- **Google Gemini API Key** (free tier available)

## 🚀 Quick Start

### 1. Clone and Setup

```powershell
cd "Project RDx 00"
```

### 2. Configure Environment

The `.env` file is already configured. Just add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Get your free API key at: https://makersuite.google.com/app/apikey

### 3. Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```powershell
cd frontend
npm install
```

### 5. Start Backend

```powershell
cd backend
python -m app.main
```

The backend API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 6. Start Frontend

In a new terminal:

```powershell
cd frontend
npm run dev
```

The frontend will be available at:
- **Dashboard**: http://localhost:3000

## 📖 Usage

### Generate Ideas via API

```powershell
curl -X POST http://localhost:8000/api/v1/ideas/generate -H "Content-Type: application/json" -d "{\"count\": 5, \"category\": \"AI Tools\"}"
```

### Run Complete Pipeline

```powershell
curl -X POST http://localhost:8000/api/v1/workflows/pipeline -H "Content-Type: application/json" -d "{\"idea_count\": 10, \"auto_research\": true, \"auto_score\": true}"
```

### View Results

Navigate to http://localhost:3000 to:
- Browse all generated ideas
- View research artifacts
- See score breakdowns
- Check rankings

## 🛠️ Development

### Backend Development

```powershell
cd backend

# Run tests
pytest tests/ -v

# Test database
python test_db.py

# Test idea generation
python test_idea_generation.py
```

### Frontend Development

```powershell
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

## 📁 Project Structure

```
Project RDx 00/
├── backend/
│   ├── app/
│   │   ├── agents/           # AI agents (idea generator, research, scoring)
│   │   ├── api/              # FastAPI routes
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic (LLM, storage, scraper)
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   └── main.py           # FastAPI app
│   ├── tests/                # Test suite
│   ├── requirements.txt      # Python dependencies
│   └── idea_engine.db        # SQLite database
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   └── lib/              # Utilities and API client
│   └── package.json
├── .env                      # Environment configuration
└── README.md
```

## 🧪 Testing

### Test Database

```powershell
cd backend
python test_db.py
```

Expected output:
- Database initializes successfully
- Idea is saved and retrieved

### Test Idea Generation

```powershell
cd backend
python test_idea_generation.py
```

Expected output:
- Generates ideas using Gemini API
- Saves ideas to database

**Note**: May fail if Gemini API rate limit is exceeded. This is normal for free tier.

### Test Backend API

```powershell
cd backend
pytest tests/ -v
```

## 🐛 Troubleshooting

### Gemini API Rate Limit

If you see rate limit errors:
- Wait 24 hours for quota reset (free tier)
- Or upgrade to paid tier for higher limits

### Database Issues

```powershell
# Delete and reinitialize database
cd backend
del idea_engine.db
python test_db.py
```

### Port Already in Use

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F
```

## 🔌 Service Access URLs

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📝 API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/ideas/generate` - Generate ideas
- `GET /api/v1/ideas/` - List ideas
- `POST /api/v1/research/start` - Start research
- `POST /api/v1/scoring/score` - Score an idea
- `POST /api/v1/workflows/pipeline` - Trigger full pipeline

## 🎯 What Changed from Original

This is a **simplified version** that removes complex infrastructure:

**Removed:**
- ❌ PostgreSQL → Using SQLite
- ❌ Redis → Using in-memory caching
- ❌ RabbitMQ → Using direct async calls
- ❌ MinIO → Using local file storage
- ❌ Temporal → Using FastAPI BackgroundTasks
- ❌ Playwright → Using simple HTTP requests

**Benefits:**
- ✅ Much easier to setup and run
- ✅ Fewer dependencies and points of failure
- ✅ Faster development iteration
- ✅ Same core functionality

## 📄 License

Open source - use as you wish.

## 🙏 Acknowledgments

Built with:
- FastAPI
- Next.js
- Google Gemini
- SQLite
- And many other amazing open-source projects
