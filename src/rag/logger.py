"""
logger.py — Structured JSON logging for RAG pipeline runs.

Logs each query as a complete record: query, retrieved chunks, reranked
chunks, generated answer, model info, and prompt version. Appends to a
JSON Lines (.jsonl) file for easy parsing.

Required by assignment: "store queries, retrieved chunks, model outputs,
and prompt/version IDs."
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def log_query(
    query: str,
    retrieved_chunks: list[dict],
    reranked_chunks: list[dict],
    generation_result: dict,
    log_path: str | Path = "logs/rag_queries.jsonl",
    metadata: Optional[dict] = None,
) -> dict:
    """Log a complete RAG pipeline run to a JSONL file.

    Args:
        query: The original query string.
        retrieved_chunks: Raw retrieval results (before reranking).
        reranked_chunks: Chunks after reranking (the ones passed to the LLM).
        generation_result: Dict from generator.generate() with answer,
                          model, prompt_version, usage.
        log_path: Path to the JSONL log file.
        metadata: Optional extra metadata dict (e.g. eval tags).

    Returns:
        The log entry dict that was written.
    """
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Slim down chunk data for logging (don't duplicate full text for retrieved)
    def slim_chunk(chunk: dict) -> dict:
        return {
            "id": chunk.get("id", ""),
            "source_id": chunk.get("source_id", ""),
            "chunk_id": chunk.get("chunk_id", ""),
            "section_title": chunk.get("section_title", ""),
            "distance": chunk.get("distance"),
            "rerank_score": chunk.get("rerank_score"),
        }

    def full_chunk(chunk: dict) -> dict:
        """Keep text for reranked chunks (these are what the LLM saw)."""
        return {
            "id": chunk.get("id", ""),
            "source_id": chunk.get("source_id", ""),
            "chunk_id": chunk.get("chunk_id", ""),
            "section_title": chunk.get("section_title", ""),
            "year": chunk.get("year"),
            "authors": chunk.get("authors", ""),
            "distance": chunk.get("distance"),
            "rerank_score": chunk.get("rerank_score"),
            "text": chunk.get("text", ""),
        }

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "retrieval": {
            "n_retrieved": len(retrieved_chunks),
            "chunks": [slim_chunk(c) for c in retrieved_chunks],
        },
        "reranking": {
            "n_reranked": len(reranked_chunks),
            "chunks": [full_chunk(c) for c in reranked_chunks],
        },
        "generation": {
            "answer": generation_result.get("answer", ""),
            "model": generation_result.get("model", ""),
            "prompt_version": generation_result.get("prompt_version", ""),
            "usage": generation_result.get("usage", {}),
        },
    }

    if metadata:
        entry["metadata"] = metadata

    # Append to JSONL
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry
