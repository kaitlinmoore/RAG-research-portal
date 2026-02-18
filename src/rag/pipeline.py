"""
pipeline.py — End-to-end RAG pipeline: retrieve → rerank → generate → log.

This is the main orchestrator. It connects all components and provides
a single function that takes a query and returns a grounded answer
with citations and a complete log entry.
"""

from pathlib import Path
from typing import Optional

from src.rag.retriever import get_collection, retrieve
from src.rag.reranker import rerank
from src.rag.generator import generate
from src.rag.logger import log_query


def run_query(
    query: str,
    db_path: str | Path = "data/chromadb",
    collection_name: str = "space_debris_rag",
    n_retrieve: int = 20,
    n_rerank: int = 10,
    where: Optional[dict] = None,
    model: Optional[str] = None,
    max_tokens: int = 2048,
    log_path: str | Path = "logs/rag_queries.jsonl",
    skip_rerank: bool = False,
    metadata: Optional[dict] = None,
) -> dict:
    """Run the full RAG pipeline for a single query.

    Args:
        query: Natural language research question.
        db_path: Path to ChromaDB storage.
        collection_name: ChromaDB collection name.
        n_retrieve: Number of chunks to retrieve from ChromaDB.
        n_rerank: Number of top chunks to keep after reranking.
        where: Optional metadata filter for retrieval.
        model: Anthropic model override.
        max_tokens: Max generation tokens.
        log_path: Path for JSONL log output.
        skip_rerank: If True, skip reranking (use retrieval order).
        metadata: Optional extra metadata for the log entry.

    Returns:
        Dict with keys:
            answer: Generated text with citations.
            chunks_used: List of chunk dicts that were passed to the LLM.
            log_entry: The full log entry dict.
    """
    # 1. Retrieve
    collection = get_collection(db_path, collection_name)
    retrieved = retrieve(query, collection, n_results=n_retrieve, where=where)
    print(f"  Retrieved {len(retrieved)} chunks")

    # 2. Rerank (or skip)
    if skip_rerank:
        reranked = retrieved[:n_rerank]
        for chunk in reranked:
            chunk["rerank_score"] = None
        print(f"  Skipped reranking, using top {len(reranked)} by embedding distance")
    else:
        reranked = rerank(query, retrieved, top_k=n_rerank)
        print(f"  Reranked to top {len(reranked)} chunks")

    # 3. Generate
    gen_result = generate(query, reranked, model=model, max_tokens=max_tokens)
    print(f"  Generated answer ({gen_result['usage']['output_tokens']} tokens)")

    # 4. Log
    log_entry = log_query(
        query=query,
        retrieved_chunks=retrieved,
        reranked_chunks=reranked,
        generation_result=gen_result,
        log_path=log_path,
        metadata=metadata,
    )
    print(f"  Logged to {log_path}")

    return {
        "answer": gen_result["answer"],
        "chunks_used": reranked,
        "log_entry": log_entry,
    }
