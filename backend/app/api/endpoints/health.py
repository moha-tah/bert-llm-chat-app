"""
Health check endpoint
"""
from fastapi import APIRouter, Depends
from app.dependencies import FAISSIndexManager, get_faiss_manager

router = APIRouter()


@router.get("/health")
async def health_check(
    faiss_manager: FAISSIndexManager = Depends(get_faiss_manager)
):
    """
    Health check endpoint for AWS App Runner and monitoring

    Returns application status and FAISS index information
    """
    faiss_status = faiss_manager.get_status()

    return {
        "status": "ok",
        "faiss_index": faiss_status
    }
