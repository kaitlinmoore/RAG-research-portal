"""
retriever.py — Query ChromaDB for relevant chunks with optional metadata filtering.

Handles embedding the query, searching the collection, and returning
ranked results with metadata for downstream reranking and generation.
"""

from pathlib import Path
from typing import Optional

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


def get_collection(
    db_path: str | Path = "data/chromadb",
    collection_name: str = "space_debris_rag",
    model_name: str = "all-mpnet-base-v2",
) -> chromadb.Collection:
    """Load an existing ChromaDB collection with its embedding function.

    Args:
        db_path: Path to ChromaDB persistent storage.
        collection_name: Name of the collection.
        model_name: Sentence-transformers model (must match what was used at ingest).

    Returns:
        chromadb.Collection ready for queries.
    """
    ef = SentenceTransformerEmbeddingFunction(model_name=model_name)
    client = chromadb.PersistentClient(path=str(db_path))
    collection = client.get_collection(
        name=collection_name,
        embedding_function=ef,
    )
    return collection


def retrieve(
    query: str,
    collection: chromadb.Collection,
    n_results: int = 20,
    where: Optional[dict] = None,
) -> list[dict]:
    """Retrieve top-k chunks from ChromaDB for a query.

    Args:
        query: Natural language query string.
        collection: ChromaDB collection to search.
        n_results: Number of results to retrieve (retrieve more than needed
                   so the reranker has a good pool to work with).
        where: Optional ChromaDB metadata filter dict, e.g.
               {"year": {"$gte": 2022}} or
               {"doc_type": "peer-reviewed"} or
               {"$and": [{"year": {"$gte": 2022}}, {"doc_type": "peer-reviewed"}]}

    Returns:
        List of dicts, each with keys:
            id, text, distance, source_id, chunk_id, section_id,
            section_title, year, doc_type, venue, authors
    """
    kwargs = {
        "query_texts": [query],
        "n_results": n_results,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)

    chunks = []
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        chunks.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i],
            "source_id": meta.get("source_id", ""),
            "chunk_id": meta.get("chunk_id", ""),
            "section_id": meta.get("section_id", ""),
            "section_title": meta.get("section_title", ""),
            "year": meta.get("year", 0),
            "doc_type": meta.get("doc_type", ""),
            "venue": meta.get("venue", ""),
            "authors": meta.get("authors", ""),
        })

    return chunks
