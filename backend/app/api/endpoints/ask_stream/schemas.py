from pydantic import BaseModel, Field
from typing import Optional, List


class Message(BaseModel):
    """Single message in conversation history"""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""

    question: str = Field(..., min_length=1, description="User question")
    history: Optional[List[Message]] = Field(
        default=[], description="Conversation history"
    )
    temperature: Optional[float] = Field(
        None, ge=0.0, le=2.0, description="Temperature for LLM response generation"
    )
