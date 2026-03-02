"""
pipeline.py — End-to-end RAG pipeline: retrieve → rerank → generate → log.

This is the main orchestrator. It connects all components and provides
a single function that takes a query and returns a grounded answer
with citations and a complete log entry.
"""

import re
from pathlib import Path
from typing import Optional

from src.rag.retriever import get_collection, retrieve
from src.rag.reranker import rerank
from src.rag.generator import generate
from src.rag.logger import log_query


def _parse_gap_suggestions(answer: str) -> tuple[str, list[dict]]:
    """Split answer into main text and gap suggestions.

    If the answer contains an "## EVIDENCE GAPS" section, parse it out
    and return the main answer plus structured gap suggestions.

    Returns:
        (main_answer, gap_suggestions) where gap_suggestions is a list of
        {"gap": str, "suggested_query": str} dicts.
    """
    if "## EVIDENCE GAPS" not in answer:
        return answer, []

    parts = answer.split("## EVIDENCE GAPS", 1)
    main_answer = parts[0].rstrip()
    gaps_text = parts[1]

    gap_suggestions = []
    for match in re.finditer(
        r'\*\*(.+?)\*\*\s*(?:\u2192|->|→)\s*Suggested query:\s*"(.+?)"',
        gaps_text,
    ):
        gap_suggestions.append({
            "gap": match.group(1),
            "suggested_query": match.group(2),
        })

    return main_answer, gap_suggestions


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


class RAGPipeline:
    """Class-based pipeline for Streamlit integration.

    Holds the ChromaDB collection in instance state so it survives
    Streamlit reruns via @st.cache_resource.
    """

    def __init__(
        self,
        db_path: str | Path = "data/chromadb",
        collection_name: str = "space_debris_rag",
    ):
        self.db_path = db_path
        self.collection_name = collection_name
        self.collection = get_collection(db_path, collection_name)

    def run(
        self,
        query: str,
        use_reranker: bool = True,
        where: Optional[dict] = None,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        log_path: str | Path = "logs/rag_queries.jsonl",
        include_gaps: bool = False,
    ) -> dict:
        """Run the full RAG pipeline.

        Returns:
            Dict with keys: answer, retrieved_chunks, reranked_chunks,
            model, prompt_version, usage, gap_suggestions.
        """
        # 1. Retrieve
        retrieved = retrieve(query, self.collection, n_results=20, where=where)

        # 2. Rerank
        if use_reranker:
            reranked = rerank(query, retrieved, top_k=10)
        else:
            reranked = retrieved[:10]
            for c in reranked:
                c["rerank_score"] = None

        # 3. Generate
        gen_result = generate(
            query, reranked, model=model, max_tokens=max_tokens,
            include_gaps=include_gaps,
        )

        # 4. Log
        log_query(
            query=query,
            retrieved_chunks=retrieved,
            reranked_chunks=reranked,
            generation_result=gen_result,
            log_path=log_path,
        )

        # 5. Parse gap suggestions (if present)
        answer, gap_suggestions = _parse_gap_suggestions(gen_result["answer"])

        return {
            "answer": answer,
            "gap_suggestions": gap_suggestions,
            "retrieved_chunks": retrieved,
            "reranked_chunks": reranked,
            "model": gen_result["model"],
            "prompt_version": gen_result["prompt_version"],
            "usage": gen_result["usage"],
        }

    def retrieve_only(
        self,
        query: str,
        use_reranker: bool = True,
        where: Optional[dict] = None,
    ) -> dict:
        """Retrieve + rerank without generation. For offline mode fallback."""
        retrieved = retrieve(query, self.collection, n_results=20, where=where)

        if use_reranker:
            reranked = rerank(query, retrieved, top_k=10)
        else:
            reranked = retrieved[:10]
            for c in reranked:
                c["rerank_score"] = None

        return {
            "retrieved_chunks": retrieved,
            "reranked_chunks": reranked,
        }
