from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import settings
from app.database import init_db, close_db
from app.api.routes import ideas, research, scoring, reports, workflows

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Idea Engine API...")
    
    # Initialize database (optional - will retry on first request if fails)
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        logger.warning("Backend will start anyway - database will be initialized on first request")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Idea Engine API...")
    try:
        await close_db()
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")


# Create FastAPI application
app = FastAPI(
    title="Unlimited Tech Business Idea Generator & Research Engine",
    description="Multi-agent system for generating, researching, scoring, and ranking business ideas",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "idea-engine-api",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Unlimited Tech Business Idea Generator & Research Engine API",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(ideas.router, prefix="/api/v1/ideas", tags=["Ideas"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"])
app.include_router(scoring.router, prefix="/api/v1/scoring", tags=["Scoring"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.log_level == "DEBUG" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=1 if settings.api_reload else settings.api_workers,
    )
