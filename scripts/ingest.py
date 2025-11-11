#!/usr/bin/env python3
"""
One-shot ingestion script for PDF manuals.
Reads PDFs, creates embeddings, and builds a FAISS index.
"""

import json
import os
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

# Configuration from environment variables
SCRIPT_DIR = Path(__file__).parent
SOURCE_PDF_DIR = SCRIPT_DIR / os.getenv("SOURCE_PDF_DIR", "./source_pdfs")
OUTPUT_DIR = SCRIPT_DIR / os.getenv("OUTPUT_DIR", "../backend/faiss_index")
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract all text from a PDF file."""
    print(f"Reading PDF: {pdf_path.name}")
    reader = PdfReader(str(pdf_path))
    text = ""
    for page_num, page in enumerate(reader.pages, 1):
        text += page.extract_text()
    print(f"  - Extracted {len(reader.pages)} pages")
    return text


def split_text_into_chunks(text: str, source_file: str) -> List[Dict[str, str]]:
    """Split text into chunks using RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = splitter.split_text(text)

    # Create chunk objects with metadata
    chunk_objects = []
    for i, chunk_text in enumerate(chunks):
        chunk_objects.append(
            {
                "text": chunk_text,
                "source": source_file,
                "chunk_id": i,
            }
        )

    print(f"  - Created {len(chunk_objects)} chunks")
    return chunk_objects


def process_all_pdfs() -> List[Dict[str, str]]:
    """Process all PDFs in the source directory."""
    pdf_files = list(SOURCE_PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {SOURCE_PDF_DIR}")
        print("Please place PDF manuals in scripts/source_pdfs/ directory")
        return []

    print(f"\nFound {len(pdf_files)} PDF file(s)")
    print("=" * 50)

    all_chunks = []
    for pdf_path in pdf_files:
        text = extract_text_from_pdf(pdf_path)
        chunks = split_text_into_chunks(text, pdf_path.name)
        all_chunks.extend(chunks)

    print("=" * 50)
    print(f"Total chunks created: {len(all_chunks)}\n")
    return all_chunks


def create_faiss_index(chunks: List[Dict[str, str]]) -> tuple:
    """Create FAISS index from text chunks."""
    print("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("Creating embeddings...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    # Convert to numpy array and normalize
    embeddings = np.array(embeddings).astype("float32")
    faiss.normalize_L2(embeddings)

    # Create FAISS index
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(
        dimension
    )  # Inner product (cosine similarity after normalization)
    index.add(embeddings)

    print(f"  - Index dimension: {dimension}")
    print(f"  - Number of vectors: {index.ntotal}")

    return index, chunks


def save_index_and_metadata(index, chunks: List[Dict[str, str]]):
    """Save FAISS index and metadata to disk."""
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save FAISS index
    index_path = OUTPUT_DIR / "index.faiss"
    faiss.write_index(index, str(index_path))
    print(f"\nSaved FAISS index to: {index_path}")

    # Save metadata
    metadata_path = OUTPUT_DIR / "index.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved metadata to: {metadata_path}")

    print(f"\nIngestion complete! Files saved in {OUTPUT_DIR}")


def main():
    """Main ingestion pipeline."""
    print("\n" + "=" * 50)
    print("FAISS Index Ingestion Script")
    print("=" * 50)

    # Check if source directory exists
    if not SOURCE_PDF_DIR.exists():
        print(f"\nError: Source directory not found: {SOURCE_PDF_DIR}")
        print("Creating directory...")
        SOURCE_PDF_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Please place PDF files in {SOURCE_PDF_DIR}")
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
