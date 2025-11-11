"""
FastAPI application initialization
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.dependencies import faiss_manager
from app.api.endpoints import health, ask_stream

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    Handles startup and shutdown tasks
    """
    # Startup: Load FAISS index
    logger.info("Starting application...")
    try:
        faiss_manager.load()
        logger.info("FAISS index loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load FAISS index: {e}")
        logger.warning("Application starting without FAISS index")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="BERT LLM Chat API",
    description="RAG-based chat API with FAISS and Groq",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured with origins: {settings.allowed_origins_list}")

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(ask_stream.router, tags=["Chat"])

logger.info("API routers registered")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BERT LLM Chat API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {"ask_stream": "POST /ask-stream"},
    }
