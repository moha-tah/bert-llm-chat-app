"""
Application configuration and settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 1024

    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    # FAISS Configuration
    FAISS_INDEX_DIR: str = "./faiss_index"
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"
    K_NEIGHBORS: int = 5

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse ALLOWED_ORIGINS as a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def faiss_index_path(self) -> Path:
        """Get path to FAISS index file"""
        return Path(self.FAISS_INDEX_DIR) / "index.faiss"

    @property
    def faiss_chunks_path(self) -> Path:
        """Get path to chunks JSON file"""
        return Path(self.FAISS_INDEX_DIR) / "index.json"


# Global settings instance
settings = Settings()
