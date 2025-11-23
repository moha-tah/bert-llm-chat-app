"""
Retrieval Evaluation Metrics

Evaluates the FAISS vector search quality using standard retrieval metrics:
- Recall@K: Proportion of relevant documents retrieved in top K
- Precision@K: Precision of top K results
- Mean Reciprocal Rank (MRR): Position of first relevant document
- NDCG@K: Normalized Discounted Cumulative Gain

Usage:
    python evaluate_retrieval.py --dataset test_dataset.json --faiss-index ../backend/faiss_index
"""

import json
import argparse
import numpy as np
from typing import List, Dict, Any, Set
from pathlib import Path
import sys

# Add backend path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("WARNING: Required libraries not available")


def load_faiss_index(index_dir: str):
    """Load FAISS index and chunks"""
    index_path = Path(index_dir) / "index.faiss"
    chunks_path = Path(index_dir) / "index.json"

    print(f"Loading FAISS index from: {index_path}")
    index = faiss.read_index(str(index_path))

    print(f"Loading chunks from: {chunks_path}")
    with open(chunks_path, 'r') as f:
        chunks = json.load(f)

    print(f"Loaded {index.ntotal} vectors and {len(chunks)} chunks")
    return index, chunks


def load_test_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """Load test dataset"""
    with open(dataset_path, 'r') as f:
        return json.load(f)


def search_faiss(
    query: str,
    model: SentenceTransformer,
    index: faiss.Index,
    k: int = 10
) -> List[int]:
    """
    Search FAISS index and return top K chunk IDs
    """
    # Generate embedding
    query_embedding = model.encode([query], normalize_embeddings=True)

    # Search
    distances, indices = index.search(query_embedding.astype('float32'), k)

    # Return list of indices (chunk IDs)
    return indices[0].tolist()


def recall_at_k(ground_truth: Set[int], retrieved: List[int], k: int) -> float:
    """
    Recall@K: Proportion of relevant documents in top K results

    Args:
        ground_truth: Set of relevant chunk IDs
        retrieved: List of retrieved chunk IDs (ranked)
        k: Cutoff position
    """
    if not ground_truth:
        return 0.0

    retrieved_k = set(retrieved[:k])
    relevant_retrieved = len(ground_truth & retrieved_k)

    return relevant_retrieved / len(ground_truth)


def precision_at_k(ground_truth: Set[int], retrieved: List[int], k: int) -> float:
    """
    Precision@K: Proportion of relevant documents in top K

    Args:
        ground_truth: Set of relevant chunk IDs
        retrieved: List of retrieved chunk IDs (ranked)
        k: Cutoff position
    """
    if k == 0:
        return 0.0

    retrieved_k = set(retrieved[:k])
    relevant_retrieved = len(ground_truth & retrieved_k)

    return relevant_retrieved / k


def mean_reciprocal_rank(ground_truth: Set[int], retrieved: List[int]) -> float:
    """
    MRR: Reciprocal of the rank of the first relevant document

    Args:
        ground_truth: Set of relevant chunk IDs
        retrieved: List of retrieved chunk IDs (ranked)
    """
    for rank, doc_id in enumerate(retrieved, 1):
        if doc_id in ground_truth:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ground_truth: Set[int], retrieved: List[int], k: int) -> float:
    """
    NDCG@K: Normalized Discounted Cumulative Gain at K

    Args:
        ground_truth: Set of relevant chunk IDs
        retrieved: List of retrieved chunk IDs (ranked)
        k: Cutoff position
    """
    # Compute DCG@K
    dcg = 0.0
    for i, doc_id in enumerate(retrieved[:k], 1):
        if doc_id in ground_truth:
            # Binary relevance: 1 if relevant, 0 otherwise
            dcg += 1.0 / np.log2(i + 1)

    # Compute Ideal DCG (IDCG)
    # In ideal ranking, all relevant docs are at the top
    num_relevant = min(len(ground_truth), k)
    idcg = sum(1.0 / np.log2(i + 1) for i in range(1, num_relevant + 1))

    if idcg == 0:
        return 0.0

    return dcg / idcg


def evaluate_retrieval(
    test_data: List[Dict[str, Any]],
    model: SentenceTransformer,
    index: faiss.Index,
    k_values: List[int] = [1, 3, 5, 10]
) -> Dict[str, Any]:
    """
    Evaluate retrieval performance across all test queries
    """
    print(f"\nEvaluating retrieval on {len(test_data)} queries...")

    all_recalls = {k: [] for k in k_values}
    all_precisions = {k: [] for k in k_values}
    all_ndcgs = {k: [] for k in k_values}
    all_mrrs = []

    for i, item in enumerate(test_data, 1):
        question = item['question']
        ground_truth = set(item['relevant_chunk_ids'])

        # Retrieve top K documents
        max_k = max(k_values)
        retrieved = search_faiss(question, model, index, k=max_k)

        # Compute metrics for different K values
        for k in k_values:
            recall = recall_at_k(ground_truth, retrieved, k)
            precision = precision_at_k(ground_truth, retrieved, k)
            ndcg = ndcg_at_k(ground_truth, retrieved, k)

            all_recalls[k].append(recall)
            all_precisions[k].append(precision)
            all_ndcgs[k].append(ndcg)

        # MRR (computed once per query)
        mrr = mean_reciprocal_rank(ground_truth, retrieved)
        all_mrrs.append(mrr)

        print(f"[{i}/{len(test_data)}] {question[:50]}... | Recall@5={recall:.3f} MRR={mrr:.3f}")

    # Aggregate results
    results = {
        "num_queries": len(test_data),
        "recall": {f"recall@{k}": float(np.mean(all_recalls[k])) for k in k_values},
        "precision": {f"precision@{k}": float(np.mean(all_precisions[k])) for k in k_values},
        "ndcg": {f"ndcg@{k}": float(np.mean(all_ndcgs[k])) for k in k_values},
        "mrr": float(np.mean(all_mrrs))
    }

    return results


def print_results(results: Dict[str, Any]):
    """Pretty print retrieval metrics"""
    print("\n" + "="*60)
    print("RETRIEVAL EVALUATION RESULTS")
    print("="*60)

    print(f"\nNumber of test queries: {results['num_queries']}")

    print("\nRecall@K:")
    for metric, value in results['recall'].items():
        print(f"  {metric:.<30} {value:.4f}")

    print("\nPrecision@K:")
    for metric, value in results['precision'].items():
        print(f"  {metric:.<30} {value:.4f}")

    print("\nNDCG@K:")
    for metric, value in results['ndcg'].items():
        print(f"  {metric:.<30} {value:.4f}")

    print(f"\nMean Reciprocal Rank (MRR):..... {results['mrr']:.4f}")

    print("="*60)

    # Assessment
    recall_5 = results['recall']['recall@5']
    if recall_5 >= 0.90:
        print("\n✅ Excellent retrieval performance!")
    elif recall_5 >= 0.75:
        print("\n✓ Good retrieval performance")
    elif recall_5 >= 0.60:
        print("\n⚠ Moderate retrieval performance")
    else:
        print("\n❌ Poor retrieval performance - consider re-indexing or using better embeddings")


def main():
    parser = argparse.ArgumentParser(description="Evaluate retrieval metrics")
    parser.add_argument(
        "--dataset",
        type=str,
        default="test_dataset.json",
        help="Path to test dataset"
    )
    parser.add_argument(
        "--faiss-index",
        type=str,
        default="../backend/faiss_index",
        help="Path to FAISS index directory"
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model name"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/retrieval_results.json",
        help="Output path for results"
    )

    args = parser.parse_args()

    if not DEPENDENCIES_AVAILABLE:
        print("ERROR: Missing dependencies. Install with:")
        print("  pip install sentence-transformers faiss-cpu")
        return 1

    # Load test dataset
    print(f"Loading test dataset from: {args.dataset}")
    test_data = load_test_dataset(args.dataset)

    # Load FAISS index
    index, chunks = load_faiss_index(args.faiss_index)

    # Load embedding model
    print(f"Loading embedding model: {args.embedding_model}")
    model = SentenceTransformer(args.embedding_model)

    # Evaluate
    results = evaluate_retrieval(
        test_data,
        model,
        index,
        k_values=[1, 3, 5, 10]
    )

    # Print results
    print_results(results)

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
