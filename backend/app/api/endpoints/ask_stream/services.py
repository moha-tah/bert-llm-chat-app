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
- Cite which document(s) you're referencing in your answer

Answer:"""

    return prompt


async def stream_groq_response(
    question: str, context_chunks: list[dict], model: str, temperature: float
):
    """
    Generator function that streams response from Groq API
    Args:
        question: User question
        context_chunks: Retrieved context chunks
        model: Groq model to use
        temperature: Temperature for response generation
    Yields:
        Chunks of text from streaming response
    """
    try:
        # Build prompt with context
        prompt = build_prompt(question, context_chunks)

        logger.info(f"Prompt: {prompt}")
        logger.info(f"Calling Groq API with model: {model}")

        # Call Groq API with streaming
        stream = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=settings.GROQ_MAX_TOKENS,
            stream=True,
        )

        # Stream response chunks
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        logger.error(f"Error during Groq streaming: {e}")
        yield f"\n\n[Error: {str(e)}]"
