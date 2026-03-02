"""Seed the cache for offline/demo mode.

Runs 12 curated queries through the RAG pipeline and caches the results.
Generates evidence tables and synthesis memos for 3 selected threads.

Usage:
    python -m scripts.seed_cache

Requires: ANTHROPIC_API_KEY set in environment or .env
"""

import os
import sys
import time

from dotenv import load_dotenv

# Ensure project root is on the path.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

load_dotenv()

from src.cache.manager import CacheManager
from src.rag.pipeline import RAGPipeline
from src.threads.manager import ThreadManager
from src.artifacts.generator import ArtifactGenerator
from src.app.components.filters import tag_to_field

# ---------------------------------------------------------------------------
# Seed queries (from PHASE3_ARTIFACTS_AND_SEEDS.md §1)
# ---------------------------------------------------------------------------

SEED_QUERIES = [
    # --- Unfiltered (7) ---
    {
        "id": "seed_01",
        "query": "What are the main failure modes of ML for collision avoidance?",
        "use_reranker": True,
        "where": None,
        "thread": False,
    },
    {
        "id": "seed_02",
        "query": "What did NASA CARA conclude about the operational viability of ML for conjunction assessment?",
        "use_reranker": True,
        "where": None,
        "thread": False,
    },
    {
        "id": "seed_03",
        "query": "Compare the uncertainty quantification approaches used across the corpus. Which methods show the most promise for operational deployment?",
        "use_reranker": True,
        "where": None,
        "thread": True,
        "thread_id": "seed_thread_01",
    },
    {
        "id": "seed_04",
        "query": "Across the corpus, what evidence exists that class imbalance is a fundamental barrier to ML for collision avoidance, and what solutions have been proposed?",
        "use_reranker": True,
        "where": None,
        "thread": True,
        "thread_id": "seed_thread_02",
    },
    {
        "id": "seed_05",
        "query": "What are the common reasons cited across NASA, ESA, and RAND sources for why ML has not yet achieved operational status in space debris tracking?",
        "use_reranker": True,
        "where": None,
        "thread": False,
    },
    {
        "id": "seed_06",
        "query": "How does catastrophic forgetting affect ML models for orbit decay prediction, and what technique does He 2024 use to address it?",
        "use_reranker": True,
        "where": None,
        "thread": False,
    },
    {
        "id": "seed_07",
        "query": "Has any ML system been deployed operationally for real-time collision avoidance decision-making?",
        "use_reranker": True,
        "where": None,
        "thread": False,
    },
    # --- Filtered (5) ---
    {
        "id": "seed_08",
        "query": "What ML approaches have been tried for collision avoidance?",
        "use_reranker": True,
        "where": {"year": {"$gte": 2022}},
        "thread": False,
    },
    {
        "id": "seed_09",
        "query": "What are the key findings from technical reports on the debris environment?",
        "use_reranker": True,
        "where": {"doc_type": "technical-report"},
        "thread": False,
    },
    {
        "id": "seed_10",
        "query": "What generalization failures have been observed in ML for space debris applications?",
        "use_reranker": True,
        "where": {tag_to_field("generalization"): {"$eq": True}},
        "thread": False,
    },
    {
        "id": "seed_11",
        "query": "How do operational integration barriers limit ML adoption for space debris tracking?",
        "use_reranker": True,
        "where": {tag_to_field("operational-integration"): {"$eq": True}},
        "thread": True,
        "thread_id": "seed_thread_03",
    },
    {
        "id": "seed_12",
        "query": "What is known about the current debris environment and long-term population stability?",
        "use_reranker": True,
        "where": {tag_to_field("debris-environment"): {"$eq": True}},
        "thread": False,
    },
]


def main():
    print("=" * 60)
    print("Cache Seeding for Offline/Demo Mode")
    print("=" * 60)

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. Cannot seed cache.")
        sys.exit(1)

    # Initialize components
    print("\nInitializing pipeline...")
    pipeline = RAGPipeline()
    cache = CacheManager()
    thread_mgr = ThreadManager()
    artifact_gen = ArtifactGenerator(cache)

    queries_cached = 0
    threads_saved = []
    artifacts_cached = 0

    # --- Phase 1: Run queries and cache results ---
    print(f"\n--- Caching {len(SEED_QUERIES)} queries ---\n")

    for i, sq in enumerate(SEED_QUERIES, 1):
        print(f"[{i}/{len(SEED_QUERIES)}] {sq['id']}: {sq['query'][:70]}...")
        if sq["where"]:
            print(f"    Filter: {sq['where']}")

        cache_key = CacheManager.make_query_key(
            sq["query"], sq["use_reranker"], sq["where"]
        )

        # Check if already cached
        existing = cache.get_query(cache_key)
        if existing:
            print(f"    Already cached (key: {cache_key})")
            result = existing
        else:
            try:
                result = pipeline.run(
                    sq["query"],
                    use_reranker=sq["use_reranker"],
                    where=sq["where"],
                    include_gaps=True,
                )
                cache.put_query(cache_key, result)
                print(f"    Cached (key: {cache_key})")
                # Brief pause to avoid rate limits
                time.sleep(1)
            except Exception as e:
                print(f"    FAILED: {e}")
                continue

        queries_cached += 1

        # Save as thread if flagged
        if sq.get("thread"):
            thread = {
                "thread_id": sq["thread_id"],
                "query": sq["query"],
                "where_filters": sq["where"],
                "use_reranker": sq["use_reranker"],
                "answer": result.get("answer"),
                "retrieved_chunks": result.get("retrieved_chunks", []),
                "reranked_chunks": result.get("reranked_chunks", []),
                "model": result.get("model"),
                "prompt_version": result.get("prompt_version"),
                "gap_suggestions": result.get("gap_suggestions", []),
            }
            thread_mgr.save(thread)
            threads_saved.append(sq["thread_id"])
            print(f"    Saved thread: {sq['thread_id']}")

    # --- Phase 2: Generate artifacts for thread queries ---
    print(f"\n--- Generating artifacts for {len(threads_saved)} threads ---\n")

    for thread_id in threads_saved:
        thread = thread_mgr.load(thread_id)
        if not thread:
            print(f"  Thread {thread_id} not found, skipping.")
            continue

        # Evidence table
        print(f"  {thread_id}: Generating evidence table...")
        et = artifact_gen.generate_evidence_table(thread)
        if et:
            print(f"    Evidence table cached.")
            artifacts_cached += 1
            time.sleep(1)
        else:
            print(f"    Evidence table FAILED.")

        # Synthesis memo
        print(f"  {thread_id}: Generating synthesis memo...")
        sm = artifact_gen.generate_synthesis_memo(thread)
        if sm:
            print(f"    Synthesis memo cached.")
            artifacts_cached += 1
            time.sleep(1)
        else:
            print(f"    Synthesis memo FAILED.")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("Cache Seeding Complete")
    print("=" * 60)
    print(f"  Queries cached:   {queries_cached}/{len(SEED_QUERIES)}")
    print(f"  Threads saved:    {len(threads_saved)}")
    print(f"  Artifacts cached: {artifacts_cached}")
    print(f"\n  Cache dir: {cache.cache_dir}")
    print(f"  Threads dir: {thread_mgr.threads_dir}")


if __name__ == "__main__":
    main()
