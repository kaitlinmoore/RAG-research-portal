"""Metadata filter sidebar widgets for narrowing retrieval results."""

from typing import Optional

import streamlit as st


# Tag options by axis (from PHASE3_PLAN.md §5)
DOMAIN_TAGS = [
    "collision-avoidance",
    "orbit-prediction",
    "debris-environment",
    "detection-classification",
]

LIMITATION_TAGS = [
    "data-quality",
    "generalization",
    "uncertainty-quantification",
    "operational-integration",
]

ROLE_TAGS = [
    "survey",
    "benchmark",
    "policy",
]

SOURCE_TYPES = [
    "peer-reviewed",
    "conference-paper",
    "technical-report",
]

YEAR_MIN = 2008
YEAR_MAX = 2025


def tag_to_field(tag: str) -> str:
    """Convert a tag name to its boolean metadata field name.

    E.g. "operational-integration" → "tag_operational_integration"
    """
    return f"tag_{tag.replace('-', '_')}"


def build_where_clause(
    year_range: tuple[int, int],
    source_types: list[str],
    domain_tags: list[str],
    limitation_tags: list[str],
    role_tags: list[str],
) -> Optional[dict]:
    """Build a ChromaDB where clause from filter selections.

    Returns None if no filters are active.
    """
    conditions = []

    # Year filter (only if narrowed from full range)
    if year_range != (YEAR_MIN, YEAR_MAX):
        conditions.append({"year": {"$gte": year_range[0]}})
        conditions.append({"year": {"$lte": year_range[1]}})

    # Source type filter (only if not all selected)
    if source_types and len(source_types) < len(SOURCE_TYPES):
        conditions.append({"doc_type": {"$in": source_types}})

    # Tag filters — each selected tag maps to a boolean metadata field.
    all_tags = (domain_tags or []) + (limitation_tags or []) + (role_tags or [])
    for tag in all_tags:
        conditions.append({tag_to_field(tag): {"$eq": True}})

    if not conditions:
        return None
    elif len(conditions) == 1:
        return conditions[0]
    else:
        return {"$and": conditions}


def render_filters() -> Optional[dict]:
    """Render filter widgets in the sidebar and return a ChromaDB where clause.

    Returns None if no filters are active.
    """
    with st.sidebar:
        st.header("Filters")

        year_range = st.slider(
            "Year range",
            min_value=YEAR_MIN,
            max_value=YEAR_MAX,
            value=(YEAR_MIN, YEAR_MAX),
        )

        source_types = st.multiselect(
            "Source type",
            options=SOURCE_TYPES,
            default=SOURCE_TYPES,
        )

        st.subheader("Tags")

        domain_tags = st.multiselect("Domain", options=DOMAIN_TAGS)
        limitation_tags = st.multiselect("ML Limitation", options=LIMITATION_TAGS)
        role_tags = st.multiselect("Content Role", options=ROLE_TAGS)

    return build_where_clause(
        year_range, source_types, domain_tags, limitation_tags, role_tags
    )
