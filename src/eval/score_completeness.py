"""
score_completeness.py — Add completeness scores to existing eval results.

Reads eval_results.jsonl, sends each record to Claude Opus for completeness
scoring, and writes enriched results to eval_results_v2.jsonl.

Also computes mechanical metrics (retrieval_recall, context_utilization)
from existing data — no API calls needed for those.

Usage:
    python -m src.eval.score_completeness \
        --input logs/eval_results.jsonl \
        --output logs/eval_results_v2.jsonl

Requires ANTHROPIC_API_KEY in environment or .env file.
"""

import json
import re
import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    _project_root = Path(__file__).resolve().parent.parent.parent
    load_dotenv(_project_root / ".env", override=True)
except ImportError:
    pass

import anthropic

JUDGE_MODEL = "claude-opus-4-6"

COMPLETENESS_PROMPT = """You are evaluating the COMPLETENESS of a RAG system's answer.

QUERY: {query}

RETRIEVED CHUNKS SENT TO GENERATOR (top {n_chunks}):
{chunks_text}

SYSTEM'S ANSWER:
{answer}

COMPLETENESS RUBRIC (1-4):
- 4: Covers all aspects of the question using the full range of relevant retrieved evidence
- 3: Mostly complete; minor gaps in coverage or over-reliance on a single source when multiple relevant sources were available
- 2: Partial; misses a major aspect of the question or ignores clearly relevant retrieved chunks
- 1: Superficial or off-target despite relevant evidence being available

IMPORTANT SCORING RULES:
- Score based on what the RETRIEVED CHUNKS could support, not what the full corpus might contain.
- If the answer explicitly says "I cannot answer this" or "evidence is missing", check whether the retrieved chunks actually support a better answer. If they do, penalize. If they genuinely don't contain relevant info, a well-structured acknowledgment of limitations can still score 3-4.
- If the query asks about multiple aspects/sources and the answer only addresses some using a subset of relevant retrieved chunks, score 2-3.
- For out-of-scope queries where retrieved chunks are genuinely irrelevant, score based on how well the answer characterizes what the corpus does contain.

Respond with ONLY a JSON object (no markdown, no backticks):
{{"completeness_score": <1-4>, "completeness_rationale": "<2-3 sentences>"}}"""


def format_chunks_for_judge(chunks):
    """Format chunks for the completeness judge prompt."""
    lines = []
    for i, c in enumerate(chunks, 1):
        source = c.get("source_id", "?")
        chunk_id = c.get("chunk_id", "?")
        section = c.get("section_title", "")
        text = c.get("text", c.get("text_preview", ""))
        # Truncate long chunks
        if len(text) > 500:
            text = text[:500] + "..."
        lines.append(f"[{i}] ({source}, {chunk_id}) | Section: {section}\n{text}")
    return "\n\n".join(lines)


def compute_retrieval_recall(record):
    """Compute fraction of expected sources in top-20 retrieved chunks."""
    expected = record.get("expected_sources", [])
    if not expected:
        return None
    retrieved = set(c["source_id"] for c in record.get("retrieved_chunks", [])[:20])
    hits = sum(1 for s in expected if s in retrieved)
    return round(hits / len(expected), 4)


def compute_context_utilization(record):
    """Compute fraction of top-10 sent chunks actually cited in the answer."""
    answer = record.get("answer", "")

    # Extract cited (source_id, chunk_id) pairs
    cited_pairs = set()
    for match in re.finditer(r'\((\w+\d{4}),\s*(sec[\w._]+)\)', answer):
        cited_pairs.add((match.group(1), match.group(2)))

    # Get chunks sent to generator
    if record.get("use_reranker") and record.get("reranked_chunks"):
        sent = record["reranked_chunks"][:10]
    else:
        sent = record.get("retrieved_chunks", [])[:10]

    if not sent:
        return None

    n_exact = sum(
        1 for c in sent
        if (c.get("source_id", ""), c.get("chunk_id", "")) in cited_pairs
    )
    return round(n_exact / len(sent), 4)


def score_completeness(client, record):
    """Call Claude Opus to score completeness for one record."""
    # Get the chunks that were sent to the generator
    if record.get("use_reranker") and record.get("reranked_chunks"):
        sent_chunks = record["reranked_chunks"][:10]
    else:
        sent_chunks = record.get("retrieved_chunks", [])[:10]

    chunks_text = format_chunks_for_judge(sent_chunks)

    prompt = COMPLETENESS_PROMPT.format(
        query=record["query"],
        n_chunks=len(sent_chunks),
        chunks_text=chunks_text,
        answer=record["answer"],
    )

    response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if present
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    result = json.loads(raw)
    tokens = {
        "input": response.usage.input_tokens,
        "output": response.usage.output_tokens,
    }
    return result, tokens


def main():
    parser = argparse.ArgumentParser(description="Add completeness scores to eval results")
    parser.add_argument("--input", default="logs/eval_results.jsonl",
                        help="Path to existing eval results JSONL")
    parser.add_argument("--output", default="logs/eval_results_v2.jsonl",
                        help="Path for enriched output JSONL")
    parser.add_argument("--summary", default=None,
                        help="Path for summary JSON (default: <output>.summary.json)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute mechanical metrics only, skip API calls")
    args = parser.parse_args()

    if args.summary is None:
        args.summary = args.output.replace(".jsonl", ".summary.json")

    # Load existing results
    records = []
    with open(args.input, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    print(f"Loaded {len(records)} records from {args.input}")

    client = None if args.dry_run else anthropic.Anthropic()

    enriched = []
    total_judge_tokens = {"input": 0, "output": 0}

    for i, record in enumerate(records):
        qid = record["query_id"]
        mode = "rerank" if record["use_reranker"] else "baseline"

        # Mechanical metrics (always computed)
        record["retrieval_recall"] = compute_retrieval_recall(record)
        record["context_utilization"] = compute_context_utilization(record)

        # Completeness scoring (API call)
        if not args.dry_run:
            try:
                result, tokens = score_completeness(client, record)
                record["completeness_score"] = result["completeness_score"]
                record["completeness_rationale"] = result["completeness_rationale"]
                total_judge_tokens["input"] += tokens["input"]
                total_judge_tokens["output"] += tokens["output"]
                print(f"  [{i+1}/{len(records)}] {qid} {mode}: "
                      f"completeness={result['completeness_score']} "
                      f"ret_recall={record['retrieval_recall']} "
                      f"ctx_util={record['context_utilization']:.2f}")
            except Exception as e:
                print(f"  [{i+1}/{len(records)}] {qid} {mode}: ERROR - {e}")
                record["completeness_score"] = None
                record["completeness_rationale"] = f"Scoring error: {e}"
        else:
            print(f"  [{i+1}/{len(records)}] {qid} {mode}: "
                  f"ret_recall={record['retrieval_recall']} "
                  f"ctx_util={record['context_utilization']:.2f} "
                  f"(dry-run, skipping completeness)")

        enriched.append(record)

        # Rate limiting: brief pause between API calls
        if not args.dry_run and i < len(records) - 1:
            time.sleep(0.5)

    # Write enriched results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for record in enriched:
            f.write(json.dumps(record) + "\n")

    print(f"\nWrote {len(enriched)} enriched records to {args.output}")

    # Compute and write summary
    summary = compute_summary(enriched, args.dry_run)
    summary["run_date"] = datetime.now(timezone.utc).isoformat()
    summary["source_file"] = args.input
    summary["judge_model"] = JUDGE_MODEL
    if not args.dry_run:
        summary["completeness_judge_tokens"] = total_judge_tokens

    with open(args.summary, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Wrote summary to {args.summary}")
    print_summary(summary, args.dry_run)


def compute_summary(records, dry_run=False):
    """Compute aggregate stats across all records."""
    summary = {"total_runs": len(records), "modes": {}}

    for mode_flag in [True, False]:
        mode_label = "rerank" if mode_flag else "baseline"
        mode_records = [r for r in records if r["use_reranker"] == mode_flag]

        by_category = {}
        for r in mode_records:
            cat = r["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)

        mode_stats = {"n": len(mode_records), "by_category": {}}

        for cat in ["direct", "synthesis", "edge_case"]:
            cat_records = by_category.get(cat, [])
            if not cat_records:
                continue

            stats = {
                "n": len(cat_records),
                "avg_groundedness": round(
                    sum(r["groundedness_score"] for r in cat_records) / len(cat_records), 2
                ),
                "avg_citation": round(
                    sum(r["citation_score"] for r in cat_records) / len(cat_records), 2
                ),
            }

            # Retrieval recall (exclude queries with no expected sources)
            rr_vals = [r["retrieval_recall"] for r in cat_records if r["retrieval_recall"] is not None]
            if rr_vals:
                stats["avg_retrieval_recall"] = round(sum(rr_vals) / len(rr_vals), 2)
                stats["n_retrieval_recall"] = len(rr_vals)

            # Context utilization
            cu_vals = [r["context_utilization"] for r in cat_records if r["context_utilization"] is not None]
            if cu_vals:
                stats["avg_context_utilization"] = round(sum(cu_vals) / len(cu_vals), 2)

            # Completeness (if scored)
            if not dry_run:
                comp_vals = [r["completeness_score"] for r in cat_records if r.get("completeness_score") is not None]
                if comp_vals:
                    stats["avg_completeness"] = round(sum(comp_vals) / len(comp_vals), 2)

            mode_stats["by_category"][cat] = stats

        # Overall averages
        all_g = [r["groundedness_score"] for r in mode_records]
        all_c = [r["citation_score"] for r in mode_records]
        all_rr = [r["retrieval_recall"] for r in mode_records if r["retrieval_recall"] is not None]
        all_cu = [r["context_utilization"] for r in mode_records if r["context_utilization"] is not None]

        mode_stats["overall"] = {
            "avg_groundedness": round(sum(all_g) / len(all_g), 2),
            "avg_citation": round(sum(all_c) / len(all_c), 2),
            "avg_retrieval_recall": round(sum(all_rr) / len(all_rr), 2) if all_rr else None,
            "avg_context_utilization": round(sum(all_cu) / len(all_cu), 2) if all_cu else None,
        }

        if not dry_run:
            all_comp = [r["completeness_score"] for r in mode_records if r.get("completeness_score") is not None]
            if all_comp:
                mode_stats["overall"]["avg_completeness"] = round(sum(all_comp) / len(all_comp), 2)

        summary["modes"][mode_label] = mode_stats

    return summary


def print_summary(summary, dry_run=False):
    """Print a formatted summary table."""
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY (4 metrics)")
    print("=" * 80)

    headers = ["Category", "n", "Ground", "Citation", "Complete", "Ret.Recall", "Ctx.Util"]
    row_fmt = "{:<12s} {:>3s} {:>7s} {:>8s} {:>8s} {:>10s} {:>8s}"

    for mode_label in ["rerank", "baseline"]:
        mode = summary["modes"].get(mode_label, {})
        print(f"\n{mode_label.upper()} (n={mode.get('n', 0)}):")
        print(row_fmt.format(*headers))
        print("-" * 65)

        for cat in ["direct", "synthesis", "edge_case"]:
            s = mode.get("by_category", {}).get(cat, {})
            if not s:
                continue
            comp = str(s.get("avg_completeness", "-")) if not dry_run else "-"
            rr = str(s.get("avg_retrieval_recall", "-"))
            cu = str(s.get("avg_context_utilization", "-"))
            print(row_fmt.format(
                cat, str(s["n"]),
                str(s["avg_groundedness"]), str(s["avg_citation"]),
                comp, rr, cu
            ))

        o = mode.get("overall", {})
        comp_o = str(o.get("avg_completeness", "-")) if not dry_run else "-"
        rr_o = str(o.get("avg_retrieval_recall", "-"))
        cu_o = str(o.get("avg_context_utilization", "-"))
        print("-" * 65)
        print(row_fmt.format(
            "OVERALL", str(mode["n"]),
            str(o["avg_groundedness"]), str(o["avg_citation"]),
            comp_o, rr_o, cu_o
        ))


if __name__ == "__main__":
    main()
