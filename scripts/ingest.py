#!/usr/bin/env python3
"""
One-shot ingestion script for PDF manuals.
Reads PDFs, creates embeddings, and builds a FAISS index.
"""

import json
import os
import logging
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configuration from environment variables
SCRIPT_DIR = Path(__file__).parent
SOURCE_PDF_DIR = SCRIPT_DIR / os.getenv("SOURCE_PDF_DIR", "./source_pdfs")
OUTPUT_DIR = SCRIPT_DIR / os.getenv("OUTPUT_DIR", "../backend/faiss_index")
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))


Chunk = Dict[str, str]
Chunks = List[Chunk]


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract all text from a PDF file."""
    logging.info(f"Reading PDF: {pdf_path.name}")
    reader = PdfReader(str(pdf_path))
    text = ""
    for page_num, page in enumerate(reader.pages, 1):
        text += page.extract_text()
    logging.info(f"  - Extracted {len(reader.pages)} pages")
    return text


def split_text_into_chunks(text: str, source_file: str) -> Chunks:
    """Split text into chunks using RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = splitter.split_text(text)

    # Create chunk objects with metadata
    chunk_objects: Chunks = []
    for i, chunk_text in enumerate(chunks):
        chunk_objects.append(
            {
                "text": chunk_text,
                "source": source_file,
                "chunk_id": i,
            }
        )

    logging.info(f"  - Created {len(chunk_objects)} chunks")
    return chunk_objects


def process_all_pdfs() -> Chunks:
    """Process all PDFs in the source directory."""
    pdf_files = list(SOURCE_PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        logging.warning(f"No PDF files found in {SOURCE_PDF_DIR}")
        logging.warning("Please place PDF manuals in scripts/source_pdfs/ directory")
        return []

    logging.info(f"Found {len(pdf_files)} PDF file(s)")

    all_chunks = []
    for pdf_path in pdf_files:
        text = extract_text_from_pdf(pdf_path)
        chunks = split_text_into_chunks(text, pdf_path.name)
        all_chunks.extend(chunks)

    logging.info(f"Total chunks created: {len(all_chunks)}")
    return all_chunks


def create_faiss_index(chunks: Chunks) -> tuple:
    """Create FAISS index from text chunks."""
    logging.info("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    logging.info("Creating embeddings...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    # Convert to numpy array and normalize
    embeddings = np.array(embeddings).astype("float32")
    faiss.normalize_L2(embeddings)

    # Create FAISS index
    logging.info("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(
        dimension
    )  # Inner product (cosine similarity after normalization)
    index.add(embeddings)

    logging.info(f"  - Index dimension: {dimension}")
    logging.info(f"  - Number of vectors: {index.ntotal}")

    return index, chunks


def save_index_and_metadata(index, chunks: Chunks):
    """Save FAISS index and metadata to disk."""
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save FAISS index
    index_path = OUTPUT_DIR / "index.faiss"
    faiss.write_index(index, str(index_path))
    logging.info(f"Saved FAISS index to: {index_path}")

    # Save metadata
    metadata_path = OUTPUT_DIR / "index.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    logging.info(f"Saved metadata to: {metadata_path}")

    logging.info(f"Ingestion complete! Files saved in {OUTPUT_DIR}")


def main():
    """Main ingestion pipeline."""
    logging.info("FAISS Index Ingestion Script started")

    # Check if source directory exists
    if not SOURCE_PDF_DIR.exists():
        logging.error(f"Source directory not found: {SOURCE_PDF_DIR}")
        logging.info("Creating directory...")
        SOURCE_PDF_DIR.mkdir(parents=True, exist_ok=True)
        logging.info(f"Please place PDF files in {SOURCE_PDF_DIR}")
        return

    # Process PDFs
    chunks = process_all_pdfs()
    if not chunks:
        return

    # Create FAISS index
    index, chunks = create_faiss_index(chunks)

    # Save to disk
    save_index_and_metadata(index, chunks)


if __name__ == "__main__":
    main()
