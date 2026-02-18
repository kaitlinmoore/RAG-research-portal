"""
reranker.py — Cross-encoder reranking of retrieved chunks.

This is a Phase 2 enhancement. After initial retrieval from ChromaDB
(which uses bi-encoder similarity), a cross-encoder scores each
query-chunk pair jointly for more accurate relevance ranking.

Uses sentence-transformers CrossEncoder with ms-marco-MiniLM-L-6-v2
(lightweight, good quality for academic text reranking).
"""

from sentence_transformers import CrossEncoder

# Module-level cache so the model loads once
_reranker: CrossEncoder | None = None


def get_reranker(
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
) -> CrossEncoder:
    """Load the cross-encoder model (cached after first call).

    Args:
        model_name: HuggingFace cross-encoder model name.

    Returns:
        CrossEncoder instance.
    """
    global _reranker
    if _reranker is None:
        print(f"Loading reranker model: {model_name}")
        _reranker = CrossEncoder(model_name)
        print("Reranker loaded.")
    return _reranker


def rerank(
    query: str,
    chunks: list[dict],
    top_k: int = 10,
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
) -> list[dict]:
    """Rerank retrieved chunks using a cross-encoder.

    Args:
        query: The original query string.
        chunks: List of chunk dicts from retriever.retrieve().
        top_k: Number of top results to return after reranking.
        model_name: Cross-encoder model to use.

    Returns:
        Top-k chunks sorted by cross-encoder relevance score (descending).
        Each chunk dict gets an added 'rerank_score' field.
    """
    if not chunks:
        return []

    reranker = get_reranker(model_name)

    # Build query-document pairs for the cross-encoder
    pairs = [(query, chunk["text"]) for chunk in chunks]
    scores = reranker.predict(pairs)

    # Attach scores and sort
    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)

    ranked = sorted(chunks, key=lambda c: c["rerank_score"], reverse=True)
    return ranked[:top_k]
