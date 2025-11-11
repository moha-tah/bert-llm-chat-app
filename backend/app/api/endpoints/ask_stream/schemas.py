from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""

    question: str = Field(..., min_length=1, description="User question")
    temperature: Optional[float] = Field(
        None, ge=0.0, le=2.0, description="Temperature for LLM response generation"
    )
