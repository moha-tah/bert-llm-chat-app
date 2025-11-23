"""
Generate Evaluation Report

Combines all evaluation results and generates:
- Markdown report for README
- HTML dashboard with interactive charts

Usage:
    python generate_report.py --output-dir reports/
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("WARNING: Plotly not available. Install with: pip install plotly")


def load_json_if_exists(filepath: str) -> Optional[Dict[str, Any]]:
    """Load JSON file if it exists"""
    path = Path(filepath)
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return None


def generate_markdown_report(
    ragas_results: Optional[Dict],
    retrieval_results: Optional[Dict],
    llm_judge_results: Optional[Dict],
    embedding_benchmark: Optional[Dict]
) -> str:
    """Generate Markdown report"""

    report = f"""# RAG System Evaluation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

This report presents a comprehensive evaluation of the RAG (Retrieval-Augmented Generation) system across multiple dimensions: answer quality, retrieval performance, and infrastructure efficiency.

"""

    # RAGAS Results
    if ragas_results:
        report += """## 1. RAG Quality Metrics (RAGAS Framework)

RAGAS (RAG Assessment) provides end-to-end evaluation of the RAG pipeline:

| Metric | Score | Description |
|--------|-------|-------------|
"""
        for metric, score in ragas_results.items():
            descriptions = {
                'faithfulness': 'Are answers grounded in retrieved context?',
                'answer_relevancy': 'Do answers address the question?',
                'context_precision': 'Are retrieved chunks relevant?',
                'context_recall': 'Are all relevant chunks retrieved?'
            }
            desc = descriptions.get(metric, '')
            report += f"| {metric.replace('_', ' ').title()} | **{score:.4f}** | {desc} |\n"

        avg_score = sum(ragas_results.values()) / len(ragas_results)
        report += f"\n**Average Score:** {avg_score:.4f}\n\n"

    # Retrieval Results
    if retrieval_results:
        report += """## 2. Retrieval Performance Metrics

Standard information retrieval metrics measuring the quality of vector search:

| Metric | Score | Description |
|--------|-------|-------------|
"""
        if 'recall' in retrieval_results:
            for metric, score in retrieval_results['recall'].items():
                k = metric.split('@')[1]
                report += f"| Recall@{k} | **{score:.4f}** | Proportion of relevant docs in top {k} |\n"

        if 'precision' in retrieval_results:
            for metric, score in retrieval_results['precision'].items():
                k = metric.split('@')[1]
                report += f"| Precision@{k} | **{score:.4f}** | Precision of top {k} results |\n"

        if 'mrr' in retrieval_results:
            report += f"| MRR | **{retrieval_results['mrr']:.4f}** | Mean Reciprocal Rank |\n"

        if 'ndcg' in retrieval_results:
            for metric, score in retrieval_results['ndcg'].items():
                k = metric.split('@')[1]
                report += f"| NDCG@{k} | **{score:.4f}** | Normalized Discounted Cumulative Gain |\n"

        report += "\n"

    # LLM Judge Results
    if llm_judge_results and 'aggregates' in llm_judge_results:
        aggregates = llm_judge_results['aggregates']
        report += """## 3. Qualitative Assessment (LLM-as-Judge)

Human-like evaluation using LLaMA 3.3 70B as a judge:

| Criterion | Score (out of 5) | Description |
|-----------|------------------|-------------|
"""
        for metric in ['relevance', 'faithfulness', 'completeness', 'coherence']:
            if metric in aggregates:
                score = aggregates[metric]['mean']
                descriptions = {
                    'relevance': 'Does answer address the question?',
                    'faithfulness': 'Is answer grounded in context?',
                    'completeness': 'Does it fully answer all aspects?',
                    'coherence': 'Is it well-structured and clear?'
                }
                report += f"| {metric.capitalize()} | **{score:.2f}** | {descriptions[metric]} |\n"

        if 'overall' in aggregates:
            overall = aggregates['overall']['mean']
            report += f"\n**Overall Quality Score:** {overall:.3f} (normalized)\n\n"

    # Embedding Benchmark
    if embedding_benchmark:
        report += """## 4. Embedding Model Benchmark

Comparison of different embedding models:

| Model | Dim | Memory (MB) | Speed (q/s) | Recall@5 |
|-------|-----|-------------|-------------|----------|
"""
        for result in embedding_benchmark[:5]:  # Top 5 models
            model_name = result['model'].split('/')[-1]
            report += (f"| {model_name} | {result['embedding_dim']} | "
                      f"{result['model_memory_mb']} | "
                      f"{result['query_encoding_speed_qps']:.1f} | "
                      f"{result.get('recall_at_5', 0):.4f} |\n")

        report += "\n"

    # Recommendations
    report += """## 5. Key Findings & Recommendations

### Strengths
"""

    findings = []

    if ragas_results:
        avg_ragas = sum(ragas_results.values()) / len(ragas_results)
        if avg_ragas >= 0.85:
            findings.append("✅ **Excellent RAG quality** - System produces highly accurate and relevant answers")

    if retrieval_results and 'recall' in retrieval_results:
        recall_5 = retrieval_results['recall'].get('recall@5', 0)
        if recall_5 >= 0.85:
            findings.append("✅ **Strong retrieval performance** - FAISS index effectively finds relevant documents")

    if llm_judge_results and 'aggregates' in llm_judge_results:
        overall = llm_judge_results['aggregates'].get('overall', {}).get('mean', 0)
        if overall >= 0.80:
            findings.append("✅ **High answer coherence** - Responses are well-structured and clear")

    for finding in findings:
        report += f"- {finding}\n"

    report += """
### Areas for Improvement

"""

    improvements = []

    if ragas_results:
        if ragas_results.get('context_recall', 1.0) < 0.75:
            improvements.append("⚠️ Consider increasing K neighbors or improving chunk overlap for better context recall")

    if retrieval_results and 'precision' in retrieval_results:
        precision_5 = retrieval_results['precision'].get('precision@5', 1.0)
        if precision_5 < 0.80:
            improvements.append("⚠️ Some irrelevant chunks are being retrieved - consider chunk size or embedding quality")

    if not improvements:
        improvements.append("✓ No major issues identified - system performing well")

    for improvement in improvements:
        report += f"- {improvement}\n"

    report += """
---

**Note:** This evaluation was performed on a curated test dataset. Results may vary with different queries and domains.
"""

    return report


def create_html_dashboard(
    ragas_results: Optional[Dict],
    retrieval_results: Optional[Dict],
    llm_judge_results: Optional[Dict],
    embedding_benchmark: Optional[Dict]
) -> str:
    """Generate interactive HTML dashboard with Plotly"""

    if not PLOTLY_AVAILABLE:
        return "<html><body><h1>Plotly not available. Install with: pip install plotly</h1></body></html>"

    # Create subplots
    num_charts = sum([
        1 if ragas_results else 0,
        1 if retrieval_results else 0,
        1 if llm_judge_results else 0,
        1 if embedding_benchmark else 0
    ])

    if num_charts == 0:
        return "<html><body><h1>No evaluation results available</h1></body></html>"

    rows = (num_charts + 1) // 2
    fig = make_subplots(
        rows=rows,
        cols=2,
        subplot_titles=tuple(filter(None, [
            "RAG Quality (RAGAS)" if ragas_results else None,
            "Retrieval Metrics" if retrieval_results else None,
            "LLM Judge Scores" if llm_judge_results else None,
            "Embedding Benchmark" if embedding_benchmark else None
        ])),
        specs=[[{"type": "bar"}, {"type": "bar"}] for _ in range(rows)]
    )

    chart_idx = 1

    # RAGAS results
    if ragas_results:
        row = (chart_idx - 1) // 2 + 1
        col = (chart_idx - 1) % 2 + 1

        metrics = list(ragas_results.keys())
        scores = list(ragas_results.values())

        fig.add_trace(
            go.Bar(
                x=metrics,
                y=scores,
                marker=dict(color='lightblue'),
                name="RAGAS"
            ),
            row=row,
            col=col
        )

        chart_idx += 1

    # Retrieval results
    if retrieval_results and 'recall' in retrieval_results:
        row = (chart_idx - 1) // 2 + 1
        col = (chart_idx - 1) % 2 + 1

        metrics = list(retrieval_results['recall'].keys())
        scores = list(retrieval_results['recall'].values())

        fig.add_trace(
            go.Bar(
                x=metrics,
                y=scores,
                marker=dict(color='lightgreen'),
                name="Recall"
            ),
            row=row,
            col=col
        )

        chart_idx += 1

    # LLM Judge results
    if llm_judge_results and 'aggregates' in llm_judge_results:
        row = (chart_idx - 1) // 2 + 1
        col = (chart_idx - 1) % 2 + 1

        aggregates = llm_judge_results['aggregates']
        metrics = []
        scores = []

        for metric in ['relevance', 'faithfulness', 'completeness', 'coherence']:
            if metric in aggregates:
                metrics.append(metric.capitalize())
                scores.append(aggregates[metric]['mean'])

        fig.add_trace(
            go.Bar(
                x=metrics,
                y=scores,
                marker=dict(color='lightcoral'),
                name="LLM Judge"
            ),
            row=row,
            col=col
        )

        chart_idx += 1

    # Embedding benchmark
    if embedding_benchmark:
        row = (chart_idx - 1) // 2 + 1
        col = (chart_idx - 1) % 2 + 1

        models = [r['model'].split('/')[-1][:20] for r in embedding_benchmark]
        speeds = [r['query_encoding_speed_qps'] for r in embedding_benchmark]

        fig.add_trace(
            go.Bar(
                x=models,
                y=speeds,
                marker=dict(color='lightyellow'),
                name="Query Speed"
            ),
            row=row,
            col=col
        )

    # Update layout
    fig.update_layout(
        title_text="RAG System Evaluation Dashboard",
        showlegend=False,
        height=400 * rows
    )

    return fig.to_html()


def main():
    parser = argparse.ArgumentParser(description="Generate evaluation report")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports/",
        help="Output directory for reports"
    )
    parser.add_argument(
        "--ragas",
        type=str,
        default="reports/ragas_results.json",
        help="Path to RAGAS results"
    )
    parser.add_argument(
        "--retrieval",
        type=str,
        default="reports/retrieval_results.json",
        help="Path to retrieval results"
    )
    parser.add_argument(
        "--llm-judge",
        type=str,
        default="reports/llm_judge_results.json",
        help="Path to LLM judge results"
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="reports/embedding_benchmark.json",
        help="Path to embedding benchmark"
    )

    args = parser.parse_args()

    # Load results
    ragas_results = load_json_if_exists(args.ragas)
    retrieval_results = load_json_if_exists(args.retrieval)
    llm_judge_results = load_json_if_exists(args.llm_judge)
    embedding_benchmark = load_json_if_exists(args.benchmark)

    # Generate markdown report
    markdown_report = generate_markdown_report(
        ragas_results,
        retrieval_results,
        llm_judge_results,
        embedding_benchmark
    )

    # Save markdown
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / "evaluation_report.md"
    with open(md_path, 'w') as f:
        f.write(markdown_report)
    print(f"Markdown report saved to: {md_path}")

    # Generate HTML dashboard
    if PLOTLY_AVAILABLE:
        html_dashboard = create_html_dashboard(
            ragas_results,
            retrieval_results,
            llm_judge_results,
            embedding_benchmark
        )

        html_path = output_dir / "dashboard.html"
        with open(html_path, 'w') as f:
            f.write(html_dashboard)
        print(f"HTML dashboard saved to: {html_path}")
    else:
        print("Skipping HTML dashboard (Plotly not available)")

    # Print summary
    print("\n" + "="*60)
    print("EVALUATION REPORT GENERATED")
    print("="*60)
    print(f"\nMarkdown: {md_path}")
    if PLOTLY_AVAILABLE:
        print(f"Dashboard: {html_path}")
    print("\nYou can now add the markdown content to your README.md")

    return 0


if __name__ == "__main__":
    exit(main())
