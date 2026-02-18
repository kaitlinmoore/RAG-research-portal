"""
src/eval/ — Evaluation suite for the RAG pipeline.

Modules:
    queries.json  — 25 evaluation queries (direct, synthesis, edge-case)
    scorer.py     — LLM-as-judge scoring (groundedness + citation correctness)
    run_eval.py   — Orchestrates evaluation runs and saves results
"""
