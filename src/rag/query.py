"""
query.py — CLI entry point for the RAG pipeline.

Usage:
    python -m src.rag.query "What are the main failure modes of ML for collision avoidance?"

    python -m src.rag.query "How does class imbalance affect ML models?" --no-rerank

    python -m src.rag.query "What uncertainty quantification methods are used?" \
        --model claude-opus-4-6 --top-k 5

This satisfies the assignment acceptance test:
  "A single command produces: retrieval results, an answer with citations,
   and a saved log entry."
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

# Load .env file (so ANTHROPIC_API_KEY is available to generator.py)
from dotenv import load_dotenv
load_dotenv(_PROJECT_ROOT / ".env", override=True)

from src.rag.pipeline import run_query


def main():
    parser = argparse.ArgumentParser(
        description="Run a RAG query against the space debris research corpus"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Research question to answer",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="data/chromadb",
        help="Path to ChromaDB storage (default: data/chromadb)",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="space_debris_rag",
        help="ChromaDB collection name (default: space_debris_rag)",
    )
    parser.add_argument(
        "--n-retrieve",
        type=int,
        default=20,
        help="Number of chunks to retrieve (default: 20)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of chunks after reranking (default: 10)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Anthropic model name (default: claude-sonnet-4-5-20250929)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Max generation tokens (default: 2048)",
    )
    parser.add_argument(
        "--log-path",
        type=str,
        default="logs/rag_queries.jsonl",
        help="Path for JSONL log file (default: logs/rag_queries.jsonl)",
    )
    parser.add_argument(
        "--no-rerank",
        action="store_true",
        help="Skip cross-encoder reranking (use embedding distance only)",
    )

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"QUERY: {args.query}")
    print(f"{'='*70}\n")

    result = run_query(
        query=args.query,
        db_path=args.db_path,
        collection_name=args.collection,
        n_retrieve=args.n_retrieve,
        n_rerank=args.top_k,
        model=args.model,
        max_tokens=args.max_tokens,
        log_path=args.log_path,
        skip_rerank=args.no_rerank,
    )

    # Print answer
    print(f"\n{'='*70}")
    print("ANSWER:")
    print(f"{'='*70}\n")
    print(result["answer"])

    # Print sources used
    print(f"\n{'='*70}")
    print(f"SOURCES USED ({len(result['chunks_used'])} chunks):")
    print(f"{'='*70}")
    for i, chunk in enumerate(result["chunks_used"], 1):
        score_str = ""
        if chunk.get("rerank_score") is not None:
            score_str = f" | rerank={chunk['rerank_score']:.4f}"
        print(
            f"  [{i}] ({chunk['source_id']}, {chunk['chunk_id']}) "
            f"dist={chunk['distance']:.4f}{score_str}"
        )

    print(f"\nLog saved to: {args.log_path}")


if __name__ == "__main__":
    main()
