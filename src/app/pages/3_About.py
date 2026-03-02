"""About page — corpus overview, architecture, citation guide, and enhancement description."""

import os
import sys

import streamlit as st
import pandas as pd
from pathlib import Path

# Ensure project root is on the path.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")

from src.app.components.styles import inject_custom_css
inject_custom_css()

st.title("About This Portal")

# -------------------------------------------------------------------
# RESEARCH QUESTION
# -------------------------------------------------------------------
st.header("Research Question")

st.markdown("""
**What are the key failure modes and limitations of machine learning systems
in space debris tracking and collision avoidance?**

This portal investigates six sub-questions spanning ML approaches, data quality
issues, generalization failures, uncertainty quantification, operational
decision-making barriers, and validation challenges with rare events. The corpus
was curated to provide evidence across all six dimensions.
""")

# -------------------------------------------------------------------
# CORPUS
# -------------------------------------------------------------------
st.header("Corpus")

st.markdown("""
The corpus contains **20 sources** published between 2008 and 2025, producing
**1,628 semantically chunked paragraphs**. Sources span peer-reviewed journal
articles, conference papers, and technical reports from NASA, ESA, RAND, and
the IADC.
""")

# Load manifest for the table
manifest_path = Path("data_manifest.csv")
if manifest_path.exists():
    df = pd.read_csv(manifest_path)
    # Select and rename columns for display
    display_df = df[["source_id", "title", "year", "source_type", "tags"]].copy()
    display_df.columns = ["Source ID", "Title", "Year", "Type", "Tags"]
    display_df = display_df.sort_values("Year", ascending=False)
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Source ID": st.column_config.TextColumn(width="small"),
            "Title": st.column_config.TextColumn(width="large"),
            "Year": st.column_config.NumberColumn(format="%d", width="small"),
            "Type": st.column_config.TextColumn(width="small"),
            "Tags": st.column_config.TextColumn(width="medium"),
        },
    )
else:
    st.warning("data_manifest.csv not found.")

st.markdown("""
All 20 papers were chunked manually with Claude following a structured protocol
(`CHUNKING_PROTOCOL.md`), producing section-aware paragraph
IDs (e.g., `sec3.1_p2`) that preserve the hierarchical document structure.
Automated OCR extraction was attempted and rejected due to poor accuracy on
mathematical notation, tables, and multi-column layouts.
""")

# -------------------------------------------------------------------
# PIPELINE ARCHITECTURE
# -------------------------------------------------------------------
st.header("Pipeline Architecture")

st.markdown("The system follows a four-stage pipeline:")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("### 🔍 Retrieve")
    st.caption(
        "Queries are embedded with `all-mpnet-base-v2` and matched against "
        "1,628 chunk embeddings in ChromaDB. Top 20 by cosine similarity. "
        "Optional metadata filters (year, type, tags) narrow the search."
    )
with col2:
    st.markdown("### ⚖️ Rerank")
    st.caption(
        "A cross-encoder (`ms-marco-MiniLM-L-6-v2`) re-scores each "
        "query–chunk pair jointly. Top 10 after reranking are passed "
        "to generation. This is the Phase 2 enhancement."
    )
with col3:
    st.markdown("### 💬 Generate")
    st.caption(
        "Claude Sonnet (`claude-sonnet-4-5-20250929`) produces a "
        "citation-grounded answer from the 10 reranked chunks. Every "
        "factual claim must cite a `(source_id, chunk_id)` pair."
    )
with col4:
    st.markdown("### 📋 Log")
    st.caption(
        "Every pipeline run is logged as structured JSON with the query, "
        "all retrieved/reranked chunks, the generated answer, model "
        "name, prompt version, and token usage."
    )

# -------------------------------------------------------------------
# HOW CITATIONS WORK
# -------------------------------------------------------------------
st.header("How Citations Work")

st.markdown("""
Every factual claim in the system's answers is backed by a citation in
`(source_id, chunk_id)` format. For example, the citation `(mashiku2025, sec5_p1)`, resolves to a specific paragraph in a specific source document.

**The citation chain:**

1. **Manifest** → `source_id` resolves to a title, authors, year, and DOI
   via `data_manifest.csv`.
2. **Chunk** → `chunk_id` resolves to a specific paragraph within the source's
   chunked file under `data/processed/`.
3. **Evidence** → The citation card in the UI shows the actual chunk text so
   you can verify the claim against its source.

**Trust behaviors:**
- The generation prompt instructs the model to **only cite chunks from the
  evidence window** and to **refuse to fabricate citations**.
- If evidence is insufficient, the system **explicitly says so** rather than
  generating unsupported claims.
- As an added fallback, citation cards in the UI only highlight citations that match real retrieved
  chunks. Unverified references are not bolded.
- Artifact generation (evidence tables and synthesis memos) passes through a
  **citation validation step** that checks every `(source_id, chunk_id)` pair
  against the thread's available evidence.
""")

# -------------------------------------------------------------------
# PHASE 3 ENHANCEMENT: METADATA FILTERING
# -------------------------------------------------------------------
st.header("Phase 3 Enhancement: Metadata Filtering")

st.markdown("""
Phase 3 adds metadata filtering as a pipeline enhancement, giving researchers
control over which evidence the system considers. Filters are applied at
retrieval time via ChromaDB's native `where` clauses, narrowing the chunk pool
before embedding similarity is computed.

Each of the 11 tags is stored as an individual boolean metadata field on every
chunk (e.g., `tag_operational_integration: True`). Filters use `$eq` operators
on these boolean fields, which avoids the pitfalls of substring matching on
delimited strings and ensures reliable, composable queries when multiple tags
are selected.

**Filter dimensions:**
""")

tag_data = {
    "Axis": [
        "Domain Application", "Domain Application", "Domain Application", "Domain Application",
        "ML Limitation Theme", "ML Limitation Theme", "ML Limitation Theme", "ML Limitation Theme",
        "Content Role", "Content Role", "Content Role",
    ],
    "Tag": [
        "collision-avoidance", "orbit-prediction", "debris-environment", "detection-classification",
        "data-quality", "generalization", "uncertainty-quantification", "operational-integration",
        "survey", "benchmark", "policy",
    ],
    "Sources": [6, 7, 4, 4, 7, 5, 5, 5, 2, 2, 4],
}

st.dataframe(
    pd.DataFrame(tag_data),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Axis": st.column_config.TextColumn(width="medium"),
        "Tag": st.column_config.TextColumn(width="medium"),
        "Sources": st.column_config.ProgressColumn(
            "Sources", min_value=0, max_value=7, format="%d",
        ),
    },
)

st.markdown("""
The tag scheme was designed so that every tag appears on 2–7 sources (average
2.5 per source), ensuring that any filter selection meaningfully narrows results
without eliminating them. The three axes are orthogonal: domain captures *what*
the paper studies, limitation captures *what failure mode* it addresses, and role
captures *how* it functions in the corpus.

Year range and source type filters are also available, using ChromaDB's native
metadata fields.
""")

# -------------------------------------------------------------------
# RESEARCH ARTIFACTS
# -------------------------------------------------------------------
st.header("Research Artifacts")

st.markdown("""
The portal generates two artifact types from saved research threads:

**Evidence Table** — Extracts discrete claims from a thread's answer and maps
each to its supporting evidence, citation, confidence level (high/medium/low),
and any caveats. Exported as CSV. Useful for systematic evidence mapping and
identifying where claims rest on thin evidence.

**Synthesis Memo** — An 800–1,200 word research document synthesized from the
thread's evidence chunks (not from the answer — this produces an independent
analysis). Uses inline `(source_id, chunk_id)` citations throughout, with a
reference list. Exported as Markdown and PDF. Useful as a starting point for
literature review sections or research summaries.

Both artifact types undergo citation validation before display: every cited
`(source_id, chunk_id)` is checked against the chunks available in the thread.
Invalid citations trigger a visible warning.
""")

# -------------------------------------------------------------------
# OFFLINE / DEMO MODE
# -------------------------------------------------------------------
st.header("Offline Mode")

st.markdown("""
The portal ships with a pre-seeded cache of query results and generated
artifacts. When no API key is configured, the app automatically runs in
**offline mode**, serving all cached content without any network calls.
Retrieval and reranking still work locally (the embedding model and
cross-encoder run on-device), so uncached queries return retrieved evidence
even without generation.

A banner at the top of each page indicates whether the app is running in
live or offline mode.
""")

# -------------------------------------------------------------------
# TOOLS AND MODELS
# -------------------------------------------------------------------
st.header("Tools and Models")

tools_data = {
    "Component": [
        "Vector store",
        "Embedding model",
        "Reranker",
        "Generation model",
        "Evaluation judge",
        "UI framework",
        "PDF export",
    ],
    "Tool": [
        "ChromaDB",
        "all-mpnet-base-v2 (sentence-transformers)",
        "ms-marco-MiniLM-L-6-v2 (cross-encoder)",
        "Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)",
        "Claude Opus 4.6 (claude-opus-4-6)",
        "Streamlit",
        "fpdf2",
    ],
    "Why": [
        "Supports native metadata filtering for Phase 3 tags",
        "Best semantic quality for small technical corpus (768-dim, cosine)",
        "Joint query–chunk scoring improves relevance ranking",
        "Cost-efficient for 50+ eval runs; configurable via flag",
        "Stronger reasoning model reduces risk of missed errors",
        "Assignment-recommended; single-command run",
        "Lightweight PDF generation for artifact export",
    ],
}

st.dataframe(
    pd.DataFrame(tools_data),
    use_container_width=True,
    hide_index=True,
)

# -------------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------------
st.divider()
st.caption("Kaitlin Moore (kmoore2) · AI Model Development · CMU · 2026")
