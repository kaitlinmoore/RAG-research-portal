"""Evaluation Dashboard — displays Phase 2 eval results and metrics.

Reads from logs/eval_results_v2.jsonl (50 records) and
logs/eval_results_v2.summary.json (aggregate stats). Fully offline —
no API calls required.
"""

import json
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Evaluation", page_icon="\U0001F4CA", layout="wide")

# Ensure project root is on the path.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.app.components.styles import inject_custom_css
inject_custom_css()

st.title("Evaluation Dashboard")

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

SUMMARY_PATH = "logs/eval_results_v2.summary.json"
RECORDS_PATH = "logs/eval_results_v2.jsonl"


@st.cache_data
def load_summary() -> dict:
    with open(SUMMARY_PATH) as f:
        return json.load(f)


@st.cache_data
def load_records() -> pd.DataFrame:
    return pd.read_json(RECORDS_PATH, lines=True)


if not os.path.exists(SUMMARY_PATH) or not os.path.exists(RECORDS_PATH):
    st.error(
        "Evaluation log files not found. Expected:\n"
        f"- `{SUMMARY_PATH}`\n"
        f"- `{RECORDS_PATH}`"
    )
    st.stop()

summary = load_summary()
df = load_records()

st.caption(
    f"**{summary['total_runs']}** evaluation runs | "
    f"Judge: {summary.get('judge_model', 'N/A')} | "
    f"Run date: {summary.get('run_date', 'N/A')[:10]}"
)

# ---------------------------------------------------------------------------
# Summary metrics row
# ---------------------------------------------------------------------------
st.markdown("### Overall Metrics")
st.caption("Reranking mode scores with delta vs. baseline")

rerank = summary["modes"]["rerank"]["overall"]
baseline = summary["modes"]["baseline"]["overall"]

METRICS = [
    ("Groundedness", "avg_groundedness", "/4"),
    ("Citation", "avg_citation", "/4"),
    ("Completeness", "avg_completeness", "/4"),
    ("Retrieval Recall", "avg_retrieval_recall", ""),
    ("Context Utilization", "avg_context_utilization", ""),
]

cols = st.columns(len(METRICS))
for col, (label, key, suffix) in zip(cols, METRICS):
    rerank_val = rerank[key]
    baseline_val = baseline[key]
    delta = round(rerank_val - baseline_val, 2)
    with col:
        st.metric(
            label=label,
            value=f"{rerank_val:.2f}{suffix}",
            delta=f"{delta:+.2f} vs baseline" if delta != 0 else "same as baseline",
            delta_color="normal" if delta >= 0 else "inverse",
        )

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
st.markdown("### Performance by Category")

chart_col1, chart_col2 = st.columns(2)

# Chart A: Grouped bar chart — selected metric by category
with chart_col1:
    metric_options = {
        "Groundedness": "avg_groundedness",
        "Citation": "avg_citation",
        "Completeness": "avg_completeness",
        "Retrieval Recall": "avg_retrieval_recall",
        "Context Utilization": "avg_context_utilization",
    }
    selected_metric_label = st.selectbox(
        "Metric",
        options=list(metric_options.keys()),
        index=4,  # Default to Context Utilization (most interesting delta)
    )
    selected_metric_key = metric_options[selected_metric_label]

    categories = ["direct", "synthesis", "edge_case"]
    category_labels = ["Direct", "Synthesis", "Edge-case"]

    rerank_vals = [
        summary["modes"]["rerank"]["by_category"][cat][selected_metric_key]
        for cat in categories
    ]
    baseline_vals = [
        summary["modes"]["baseline"]["by_category"][cat][selected_metric_key]
        for cat in categories
    ]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Reranking",
        x=category_labels,
        y=rerank_vals,
        marker_color="#21918C",
        text=[f"{v:.2f}" for v in rerank_vals],
        textposition="outside",
    ))
    fig_bar.add_trace(go.Bar(
        name="Baseline",
        x=category_labels,
        y=baseline_vals,
        marker_color="#6A0572",
        text=[f"{v:.2f}" for v in baseline_vals],
        textposition="outside",
    ))

    # Set y-axis range based on metric type
    is_score_metric = selected_metric_key in ("avg_groundedness", "avg_citation", "avg_completeness")
    y_max = 4.5 if is_score_metric else 1.1

    fig_bar.update_layout(
        barmode="group",
        title=f"{selected_metric_label} by Category",
        yaxis=dict(range=[0, y_max], title=selected_metric_label),
        xaxis=dict(title="Category"),
        height=480,
        margin=dict(t=60, b=100),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Chart B: Radar chart — rerank vs. baseline across all 5 metrics
with chart_col2:
    radar_labels = ["Groundedness", "Citation", "Completeness", "Recall", "Context<br>Utilization"]
    radar_keys = [
        "avg_groundedness", "avg_citation", "avg_completeness",
        "avg_retrieval_recall", "avg_context_utilization",
    ]
    # Normalize: score metrics /4, ratio metrics already 0-1
    divisors = [4.0, 4.0, 4.0, 1.0, 1.0]

    rerank_radar = [rerank[k] / d for k, d in zip(radar_keys, divisors)]
    baseline_radar = [baseline[k] / d for k, d in zip(radar_keys, divisors)]

    # Close the polygon
    rerank_radar.append(rerank_radar[0])
    baseline_radar.append(baseline_radar[0])
    radar_labels_closed = radar_labels + [radar_labels[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=rerank_radar,
        theta=radar_labels_closed,
        fill="toself",
        name="Reranking",
        fillcolor="rgba(33, 145, 140, 0.2)",
        line=dict(color="#21918C"),
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=baseline_radar,
        theta=radar_labels_closed,
        fill="toself",
        name="Baseline",
        fillcolor="rgba(106, 5, 114, 0.15)",
        line=dict(color="#6A0572", dash="dash"),
    ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1.05])),
        title="Rerank vs. Baseline (Normalized)",
        height=480,
        margin=dict(t=60, b=100),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ---------------------------------------------------------------------------
# Per-query detail table
# ---------------------------------------------------------------------------
st.markdown("### Per-Query Results")

# Filters
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    cat_filter = st.selectbox(
        "Category",
        options=["All", "direct", "synthesis", "edge_case"],
        index=0,
    )
with filter_col2:
    mode_filter = st.radio(
        "Mode",
        options=["All", "Reranking", "Baseline"],
        horizontal=True,
    )

# Apply filters
filtered = df.copy()
if cat_filter != "All":
    filtered = filtered[filtered["category"] == cat_filter]
if mode_filter == "Reranking":
    filtered = filtered[filtered["use_reranker"] == True]  # noqa: E712
elif mode_filter == "Baseline":
    filtered = filtered[filtered["use_reranker"] == False]  # noqa: E712

# Format failure_tags for display
filtered["mode"] = filtered["use_reranker"].map({True: "rerank", False: "baseline"})
filtered["failure_tags_str"] = filtered["failure_tags"].apply(
    lambda tags: ", ".join(tags) if isinstance(tags, list) and tags else "none"
)

# Display table
display_cols = [
    "query_id", "category", "mode",
    "groundedness_score", "citation_score", "completeness_score",
    "retrieval_recall", "context_utilization", "failure_tags_str",
]
st.dataframe(
    filtered[display_cols].sort_values(["query_id", "mode"]),
    use_container_width=True,
    hide_index=True,
    column_config={
        "query_id": st.column_config.TextColumn("Query", width="small"),
        "category": st.column_config.TextColumn("Category", width="small"),
        "mode": st.column_config.TextColumn("Mode", width="small"),
        "groundedness_score": st.column_config.NumberColumn("Ground.", format="%d", width="small"),
        "citation_score": st.column_config.NumberColumn("Citation", format="%d", width="small"),
        "completeness_score": st.column_config.NumberColumn("Complete.", format="%d", width="small"),
        "retrieval_recall": st.column_config.NumberColumn("Recall", format="%.2f", width="small"),
        "context_utilization": st.column_config.NumberColumn("Ctx Util", format="%.2f", width="small"),
        "failure_tags_str": st.column_config.TextColumn("Failure Tags", width="medium"),
    },
)

# ---------------------------------------------------------------------------
# Query detail drill-down
# ---------------------------------------------------------------------------
st.markdown("### Query Detail")

query_ids = sorted(filtered["query_id"].unique())
if query_ids:
    selected_query = st.selectbox("Select a query to inspect", options=query_ids)
    query_rows = filtered[filtered["query_id"] == selected_query]

    for _, row in query_rows.iterrows():
        mode_label = "Reranking" if row["use_reranker"] else "Baseline"
        with st.expander(f"{row['query_id']} — {mode_label}", expanded=len(query_rows) == 1):
            st.markdown(f"**Query:** {row['query']}")
            st.markdown(f"**Category:** {row['category']} | **Expected sources:** {row.get('expected_sources', 'N/A')}")

            score_cols = st.columns(5)
            with score_cols[0]:
                st.metric("Groundedness", f"{row['groundedness_score']}/4")
            with score_cols[1]:
                st.metric("Citation", f"{row['citation_score']}/4")
            with score_cols[2]:
                st.metric("Completeness", f"{row['completeness_score']}/4")
            with score_cols[3]:
                st.metric("Recall", f"{row['retrieval_recall']:.2f}")
            with score_cols[4]:
                st.metric("Ctx Util", f"{row['context_utilization']:.2f}")

            if row.get("groundedness_rationale"):
                st.caption(f"**Groundedness:** {row['groundedness_rationale']}")
            if row.get("citation_rationale"):
                st.caption(f"**Citation:** {row['citation_rationale']}")
            if row.get("completeness_rationale"):
                st.caption(f"**Completeness:** {row['completeness_rationale']}")

            tags = row.get("failure_tags", [])
            if isinstance(tags, list) and tags:
                st.warning(f"Failure tags: {', '.join(tags)}")

            if row.get("answer"):
                st.markdown("**Answer (excerpt):**")
                answer_text = str(row["answer"])
                if len(answer_text) > 500:
                    st.text(answer_text[:500] + "...")
                else:
                    st.text(answer_text)

# ---------------------------------------------------------------------------
# Key insights
# ---------------------------------------------------------------------------
st.markdown("### Key Insights")

st.markdown("""
- **Groundedness is perfect (4.0/4)** across both modes and all categories — no hallucinated claims detected in any of the 50 runs.
- **Reranking improves context utilization** from 0.40 to 0.46 (+15%), most visible in synthesis queries where it increases from 0.57 to 0.64.
- **Completeness is the weakest metric** (3.68–3.72/4) — the model does not always exploit all available evidence, leaving some relevant chunks uncited.
- **Citation accuracy is near-perfect**, with rare minor issues only on edge-case queries (3.83/4 for reranking edge cases vs. 4.0/4 for baseline).
- **Retrieval recall is identical** between modes (0.84) — reranking reorders chunks but does not affect what is retrieved from ChromaDB.
""")

st.caption(
    f"Evaluation ran {summary['total_runs']} queries (25 queries x 2 modes) "
    f"judged by {summary.get('judge_model', 'N/A')} on {summary.get('run_date', 'N/A')[:10]}."
)
