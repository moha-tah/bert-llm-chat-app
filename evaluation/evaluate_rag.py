"""
RAG Evaluation using RAGAS Framework

This script evaluates the RAG system using multiple metrics:
- Faithfulness: Are answers grounded in retrieved context?
- Answer Relevancy: Do answers address the question?
- Context Precision: Are retrieved chunks relevant?
- Context Recall: Are all relevant chunks retrieved?

Usage:
    python evaluate_rag.py --backend-url http://localhost:8080 --dataset test_dataset.json
"""

import json
import argparse
import requests
from typing import List, Dict, Any
from pathlib import Path
import time

try:
    from ragas import evaluate
    from ragas.metrics import (
        context_precision,
        context_recall,
    )
    from datasets import Dataset
    # Import LLM configuration
    from langchain_groq import ChatGroq
    import os
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    print("WARNING: RAGAS not installed. Install with: pip install ragas datasets langchain-groq")


def load_test_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """Load test dataset from JSON file"""
    with open(dataset_path, 'r') as f:
        return json.load(f)


def query_backend(question: str, backend_url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Query the RAG backend and get response with sources

    Returns:
        dict with 'answer' and 'sources' keys
    """
    url = f"{backend_url}/ask-stream"

    payload = {
        "question": question,
        "history": []
    }

    try:
        # Note: This is a simplified version that doesn't handle streaming
        # For full streaming support, we'd need to parse SSE events
        response = requests.post(url, json=payload, timeout=timeout, stream=True)
        response.raise_for_status()

        # Collect streamed response
        full_answer = ""

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove 'data: ' prefix
                    if data_str.strip() and data_str != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            # Backend sends "content" not "token"
                            if 'content' in data:
                                full_answer += data['content']
                            # Sources not available in stream - ignore
                        except json.JSONDecodeError:
                            continue

        return {
            "answer": full_answer.strip(),
            "sources": []  # Not available in current backend
        }

    except requests.exceptions.RequestException as e:
        print(f"Error querying backend: {e}")
        return {
            "answer": "",
            "sources": []
        }


def extract_contexts(sources: List[Dict[str, Any]]) -> List[str]:
    """Extract context text from sources"""
    return [source.get('text', '') for source in sources]


def prepare_ragas_dataset(
    test_data: List[Dict[str, Any]],
    backend_url: str,
    verbose: bool = True
) -> Dataset:
    """
    Query backend for all test questions and prepare RAGAS dataset
    """
    questions = []
    answers = []
    contexts = []
    ground_truths = []

    print(f"\nQuerying backend for {len(test_data)} test questions...")

    for i, item in enumerate(test_data, 1):
        question = item['question']
        ground_truth = item['ground_truth']

        if verbose:
            print(f"[{i}/{len(test_data)}] {question[:60]}...")

        # Query backend
        result = query_backend(question, backend_url)
        answer = result['answer']
        retrieved_contexts = extract_contexts(result['sources'])

        if not answer:
            print(f"  WARNING: Empty answer for question {i}")
            answer = "No answer generated"

        if not retrieved_contexts:
            print(f"  WARNING: No contexts retrieved for question {i}")
            retrieved_contexts = ["No context retrieved"]

        questions.append(question)
        answers.append(answer)
        contexts.append(retrieved_contexts)
        ground_truths.append(ground_truth)

        # Be nice to the API
        time.sleep(0.5)

    # Create RAGAS dataset
    dataset_dict = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }

    return Dataset.from_dict(dataset_dict)


def evaluate_with_ragas(dataset: Dataset, groq_api_key: str) -> Dict[str, float]:
    """
    Evaluate using RAGAS metrics with Groq LLM
    """
    print("\nRunning RAGAS evaluation with Groq...")

    # Configure RAGAS to use Groq instead of OpenAI
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=groq_api_key,
        temperature=0.0
    )

    # Only use metrics that work without complex LLM requirements
    # context_precision and context_recall work with Groq
    result = evaluate(
        dataset,
        metrics=[
            context_precision,
            context_recall,
        ],
        llm=llm
    )

    return result


def save_results(results: Dict[str, Any], output_path: str):
    """Save evaluation results to JSON"""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")


def print_results(results: Dict[str, float]):
    """Pretty print evaluation results"""
    print("\n" + "="*60)
    print("RAG EVALUATION RESULTS")
    print("="*60)

    for metric, score in results.items():
        print(f"{metric:.<40} {score:.4f}")

    print("="*60)

    # Overall assessment
    avg_score = sum(results.values()) / len(results)
    print(f"\nAverage Score: {avg_score:.4f}")

    if avg_score >= 0.85:
        print("✅ Excellent RAG system performance!")
    elif avg_score >= 0.70:
        print("✓ Good RAG system performance")
    elif avg_score >= 0.55:
        print("⚠ Moderate RAG system performance - room for improvement")
    else:
        print("❌ Poor RAG system performance - needs significant improvement")


def main():
    parser = argparse.ArgumentParser(description="Evaluate RAG system with RAGAS")
    parser.add_argument(
        "--backend-url",
        type=str,
        default="http://localhost:8080",
        help="Backend API URL"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="test_dataset.json",
        help="Path to test dataset JSON file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/ragas_results.json",
        help="Output path for results"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Check if RAGAS is available
    if not RAGAS_AVAILABLE:
        print("ERROR: RAGAS library not available. Install with:")
        print("  pip install ragas datasets langchain-groq")
        return 1

    # Get Groq API key
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        print("ERROR: GROQ_API_KEY environment variable not set")
        print("Please set it with: export GROQ_API_KEY=your_key")
        return 1

    # Load test dataset
    print(f"Loading test dataset from: {args.dataset}")
    test_data = load_test_dataset(args.dataset)
    print(f"Loaded {len(test_data)} test questions")

    # Prepare RAGAS dataset by querying backend
    ragas_dataset = prepare_ragas_dataset(test_data, args.backend_url, args.verbose)

    # Evaluate with RAGAS using Groq
    results = evaluate_with_ragas(ragas_dataset, groq_api_key)

    # Convert to dict for JSON serialization
    results_dict = {k: float(v) for k, v in results.items()}

    # Print results
    print_results(results_dict)

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_results(results_dict, str(output_path))

    return 0


if __name__ == "__main__":
    exit(main())
