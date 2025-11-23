"""
LLM-as-a-Judge Evaluation

Uses an LLM (via Groq API) to evaluate answer quality on multiple dimensions:
- Relevance: Does the answer address the question?
- Faithfulness: Is the answer grounded in the context?
- Completeness: Does it fully answer all aspects?
- Coherence: Is it well-structured and clear?

Usage:
    python llm_judge.py --dataset test_dataset.json --backend-url http://localhost:8080
"""

import json
import argparse
import requests
import time
from typing import List, Dict, Any
from pathlib import Path
import os

try:
    from groq import Groq

    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("WARNING: Groq library not available. Install with: pip install groq")


JUDGE_PROMPT_TEMPLATE = """You are an expert evaluator for question-answering systems. Your task is to evaluate the quality of an answer given a question and the retrieved context.

Question: {question}

Retrieved Context:
{context}

Generated Answer:
{answer}

Ground Truth (for reference):
{ground_truth}

Please evaluate the answer on the following criteria and provide scores from 1-5 (1=very poor, 5=excellent):

1. RELEVANCE: Does the answer directly address the question asked?
2. FAITHFULNESS: Is the answer grounded in and supported by the provided context?
3. COMPLETENESS: Does the answer fully address all aspects of the question?
4. COHERENCE: Is the answer well-structured, clear, and easy to understand?

Also provide a brief explanation of your scores.

Respond ONLY with valid JSON in this exact format:
{{
  "relevance": <score 1-5>,
  "faithfulness": <score 1-5>,
  "completeness": <score 1-5>,
  "coherence": <score 1-5>,
  "reasoning": "<brief explanation>"
}}"""


def load_test_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """Load test dataset"""
    with open(dataset_path, "r") as f:
        return json.load(f)


def query_backend(question: str, backend_url: str) -> Dict[str, Any]:
    """Query RAG backend and get response"""
    url = f"{backend_url}/ask-stream"
    payload = {"question": question, "history": []}

    try:
        response = requests.post(url, json=payload, timeout=30, stream=True)
        response.raise_for_status()

        full_answer = ""

        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str.strip() and data_str != "[DONE]":
                        try:
                            data = json.loads(data_str)
                            # Backend sends "content" not "token"
                            if "content" in data:
                                full_answer += data["content"]
                            # Sources not available in stream
                        except json.JSONDecodeError:
                            continue

        return {"answer": full_answer.strip(), "sources": []}
    except Exception as e:
        print(f"Error querying backend: {e}")
        return {"answer": "", "sources": []}


def evaluate_with_llm_judge(
    question: str, answer: str, context: str, ground_truth: str, client: Groq
) -> Dict[str, Any]:
    """
    Use LLM to evaluate answer quality
    """
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        question=question, context=context, answer=answer, ground_truth=ground_truth
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=500,
        )

        response_text = response.choices[0].message.content.strip()

        # Try to parse JSON response
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()

        result = json.loads(response_text)
        return result

    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        print(f"Response was: {response_text}")
        return {
            "relevance": 0,
            "faithfulness": 0,
            "completeness": 0,
            "coherence": 0,
            "reasoning": "Failed to parse LLM response",
        }
    except Exception as e:
        print(f"Error calling LLM judge: {e}")
        return {
            "relevance": 0,
            "faithfulness": 0,
            "completeness": 0,
            "coherence": 0,
            "reasoning": f"Error: {str(e)}",
        }


def evaluate_all_questions(
    test_data: List[Dict[str, Any]], backend_url: str, client: Groq
) -> List[Dict[str, Any]]:
    """
    Evaluate all test questions using LLM-as-judge
    """
    print(f"\nEvaluating {len(test_data)} questions with LLM judge...")

    results = []

    for i, item in enumerate(test_data, 1):
        question = item["question"]
        ground_truth = item["ground_truth"]

        print(f"\n[{i}/{len(test_data)}] {question[:60]}...")

        # Query backend
        response = query_backend(question, backend_url)
        answer = response["answer"]
        sources = response["sources"]

        # Format context
        context = "\n\n".join(
            [f"[Chunk {i+1}] {src.get('text', '')}" for i, src in enumerate(sources)]
        )

        if not answer:
            print("  WARNING: Empty answer")
            answer = "No answer generated"

        if not context:
            context = "No context retrieved"

        # Evaluate with LLM judge
        evaluation = evaluate_with_llm_judge(
            question, answer, context, ground_truth, client
        )

        result = {
            "question_id": item.get("question_id", i),
            "question": question,
            "answer": answer,
            "ground_truth": ground_truth,
            "evaluation": evaluation,
            "category": item.get("category", "unknown"),
            "difficulty": item.get("difficulty", "unknown"),
        }

        results.append(result)

        # Print scores
        eval_scores = evaluation
        print(f"  Relevance: {eval_scores.get('relevance', 0)}/5")
        print(f"  Faithfulness: {eval_scores.get('faithfulness', 0)}/5")
        print(f"  Completeness: {eval_scores.get('completeness', 0)}/5")
        print(f"  Coherence: {eval_scores.get('coherence', 0)}/5")

        # Rate limiting
        time.sleep(1)

    return results


def compute_aggregate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregate statistics"""
    metrics = ["relevance", "faithfulness", "completeness", "coherence"]

    aggregates = {}
    for metric in metrics:
        scores = [r["evaluation"].get(metric, 0) for r in results]
        valid_scores = [s for s in scores if s > 0]

        if valid_scores:
            aggregates[metric] = {
                "mean": sum(valid_scores) / len(valid_scores),
                "min": min(valid_scores),
                "max": max(valid_scores),
                "num_evaluated": len(valid_scores),
            }
        else:
            aggregates[metric] = {"mean": 0, "min": 0, "max": 0, "num_evaluated": 0}

    # Overall score (normalized to 0-1)
    overall_scores = []
    for r in results:
        eval_scores = r["evaluation"]
        valid = [eval_scores.get(m, 0) for m in metrics if eval_scores.get(m, 0) > 0]
        if valid:
            overall_scores.append(sum(valid) / (5 * len(valid)))

    aggregates["overall"] = {
        "mean": sum(overall_scores) / len(overall_scores) if overall_scores else 0,
        "num_evaluated": len(overall_scores),
    }

    return aggregates


def print_results(aggregates: Dict[str, Any], results: List[Dict[str, Any]]):
    """Pretty print evaluation results"""
    print("\n" + "=" * 60)
    print("LLM-AS-JUDGE EVALUATION RESULTS")
    print("=" * 60)

    print(f"\nNumber of questions evaluated: {len(results)}")

    print("\nAggregate Scores (out of 5):")
    for metric in ["relevance", "faithfulness", "completeness", "coherence"]:
        data = aggregates[metric]
        print(
            f"  {metric.capitalize():.<30} {data['mean']:.2f} (min={data['min']}, max={data['max']})"
        )

    overall = aggregates["overall"]["mean"]
    print(f"\nOverall Score (normalized):..... {overall:.3f}")

    print("=" * 60)

    if overall >= 0.85:
        print("\n✅ Excellent answer quality!")
    elif overall >= 0.70:
        print("\n✓ Good answer quality")
    elif overall >= 0.55:
        print("\n⚠ Moderate answer quality - room for improvement")
    else:
        print("\n❌ Poor answer quality - needs significant improvement")


def main():
    parser = argparse.ArgumentParser(description="LLM-as-Judge evaluation")
    parser.add_argument(
        "--dataset", type=str, default="test_dataset.json", help="Path to test dataset"
    )
    parser.add_argument(
        "--backend-url",
        type=str,
        default="http://localhost:8080",
        help="Backend API URL",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/llm_judge_results.json",
        help="Output path for results",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Groq API key (or set GROQ_API_KEY env var)",
    )

    args = parser.parse_args()

    if not GROQ_AVAILABLE:
        print("ERROR: Groq library not available. Install with:")
        print("  pip install groq")
        return 1

    # Get API key
    api_key = args.api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        print(
            "ERROR: GROQ_API_KEY not set. Please provide via --api-key or environment variable."
        )
        return 1

    # Initialize Groq client
    client = Groq(api_key=api_key)

    # Load test dataset
    print(f"Loading test dataset from: {args.dataset}")
    test_data = load_test_dataset(args.dataset)

    # Evaluate
    results = evaluate_all_questions(test_data, args.backend_url, client)

    # Compute aggregates
    aggregates = compute_aggregate_metrics(results)

    # Print results
    print_results(aggregates, results)

    # Save results
    output_data = {"aggregates": aggregates, "detailed_results": results}

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
