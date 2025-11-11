"""
Dependencies and shared resources
"""
import json
import logging
from typing import Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)


class FAISSIndexManager:
    """Manages FAISS index and embeddings in memory"""

    def __init__(self):
        self.index: Optional[faiss.Index] = None
        self.chunks: Optional[list[dict]] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.is_loaded = False

    def load(self):
        """Load FAISS index, chunks, and embedding model into memory"""
        try:
            logger.info(f"Loading FAISS index from {settings.faiss_index_path}")

            # Load FAISS index
            if not settings.faiss_index_path.exists():
                raise FileNotFoundError(f"FAISS index not found at {settings.faiss_index_path}")

            self.index = faiss.read_index(str(settings.faiss_index_path))
            logger.info(f"FAISS index loaded successfully with {self.index.ntotal} vectors")

            # Load chunks metadata
            if not settings.faiss_chunks_path.exists():
                raise FileNotFoundError(f"Chunks file not found at {settings.faiss_chunks_path}")

            with open(settings.faiss_chunks_path, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
            logger.info(f"Loaded {len(self.chunks)} chunks from metadata")

            # Load embedding model
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")

            self.is_loaded = True
            logger.info("FAISS index loaded and ready")

        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            raise

    def vectorize_query(self, query: str) -> np.ndarray:
        """Convert query text to embedding vector"""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not loaded")

        # Generate embedding
        embedding = self.embedding_model.encode([query])[0]

        # Normalize for cosine similarity (IndexFlatIP expects normalized vectors)
        embedding = embedding / np.linalg.norm(embedding)

        return embedding.astype('float32')

    def search(self, query: str, k: int = None) -> list[dict]:
        """
        Search for similar chunks given a query

        Args:
            query: User question
            k: Number of results to return (defaults to settings.K_NEIGHBORS)

        Returns:
            List of chunk dictionaries with similarity scores
        """
        if not self.is_loaded:
            raise RuntimeError("FAISS index not loaded")

        if k is None:
            k = settings.K_NEIGHBORS

        # Vectorize query
        query_vector = self.vectorize_query(query)

        # Search FAISS index
        distances, indices = self.index.search(
            query_vector.reshape(1, -1),
            k
        )

        # Build results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["similarity_score"] = float(distance)
                results.append(chunk)

        return results

    def get_status(self) -> dict:
        """Get status information about the loaded index"""
        if not self.is_loaded:
            return {
                "loaded": False,
                "message": "FAISS index not loaded"
            }

        return {
            "loaded": True,
            "num_vectors": self.index.ntotal if self.index else 0,
            "num_chunks": len(self.chunks) if self.chunks else 0,
            "embedding_model": settings.EMBEDDING_MODEL,
            "k_neighbors": settings.K_NEIGHBORS
        }


# Global instance
faiss_manager = FAISSIndexManager()


def get_faiss_manager() -> FAISSIndexManager:
    """Dependency injection for FAISS manager"""
    return faiss_manager
