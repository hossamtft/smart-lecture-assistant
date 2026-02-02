"""
Smart Lecture Assistant - FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
import os

# Create FastAPI application
app = FastAPI(
    title="Smart Lecture Assistant API",
    description="AI-powered lecture analysis with cross-lecture topic detection and RAG-based Q&A",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Initialize database tables
    init_db()

    print(f"🚀 Smart Lecture Assistant API started")
    print(f"📚 Upload directory: {settings.upload_dir}")
    print(f"🤖 LLM Provider: {settings.llm_provider}")
    print(f"🔢 Embedding Provider: {settings.embedding_provider}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Lecture Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider
    }


# Import and include routers
from .api.routes import lectures
app.include_router(lectures.router, prefix="/api/lectures", tags=["lectures"])

# To be added:
# from .api.routes import topics, query, dashboard
# app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
# app.include_router(query.router, prefix="/api/query", tags=["query"])
# app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
