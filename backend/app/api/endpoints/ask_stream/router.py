import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.config import settings
from app.dependencies import FAISSIndexManager, get_faiss_manager
from .schemas import ChatRequest
from .services import stream_groq_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ask-stream")
async def ask_stream(
    request: ChatRequest, faiss_manager: FAISSIndexManager = Depends(get_faiss_manager)
):
    """
    RAG endpoint with streaming response

    Retrieves relevant document chunks and streams LLM response

    Args:
        request: Chat request with question
        faiss_manager: FAISS index manager dependency

    Returns:
        StreamingResponse with text/plain content
    """
    try:
        # Check if FAISS index is loaded
        if not faiss_manager.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="FAISS index not loaded. Please check server logs.",
            )

        logger.info(f"Processing question: {request.question[:100]}...")

        # Search for relevant chunks
        context_chunks = faiss_manager.search(
            query=request.question, k=settings.K_NEIGHBORS
        )

        logger.info(f"Retrieved {len(context_chunks)} context chunks")

        # Use temperature from request or default from settings
        temperature = (
            request.temperature
            if request.temperature is not None
            else settings.GROQ_TEMPERATURE
        )

        # Convert history to dict format
        history = (
            [msg.model_dump() for msg in request.history] if request.history else []
        )

        # Return streaming response with SSE media type
        return StreamingResponse(
            stream_groq_response(
                request.question,
                context_chunks,
                settings.GROQ_MODEL,
                temperature,
                history,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ask_stream endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
