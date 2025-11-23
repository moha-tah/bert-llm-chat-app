#!/bin/bash

# Run All RAG Evaluations
# Usage: ./run_all_evaluations.sh
#
# Prerequisites:
#   - Poetry installed: curl -sSL https://install.python-poetry.org | python3 -
#   - Dependencies installed: poetry install

set -e  # Exit on error

echo "=================================="
echo "RAG SYSTEM EVALUATION SUITE"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"
FAISS_INDEX="${FAISS_INDEX:-../backend/faiss_index}"
DATASET="${DATASET:-test_dataset.json}"

# Check if backend is running
echo -e "${YELLOW}Checking backend availability...${NC}"
if curl -s -f "${BACKEND_URL}/health" > /dev/null; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo "❌ Backend is not accessible at ${BACKEND_URL}"
    echo "Please start the backend first:"
    echo "  cd ../backend && docker-compose up"
    exit 1
fi

# Check for Groq API key
if [ -z "$GROQ_API_KEY" ]; then
    echo -e "${YELLOW}⚠ GROQ_API_KEY not set. LLM-as-judge evaluation will be skipped.${NC}"
    echo "To enable it: export GROQ_API_KEY=your_key"
    SKIP_LLM_JUDGE=1
else
    echo -e "${GREEN}✓ GROQ_API_KEY is set${NC}"
    SKIP_LLM_JUDGE=0
fi

echo ""
echo "=================================="
echo "1/5 Running Retrieval Evaluation"
echo "=================================="
poetry run python evaluate_retrieval.py \
    --dataset "$DATASET" \
    --faiss-index "$FAISS_INDEX" \
    --output reports/retrieval_results.json

echo ""
echo "=================================="
echo "2/5 Running RAGAS Evaluation"
echo "=================================="
poetry run python evaluate_rag.py \
    --backend-url "$BACKEND_URL" \
    --dataset "$DATASET" \
    --output reports/ragas_results.json

if [ $SKIP_LLM_JUDGE -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "3/5 Running LLM-as-Judge"
    echo "=================================="
    poetry run python llm_judge.py \
        --backend-url "$BACKEND_URL" \
        --dataset "$DATASET" \
        --output reports/llm_judge_results.json
else
    echo ""
    echo "=================================="
    echo "3/5 Skipping LLM-as-Judge (no API key)"
    echo "=================================="
fi

echo ""
echo "=================================="
echo "4/5 Running Embedding Benchmark"
echo "=================================="
# Only test current model by default for speed
poetry run python benchmark_embeddings.py \
    --dataset "$DATASET" \
    --faiss-index "$FAISS_INDEX" \
    --models sentence-transformers/all-MiniLM-L6-v2 \
    --output reports/embedding_benchmark.json

echo ""
echo "=================================="
echo "5/5 Generating Report"
echo "=================================="
poetry run python generate_report.py --output-dir reports/

echo ""
echo -e "${GREEN}=================================="
echo "EVALUATION COMPLETE!"
echo "==================================${NC}"
echo ""
echo "Results saved in reports/:"
echo "  - retrieval_results.json"
echo "  - ragas_results.json"
if [ $SKIP_LLM_JUDGE -eq 0 ]; then
    echo "  - llm_judge_results.json"
fi
echo "  - embedding_benchmark.json"
echo "  - evaluation_report.md"
echo "  - dashboard.html"
echo ""
echo "Open the dashboard:"
echo "  open reports/dashboard.html"
echo ""
echo "View the report:"
echo "  cat reports/evaluation_report.md"
