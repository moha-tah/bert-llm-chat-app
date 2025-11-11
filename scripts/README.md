# Data Ingestion Scripts

This directory contains the scripts required for processing and ingesting data for the Bert LLM chat application. The main script, `ingest.py`, is designed to read PDF files, divide them into text chunks, generate embeddings (vector representations) for each chunk, and finally build a FAISS index for efficient semantic similarity search. This index is then used by the application's backend to provide relevant answers to user messages.

## Description

The `ingest.py` script automates the data preparation pipeline for the language model. Here are the key steps involved:

1.  **Text Extraction**: Reads all PDF files located in the `source_pdfs` directory.
2.  **Chunking**: Splits the extracted text into smaller, manageable segments (chunks) using a recursive strategy.
3.  **Embedding Generation**: Uses a `sentence-transformers` model to convert each text chunk into a numerical vector (embedding).
4.  **FAISS Indexing**: Creates a FAISS (Facebook AI Similarity Search) index from the embeddings. This index allows for the rapid retrieval of text chunks that are most relevant to a given query.
5.  **Saving**: Saves the FAISS index (`index.faiss`) and the associated metadata (`index.json`) to an output directory, ready to be used by the application's backend.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python (version 3.11 or higher)
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management

## Installation

Follow these steps to set up the development environment:

1.  **Navigate to the scripts directory:**

    ```bash
    cd /path/to/your/project/bert-llm-chat-app/scripts
    ```

2.  **Install dependencies:**

    Use Poetry to install all the required Python libraries, which are listed in the `pyproject.toml` file.

    ```bash
    poetry install
    ```

## Configuration

1.  **Place PDF files:**

    Add all the PDF documents you want to process into the `scripts/source_pdfs/` directory. If the directory does not exist, the script will create it for you on the first run.

2.  **Environment Variables (Optional):**

    You can configure the script by creating a `.env` file in the root of the `scripts` directory. Here are the variables you can override:

    - `SOURCE_PDF_DIR`: Path to the directory containing the PDFs (default: `./source_pdfs`).
    - `OUTPUT_DIR`: Path to the directory where the index will be saved (default: `../backend/faiss_index`).
    - `EMBEDDING_MODEL`: Name of the `sentence-transformers` model to use (default: `sentence-transformers/all-MiniLM-L6-v2`).
    - `CHUNK_SIZE`: Maximum size of the text chunks (default: `1000`).
    - `CHUNK_OVERLAP`: Number of overlapping characters between chunks (default: `200`).

    Example `.env` file:

    ```
    SOURCE_PDF_DIR=./my_pdfs
    OUTPUT_DIR=../my_backend/index
    EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
    ```

## Usage

To run the ingestion process, execute the following command from the `scripts` directory:

```bash
poetry run python ingest.py
```

The script will display its progress in the console, including the files being processed, the creation of embeddings, and the building of the index.

## Output Files

Upon successful completion of the script, you will find the following files in the specified output directory (default `../backend/faiss_index/`):

- `index.faiss`: The binary file for the FAISS index.
- `index.json`: A JSON file containing metadata, including the original text of each chunk and its source.
