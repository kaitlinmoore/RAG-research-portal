# Personal Research Portal: ML Failure Modes in Space Debris Tracking

A research-grade Retrieval-Augmented Generation (RAG) pipeline for exploring ML failure modes and limitations in space debris tracking and collision avoidance. Built for CMU's AI Modeling course (Phases 2-3).

**Research question:** What are the key failure modes and limitations of ML systems for space debris tracking and collision avoidance?

**Author:** Kaitlin Moore (kmoore2)

## Quick Start

### Prerequisites

- Python 3.10+
- An Anthropic API key: A `grader.env` file was uploaded to Canvas with a unique API key attached to a tiny budget for grading purposes. Please limit use to grading evaluation.

### Setup

```bash
# 1. Create and activate a Python virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place the grader.env file (from Canvas) in the project root.
#    It contains a single line: ANTHROPIC_API_KEY={API KEY}.
#    The pipeline loads grader.env automatically — no renaming needed.

# 4. Ask a question (retrieves, reranks, generates, logs — one command)
python -m src.rag.query "What are the main failure modes of ML for collision avoidance?"
```

> **Note for graders:** Download `grader.env` from Canvas and place it in the repository root directory (next to `README.md`). The pipeline loads it automatically — no renaming or environment variable setup required.

## What This Does

Given a natural-language research question, the pipeline:

1. **Retrieves** the 20 most relevant chunks from a 1,628-chunk academic corpus using semantic search (ChromaDB + `all-mpnet-base-v2`)
2. **Reranks** them with a cross-encoder (`ms-marco-MiniLM-L-6-v2`) to surface the best 10
3. **Generates** a grounded answer with inline `(source_id, chunk_id)` citations using the Anthropic API
4. **Logs** the full run (query, retrieved chunks, answer, model, prompt version, token usage) to `logs/rag_queries.jsonl`

Every citation resolves to a real chunk in the corpus. The system refuses to invent citations and explicitly flags missing or conflicting evidence.

## Corpus

20 sources (2008-2025) spanning peer-reviewed papers, conference papers, and technical reports on space debris tracking, conjunction assessment, and ML applications in space situational awareness. Metadata is tracked in `data_manifest.csv`.

Sources include ESA conjunction data studies, NASA handbooks, RAND analyses of AI for SSA, ML competition results, survey papers on orbit prediction and RSO characterization, and domain-specific work on uncertainty quantification, Kessler syndrome modeling, and deep learning for radar-based debris detection.

All papers were manually chunked into structured Markdown following a consistent protocol (section headers, paragraph-level chunk IDs), then embedded and stored in ChromaDB.

## Project Structure

```
.
├── data/
│   ├── raw/                    # Original PDFs (20 papers)
│   ├── processed/              # Chunked Markdown files (20 papers, 1,628 chunks)
│   └── chromadb/               # Vector store
├── src/
│   ├── ingest/
│   │   ├── parser.py           # Parses chunked Markdown into structured dicts
│   │   └── ingest.py           # Embeds chunks into ChromaDB with metadata
│   ├── rag/
│   │   ├── retriever.py        # Semantic search with optional metadata filters
│   │   ├── reranker.py         # Cross-encoder reranking
│   │   ├── prompts.py          # Citation-enforcing prompt templates (versioned)
│   │   ├── generator.py        # Anthropic API generation
│   │   ├── logger.py           # Structured JSONL logging
│   │   ├── pipeline.py         # Orchestrator: retrieve -> rerank -> generate -> log
│   │   └── query.py            # CLI entry point
│   └── eval/
│       ├── queries.json        # 25 evaluation queries (direct, synthesis, edge-case)
│       ├── scorer.py           # LLM-as-judge (groundedness + citation correctness)
│       ├── run_eval.py         # Evaluation runner (both modes, incremental output)
│       └── score_completeness.py  # Completeness scoring + mechanical metrics
├── logs/                       # Query logs and evaluation results (JSONL)
├── data_manifest.csv           # Corpus metadata (20 sources)
├── requirements.txt            # Pinned dependencies
```

## Usage

### Ask a Question

```bash
# Default: retrieve + rerank + generate with citations
python -m src.rag.query "What uncertainty quantification methods are used for thermospheric density modeling?"

# Skip reranking (baseline comparison)
python -m src.rag.query "How does class imbalance affect ML models?" --no-rerank

# Use a different model
python -m src.rag.query "What is the Kessler syndrome?" --model claude-opus-4-6
```

### Run the Evaluation Suite

The evaluation suite runs 25 queries in two modes (with and without reranking) and scores each response using LLM-as-judge.

```bash
# Dry-run a single query (no scoring, no API cost beyond generation)
python -m src.eval.run_eval --no-score --filter "D01"

# Full evaluation with Opus as judge (50 pipeline runs + 50 judge calls)
python -m src.eval.run_eval --judge-model claude-opus-4-6

# Rerank mode only
python -m src.eval.run_eval --rerank-only --judge-model claude-opus-4-6
```

### Add Completeness Scores

Supplements existing evaluation results with completeness scoring and mechanical metrics (retrieval recall, context utilization).

```bash
# Mechanical metrics only (no API calls)
python -m src.eval.score_completeness --dry-run

# Full run with completeness scoring
python -m src.eval.score_completeness
```

## Evaluation Results

Claude Opus 4.6 LLM-as-Judge scored 25 queries across three categories, each run with and without reranking (50 total). Retrieval Recall and Context Utilization were calculated.

| Mode | Groundedness | Citation | Completeness | Retrieval Recall | Context Utilization |
|------|:---:|:---:|:---:|:---:|:---:|
| **With Reranking** | 4.00 | 3.96 | 3.72 | 0.84 | 0.46 |
| **Baseline** | 4.00 | 4.00 | 3.68 | 0.84 | 0.40 |

**Scoring rubric:** 1-4 scale where 4 = fully correct/complete, 1 = not usable.

Key findings:
- Groundedness is consistently perfect: the system does not hallucinate beyond retrieved evidence
- Reranking improves context utilization (0.40 to 0.46), especially for synthesis queries
- Completeness is the most discriminating metric, varying across query types
- Edge-case queries show lower retrieval recall (0.67) as expected for out-of-scope topics

## Architecture

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Vector store | ChromaDB | Metadata filtering support for Phase 3 portal |
| Embeddings | `all-mpnet-base-v2` | Best quality for small academic corpora; 768-dim, cosine similarity |
| Reranker | `ms-marco-MiniLM-L-6-v2` | Cross-encoder reranking as measurable Phase 2 enhancement |
| Generator | Claude Sonnet (Anthropic API) | Cost-effective for iterative evaluation runs |
| Judge | Claude Opus | Stronger model judges weaker to reduce shared-bias |
| Chunking | Manual with structured IDs | Image-based PDFs made automated extraction unreliable |

## Dependencies

- Python 3.10+
- `chromadb` -- vector store
- `sentence-transformers` -- embedding and cross-encoder models
- `anthropic` -- LLM generation and scoring
- `python-dotenv` -- environment variable management

Install with:
```bash
pip install -r requirements.txt
```

## Logs and Output

All pipeline runs are logged to `logs/rag_queries.jsonl` as structured records containing the query, all retrieved/reranked chunks, the generated answer, model name, prompt version, and token usage.

Evaluation output:
- `logs/eval_results.jsonl` -- per-query scores (groundedness, citation, failure tags)
- `logs/eval_results_v2.jsonl` -- enriched with completeness, retrieval recall, context utilization
- `logs/eval_results_v2.summary.json` -- aggregate statistics
