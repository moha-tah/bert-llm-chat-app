import logging
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Groq client
groq_client = Groq(api_key=settings.GROQ_API_KEY)


def build_prompt(question: str, context_chunks: list[dict]) -> str:
    """
    Build prompt with retrieved context chunks
    Args:
        question: User question
        context_chunks: List of relevant document chunks
    Returns:
        Formatted prompt string
    """
    # Build context from chunks
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        source = chunk.get("source", "Unknown")
        text = chunk.get("text", "")
        score = chunk.get("similarity_score", 0.0)
        context_parts.append(
            f"[Part {i}] (Document: {source}, Relevance: {score:.3f})\n{text}"
        )

    context = "\n\n".join(context_parts)

    # Build full prompt
    prompt = f"""You are an intelligent assistant that answers questions based on provided context from documents.

Context from relevant parts:
{context}

User Question: {question}

Instructions:
- Answer the question based ONLY on the information provided in the context above
- If the context doesn't contain enough information to answer the question, say so clearly
- If the question doesn't need any context, answer based on your knowledge
- Be concise and accurate
- Cite which document(s) you're referencing in your answer (at the end after jumping to the next line)

Answer:"""

    return prompt


async def stream_groq_response(
    question: str,
    context_chunks: list[dict],
    model: str,
    temperature: float,
    history: list[dict] = None,
):
    """
    Generator function that streams response from Groq API in SSE format
    Args:
        question: User question
        context_chunks: Retrieved context chunks
        model: Groq model to use
        temperature: Temperature for response generation
        history: Conversation history (list of messages)
    Yields:
        Server-Sent Events formatted chunks
    """
    try:
        # Build prompt with context
        prompt = build_prompt(question, context_chunks)

        logger.info(f"Calling Groq API with model: {model}")

        # Build messages array with history
        messages = []

        # Add conversation history if provided
        if history:
            for msg in history:
                messages.append(
                    {"role": msg.get("role"), "content": msg.get("content")}
                )

        # Add current question with context
        messages.append({"role": "user", "content": prompt})

        logger.info(f"Messages count: {len(messages)}")

        # Call Groq API with streaming
        stream = groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=settings.GROQ_MAX_TOKENS,
            stream=True,
        )

        # Stream response chunks in SSE format
        import json

        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                # Format as Server-Sent Event with JSON payload
                event_data = json.dumps({"content": content})
                yield f"data: {event_data}\n\n"

        # Send completion event
        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"Error during Groq streaming: {e}")
        import json

        error_data = json.dumps({"error": str(e)})
        yield f"data: {error_data}\n\n"
