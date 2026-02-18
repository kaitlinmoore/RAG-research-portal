"""
run_eval.py — Evaluation runner for the RAG pipeline.

Loads evaluation queries from src/eval/queries.json, runs each through the
RAG pipeline in two configurations (with and without reranking), scores
each response using LLM-as-judge, and saves structured results.

Usage:
    # Run full evaluation (both modes)
    python -m src.eval.run_eval

    # Run only with reranking
    python -m src.eval.run_eval --rerank-only

    # Run only without reranking (baseline)
    python -m src.eval.run_eval --baseline-only

    # Run a subset of queries (by ID prefix)
    python -m src.eval.run_eval --filter "D-"

    # Skip scoring (just run pipeline, useful for testing)
    python -m src.eval.run_eval --no-score

    # Specify output file
    python -m src.eval.run_eval --output logs/my_eval.jsonl

Output:
    JSONL file where each line is a complete evaluation record containing:
    - query metadata (id, category, sub_question, expected_sources)
    - pipeline config (use_reranker, model, prompt_version)
    - pipeline output (answer, retrieved_chunks, reranked_chunks)
    - scores (groundedness, citation_correctness, failure_tags)
    - timing information
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (handles cases where cwd differs)
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env", override=True)
load_dotenv(_project_root / "grader.env", override=True)

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.rag.pipeline import run_query
from src.eval.scorer import score_response


def load_queries(queries_path: str | Path) -> list[dict]:
    """Load evaluation queries from JSON file.
    
    Args:
        queries_path: Path to queries.json
    
    Returns:
        List of query dicts with keys: id, category, sub_question, query,
        expected_sources, notes
    """
    path = Path(queries_path)
    if not path.exists():
        print(f"ERROR: Queries file not found at {path}")
        sys.exit(1)
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # queries.json wraps the list under a "queries" key alongside "metadata"
    if isinstance(data, dict) and "queries" in data:
        queries = data["queries"]
    elif isinstance(data, list):
        queries = data
    else:
        print(f"ERROR: Unexpected queries.json structure (expected list or dict with 'queries' key)")
        sys.exit(1)

    print(f"Loaded {len(queries)} evaluation queries from {path}")
    return queries


def run_single_query(
    query_text: str,
    use_reranker: bool = True,
    db_path: str = "data/chromadb",
    collection_name: str = "space_debris_rag",
) -> dict:
    """Run a single query through the pipeline and capture all outputs.

    Calls the pipeline's run_query() function and reshapes the result
    into the flat dict that build_eval_record() expects.

    Args:
        query_text: The query string.
        use_reranker: Whether to use cross-encoder reranking.
        db_path: Path to ChromaDB database.
        collection_name: ChromaDB collection name.

    Returns:
        Dict with: answer, retrieved_chunks, reranked_chunks,
        model, prompt_version, usage, elapsed_seconds, use_reranker.
    """
    start = time.time()

    # run_query() returns: {answer, chunks_used, log_entry}
    # log_entry contains the full details we need.
    raw = run_query(
        query=query_text,
        db_path=db_path,
        collection_name=collection_name,
        skip_rerank=not use_reranker,
    )

    elapsed = time.time() - start

    log_entry = raw["log_entry"]
    gen = log_entry.get("generation", {})

    # Reshape: the retriever returns full chunk dicts in log_entry.
    # We need the full text for the scorer, so pull reranked chunks
    # (which have text) from log_entry["reranking"]["chunks"], and
    # retrieval summaries from log_entry["retrieval"]["chunks"].
    # However, the slim retrieval chunks lack text. For the eval record
    # we mainly need the reranked/used chunks (which have text in
    # raw["chunks_used"]).
    result = {
        "answer": raw["answer"],
        "retrieved_chunks": log_entry.get("retrieval", {}).get("chunks", []),
        "reranked_chunks": raw["chunks_used"],
        "model": gen.get("model", "unknown"),
        "prompt_version": gen.get("prompt_version", "unknown"),
        "usage": gen.get("usage", {}),
        "elapsed_seconds": round(elapsed, 2),
        "use_reranker": use_reranker,
    }

    return result


def build_eval_record(
    query_meta: dict,
    pipeline_result: dict,
    scores: dict | None = None,
) -> dict:
    """Combine query metadata, pipeline output, and scores into one record.
    
    Args:
        query_meta: From queries.json (id, category, query, expected_sources, etc.)
        pipeline_result: From run_single_query (answer, chunks, timing, etc.)
        scores: From scorer.score_response (groundedness, citation, failure_tags)
    
    Returns:
        Flat dict suitable for JSONL serialization.
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        # Query metadata
        "query_id": query_meta.get("id", "unknown"),
        "category": query_meta.get("category", "unknown"),
        "sub_question": query_meta.get("sub_question", ""),
        "query": query_meta.get("query", ""),
        "expected_sources": query_meta.get("expected_sources", []),
        "notes": query_meta.get("notes", ""),
        # Pipeline config
        "use_reranker": pipeline_result.get("use_reranker", True),
        "model": pipeline_result.get("model", "unknown"),
        "prompt_version": pipeline_result.get("prompt_version", "unknown"),
        # Pipeline output
        "answer": pipeline_result.get("answer", ""),
        "retrieved_chunks": _simplify_chunks(
            pipeline_result.get("retrieved_chunks", [])
        ),
        "reranked_chunks": _simplify_chunks(
            pipeline_result.get("reranked_chunks", [])
        ),
        # Token usage and timing
        "generation_tokens": pipeline_result.get("usage", {}),
        "elapsed_seconds": pipeline_result.get("elapsed_seconds", 0),
    }
    
    # Add scores if available
    if scores:
        record["groundedness_score"] = scores.get("groundedness_score", 0)
        record["groundedness_rationale"] = scores.get("groundedness_rationale", "")
        record["citation_score"] = scores.get("citation_score", 0)
        record["citation_rationale"] = scores.get("citation_rationale", "")
        record["failure_tags"] = scores.get("failure_tags", [])
        record["judge_model"] = scores.get("judge_model", "")
        record["judge_tokens"] = {
            "input": scores.get("judge_input_tokens", 0),
            "output": scores.get("judge_output_tokens", 0),
        }
    
    return record


def _simplify_chunks(chunks: list[dict]) -> list[dict]:
    """Reduce chunk data to essentials for the eval log.
    
    Keeps source_id, chunk_id, section_title, and first 200 chars of text.
    This prevents the log file from becoming enormous while preserving
    enough info for manual verification.
    """
    simplified = []
    for c in chunks:
        text = c.get("text", c.get("document", ""))
        simplified.append({
            "source_id": c.get("source_id", ""),
            "chunk_id": c.get("chunk_id", ""),
            "section_title": c.get("section_title", ""),
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "distance": c.get("distance", None),
            "rerank_score": c.get("rerank_score", None),
        })
    return simplified


def print_progress(
    idx: int,
    total: int,
    query_id: str,
    mode: str,
    scores: dict | None = None,
):
    """Print a compact progress line."""
    mode_label = "rerank" if mode == "rerank" else "baseline"
    prefix = f"[{idx}/{total}] {query_id} ({mode_label})"
    
    if scores:
        g = scores.get("groundedness_score", "?")
        c = scores.get("citation_score", "?")
        tags = scores.get("failure_tags", [])
        tag_str = f" | tags: {', '.join(tags)}" if tags else ""
        print(f"  {prefix}: G={g} C={c}{tag_str}")
    else:
        print(f"  {prefix}: running...")


def print_summary(records: list[dict]):
    """Print summary statistics from the evaluation run."""
    if not records:
        print("\nNo records to summarize.")
        return
    
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    
    # Split by mode
    rerank_records = [r for r in records if r.get("use_reranker")]
    baseline_records = [r for r in records if not r.get("use_reranker")]
    
    for label, subset in [("With Reranking", rerank_records), ("Baseline (No Reranking)", baseline_records)]:
        if not subset:
            continue
        
        scored = [r for r in subset if r.get("groundedness_score", 0) > 0]
        if not scored:
            print(f"\n{label}: {len(subset)} queries run, no scores available")
            continue
        
        g_scores = [r["groundedness_score"] for r in scored]
        c_scores = [r["citation_score"] for r in scored]
        avg_g = sum(g_scores) / len(g_scores)
        avg_c = sum(c_scores) / len(c_scores)
        
        # Count failure tags
        all_tags = []
        for r in scored:
            all_tags.extend(r.get("failure_tags", []))
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Count by category
        categories = {}
        for r in scored:
            cat = r.get("category", "unknown")
            if cat not in categories:
                categories[cat] = {"g": [], "c": []}
            categories[cat]["g"].append(r["groundedness_score"])
            categories[cat]["c"].append(r["citation_score"])
        
        print(f"\n--- {label} ---")
        print(f"  Queries scored: {len(scored)}")
        print(f"  Avg Groundedness: {avg_g:.2f} / 4.00")
        print(f"  Avg Citation Correctness: {avg_c:.2f} / 4.00")
        
        if tag_counts:
            print(f"  Failure tags:")
            for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
                print(f"    {tag}: {count}")
        else:
            print(f"  Failure tags: none")
        
        print(f"  By category:")
        for cat, vals in sorted(categories.items()):
            cat_g = sum(vals["g"]) / len(vals["g"])
            cat_c = sum(vals["c"]) / len(vals["c"])
            print(f"    {cat}: G={cat_g:.2f} C={cat_c:.2f} (n={len(vals['g'])})")
    
    # Comparison if both modes present
    if rerank_records and baseline_records:
        r_scored = [r for r in rerank_records if r.get("groundedness_score", 0) > 0]
        b_scored = [r for r in baseline_records if r.get("groundedness_score", 0) > 0]
        if r_scored and b_scored:
            r_avg_g = sum(r["groundedness_score"] for r in r_scored) / len(r_scored)
            b_avg_g = sum(r["groundedness_score"] for r in b_scored) / len(b_scored)
            r_avg_c = sum(r["citation_score"] for r in r_scored) / len(r_scored)
            b_avg_c = sum(r["citation_score"] for r in b_scored) / len(b_scored)
            
            print(f"\n--- Reranking Impact ---")
            print(f"  Groundedness:  {b_avg_g:.2f} -> {r_avg_g:.2f} (delta = {r_avg_g - b_avg_g:+.2f})")
            print(f"  Citation:      {b_avg_c:.2f} -> {r_avg_c:.2f} (delta = {r_avg_c - b_avg_c:+.2f})")
    
    # Identify worst-scoring queries for failure case analysis
    all_scored = [r for r in records if r.get("groundedness_score", 0) > 0]
    if all_scored:
        worst = sorted(all_scored, key=lambda r: r["groundedness_score"] + r["citation_score"])[:5]
        print(f"\n--- Lowest-Scoring Queries (candidates for failure case analysis) ---")
        for r in worst:
            mode = "rerank" if r.get("use_reranker") else "baseline"
            tags = ", ".join(r.get("failure_tags", [])) or "none"
            print(f"  {r['query_id']} ({mode}): G={r['groundedness_score']} C={r['citation_score']} | {tags}")
            print(f"    Query: {r['query'][:80]}...")
    
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Run RAG evaluation suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--queries",
        default="src/eval/queries.json",
        help="Path to evaluation queries JSON (default: src/eval/queries.json)",
    )
    parser.add_argument(
        "--output",
        default="logs/eval_results.jsonl",
        help="Output JSONL path (default: logs/eval_results.jsonl)",
    )
    parser.add_argument(
        "--rerank-only",
        action="store_true",
        help="Only run with reranking (skip baseline)",
    )
    parser.add_argument(
        "--baseline-only",
        action="store_true",
        help="Only run without reranking (skip reranked)",
    )
    parser.add_argument(
        "--filter",
        default=None,
        help="Only run queries whose ID starts with this prefix (e.g., 'D-' for direct queries)",
    )
    parser.add_argument(
        "--no-score",
        action="store_true",
        help="Skip LLM-as-judge scoring (useful for testing pipeline only)",
    )
    parser.add_argument(
        "--judge-model",
        default="claude-opus-4-6",
        help="Model to use for LLM-as-judge scoring",
    )
    parser.add_argument(
        "--db-path",
        default="data/chromadb",
        help="Path to ChromaDB database",
    )
    parser.add_argument(
        "--collection",
        default="space_debris_rag",
        help="ChromaDB collection name",
    )
    args = parser.parse_args()
    
    # Determine which modes to run
    modes = []
    if not args.baseline_only:
        modes.append("rerank")
    if not args.rerank_only:
        modes.append("baseline")
    
    # Load queries
    queries = load_queries(args.queries)
    
    # Apply filter if specified
    if args.filter:
        queries = [q for q in queries if q["id"].startswith(args.filter)]
        print(f"Filtered to {len(queries)} queries matching prefix '{args.filter}'")
    
    if not queries:
        print("No queries to run. Check your --filter setting.")
        sys.exit(1)
    
    total_runs = len(queries) * len(modes)
    print(f"\nPlanned: {len(queries)} queries × {len(modes)} mode(s) = {total_runs} total runs")
    if not args.no_score:
        print(f"Judge model: {args.judge_model}")
    print()
    
    # Pipeline is initialized on each call (run_query handles it internally).
    print(f"Using ChromaDB at: {args.db_path} (collection: {args.collection})\n")
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run evaluation
    all_records = []
    run_idx = 0
    
    for mode in modes:
        use_reranker = mode == "rerank"
        mode_label = "WITH reranking" if use_reranker else "WITHOUT reranking (baseline)"
        print(f"\n{'='*50}")
        print(f"Running {len(queries)} queries {mode_label}")
        print(f"{'='*50}\n")
        
        for query_meta in queries:
            run_idx += 1
            query_id = query_meta["id"]
            query_text = query_meta["query"]
            
            print_progress(run_idx, total_runs, query_id, mode)
            
            try:
                # Run pipeline
                pipeline_result = run_single_query(
                    query_text,
                    use_reranker=use_reranker,
                    db_path=args.db_path,
                    collection_name=args.collection,
                )
                
                # Score with LLM-as-judge (unless --no-score)
                scores = None
                if not args.no_score:
                    # Determine which chunks to send to the judge:
                    # If reranking was used, send the reranked chunks (what the generator saw).
                    # If no reranking, send the retrieved chunks.
                    judge_chunks = (
                        pipeline_result.get("reranked_chunks")
                        or pipeline_result.get("retrieved_chunks", [])
                    )
                    
                    scores = score_response(
                        query=query_text,
                        answer=pipeline_result.get("answer", ""),
                        chunks=judge_chunks,
                        model=args.judge_model,
                    )
                    print_progress(run_idx, total_runs, query_id, mode, scores)
                
                # Build and save record
                record = build_eval_record(query_meta, pipeline_result, scores)
                all_records.append(record)
                
                # Append to file incrementally (so we don't lose data on crash)
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                
            except Exception as e:
                print(f"  ERROR on {query_id} ({mode}): {e}")
                error_record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "query_id": query_id,
                    "query": query_text,
                    "use_reranker": use_reranker,
                    "error": str(e),
                    "category": query_meta.get("category", ""),
                }
                all_records.append(error_record)
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(error_record, ensure_ascii=False) + "\n")
    
    # Print summary
    print_summary(all_records)
    
    print(f"\nResults saved to: {output_path}")
    print(f"Total records: {len(all_records)}")
    
    # Also save a summary JSON for easy reference
    summary_path = output_path.with_suffix(".summary.json")
    scored_records = [r for r in all_records if r.get("groundedness_score", 0) > 0]
    if scored_records:
        summary = {
            "run_date": datetime.now(timezone.utc).isoformat(),
            "total_queries": len(queries),
            "total_runs": len(all_records),
            "errors": len([r for r in all_records if "error" in r]),
            "modes": modes,
        }
        
        for mode in modes:
            mode_key = "rerank" if mode == "rerank" else "baseline"
            subset = [
                r for r in scored_records
                if r.get("use_reranker") == (mode == "rerank")
            ]
            if subset:
                summary[mode_key] = {
                    "n": len(subset),
                    "avg_groundedness": round(
                        sum(r["groundedness_score"] for r in subset) / len(subset), 2
                    ),
                    "avg_citation": round(
                        sum(r["citation_score"] for r in subset) / len(subset), 2
                    ),
                }
        
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
