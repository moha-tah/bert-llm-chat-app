"""
Embedding Model Benchmark

Compares different embedding models on:
- Inference speed (queries per second)
- Memory usage
- Embedding dimensions
- Model size
- Retrieval quality (Recall@5)

Usage:
    python benchmark_embeddings.py --dataset test_dataset.json --faiss-index ../backend/faiss_index
"""

import json
import argparse
import time
import numpy as np
from typing import List, Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import psutil
    import os
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("WARNING: Required libraries not available")


# Models to benchmark
MODELS_TO_COMPARE = [
    "sentence-transformers/all-MiniLM-L6-v2",      # Current (384-dim)
    "sentence-transformers/all-MiniLM-L12-v2",     # Larger MiniLM (384-dim)
    "sentence-transformers/all-mpnet-base-v2",     # MPNet (768-dim)
    "BAAI/bge-small-en-v1.5",                       # BGE small (384-dim)
    "BAAI/bge-base-en-v1.5",                        # BGE base (768-dim)
]


def load_test_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """Load test dataset"""
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    # Use subset for faster benchmarking
    return data[:10]  # First 10 questions


def load_faiss_chunks(index_dir: str) -> List[Dict[str, Any]]:
    """Load chunk texts from FAISS index"""
    chunks_path = Path(index_dir) / "index.json"
    with open(chunks_path, 'r') as f:
        return json.load(f)


def benchmark_model(
    model_name: str,
    test_queries: List[str],
    chunks: List[Dict[str, Any]],
    ground_truth: List[List[int]]
) -> Dict[str, Any]:
    """
    Benchmark a single embedding model
    """
    print(f"\nBenchmarking: {model_name}")
    print("-" * 60)

    # Memory before loading
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024  # MB

    # Load model
    load_start = time.time()
    model = SentenceTransformer(model_name)
    load_time = time.time() - load_start

    # Memory after loading
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    model_memory = mem_after - mem_before

    # Get model info
    embedding_dim = model.get_sentence_embedding_dimension()

    # Measure query encoding speed
    print("  Testing query encoding speed...")
    start_time = time.time()
    query_embeddings = model.encode(
        test_queries,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    query_time = time.time() - start_time
    queries_per_sec = len(test_queries) / query_time

    # Measure chunk encoding speed
    print("  Testing chunk encoding speed...")
    chunk_texts = [chunk['text'] for chunk in chunks[:100]]  # First 100 chunks
    start_time = time.time()
    chunk_embeddings = model.encode(
        chunk_texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    chunk_time = time.time() - start_time
    chunks_per_sec = len(chunk_texts) / chunk_time

    # Build temporary FAISS index for retrieval quality test
    print("  Testing retrieval quality...")
    all_chunk_embeddings = model.encode(
        [chunk['text'] for chunk in chunks],
        normalize_embeddings=True,
        show_progress_bar=False
    )

    # Create FAISS index
    index = faiss.IndexFlatIP(embedding_dim)
    index.add(all_chunk_embeddings.astype('float32'))

    # Test retrieval quality (Recall@5)
    recalls = []
    for query_emb, gt_ids in zip(query_embeddings, ground_truth):
        query_emb_2d = query_emb.reshape(1, -1).astype('float32')
        distances, indices = index.search(query_emb_2d, 5)
        retrieved = set(indices[0].tolist())
        relevant = set(gt_ids)
        if relevant:
            recall = len(retrieved & relevant) / len(relevant)
            recalls.append(recall)

    avg_recall_at_5 = np.mean(recalls) if recalls else 0.0

    results = {
        "model": model_name,
        "embedding_dim": embedding_dim,
        "model_memory_mb": round(model_memory, 2),
        "load_time_sec": round(load_time, 2),
        "query_encoding_speed_qps": round(queries_per_sec, 2),
        "chunk_encoding_speed_cps": round(chunks_per_sec, 2),
        "avg_time_per_query_ms": round((query_time / len(test_queries)) * 1000, 2),
        "recall_at_5": round(avg_recall_at_5, 4)
    }

    print(f"  ✓ Embedding dim: {embedding_dim}")
    print(f"  ✓ Memory: {model_memory:.0f} MB")
    print(f"  ✓ Query speed: {queries_per_sec:.1f} q/s")
    print(f"  ✓ Recall@5: {avg_recall_at_5:.4f}")

    return results


def print_comparison_table(results: List[Dict[str, Any]]):
    """Print nice comparison table"""
    print("\n" + "="*100)
    print("EMBEDDING MODEL BENCHMARK RESULTS")
    print("="*100)

    # Header
    print(f"\n{'Model':<40} {'Dim':>6} {'Mem(MB)':>8} {'Q/s':>8} {'ms/q':>8} {'Recall@5':>10}")
    print("-" * 100)

    # Rows
    for r in results:
        model_name = r['model'].split('/')[-1][:38]
        print(f"{model_name:<40} {r['embedding_dim']:>6} {r['model_memory_mb']:>8} "
              f"{r['query_encoding_speed_qps']:>8.1f} {r['avg_time_per_query_ms']:>8.1f} "
              f"{r['recall_at_5']:>10.4f}")

    print("="*100)

    # Recommendations
    print("\n📊 ANALYSIS:")

    # Find best for each metric
    fastest = max(results, key=lambda x: x['query_encoding_speed_qps'])
    smallest = min(results, key=lambda x: x['model_memory_mb'])
    best_quality = max(results, key=lambda x: x['recall_at_5'])

    print(f"  🚀 Fastest: {fastest['model'].split('/')[-1]} ({fastest['query_encoding_speed_qps']:.1f} q/s)")
    print(f"  💾 Smallest: {smallest['model'].split('/')[-1]} ({smallest['model_memory_mb']:.0f} MB)")
    print(f"  🎯 Best Quality: {best_quality['model'].split('/')[-1]} (Recall@5={best_quality['recall_at_5']:.4f})")

    # Overall recommendation
    print("\n💡 RECOMMENDATION:")
    print("  For production deployment with balanced speed/quality trade-off:")

    # Score based on normalized metrics
    for r in results:
        speed_score = r['query_encoding_speed_qps'] / max(x['query_encoding_speed_qps'] for x in results)
        memory_score = 1 - (r['model_memory_mb'] / max(x['model_memory_mb'] for x in results))
        quality_score = r['recall_at_5'] / max(x['recall_at_5'] for x in results)
        r['overall_score'] = (speed_score + memory_score + quality_score) / 3

    recommended = max(results, key=lambda x: x['overall_score'])
    print(f"  → {recommended['model']}")
    print(f"    Balanced score: {recommended['overall_score']:.3f}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark embedding models")
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
        "--output",
        type=str,
        default="reports/embedding_benchmark.json",
        help="Output path for results"
    )
    parser.add_argument(
        "--models",
        type=str,
        nargs='+',
        default=None,
        help="Specific models to benchmark (optional)"
    )

    args = parser.parse_args()

    if not DEPENDENCIES_AVAILABLE:
        print("ERROR: Missing dependencies. Install with:")
        print("  pip install sentence-transformers faiss-cpu psutil")
        return 1

    # Determine models to test
    models = args.models if args.models else MODELS_TO_COMPARE

    print("="*100)
    print("EMBEDDING MODEL BENCHMARK")
    print("="*100)
    print(f"\nTesting {len(models)} models...")

    # Load test data
    test_data = load_test_dataset(args.dataset)
    test_queries = [item['question'] for item in test_data]
    ground_truth = [item['relevant_chunk_ids'] for item in test_data]

    print(f"Using {len(test_queries)} test queries")

    # Load chunks
    chunks = load_faiss_chunks(args.faiss_index)
    print(f"Loaded {len(chunks)} chunks for indexing")

    # Benchmark each model
    all_results = []
    for model_name in models:
        try:
            result = benchmark_model(model_name, test_queries, chunks, ground_truth)
            all_results.append(result)
        except Exception as e:
            print(f"  ❌ Error benchmarking {model_name}: {e}")
            continue

    # Print comparison
    if all_results:
        print_comparison_table(all_results)

        # Save results
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults saved to: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
