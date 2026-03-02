"""Citation card component — renders expandable source cards under answers."""

import re

import streamlit as st


def render_citation_cards(chunks: list[dict]) -> None:
    """Display reranked chunks as expandable citation cards.

    Each card shows:
    - Header: [i] (source_id, chunk_id) — section_title
    - Expanded: full chunk text, metadata row (year, type, venue, tags, rerank score)
    """
    if not chunks:
        return

    st.markdown(f"**Sources** ({len(chunks)} chunks)")

    for i, chunk in enumerate(chunks):
        source_id = chunk.get("source_id", "unknown")
        chunk_id = chunk.get("chunk_id", "unknown")
        section = chunk.get("section_title", "")
        label = f"[{i + 1}] ({source_id}, {chunk_id}) — {section}"

        with st.expander(label, expanded=False):
            st.markdown(chunk.get("text", ""))
            st.divider()

            cols = st.columns(4)
            cols[0].caption(f"Year: {chunk.get('year', 'N/A')}")
            cols[1].caption(f"Type: {chunk.get('doc_type', 'N/A')}")
            cols[2].caption(f"Tags: {chunk.get('tags', 'N/A')}")
            if chunk.get("rerank_score") is not None:
                cols[3].caption(f"Rerank: {chunk['rerank_score']:.4f}")
            else:
                dist = chunk.get("distance")
                if dist is not None:
                    cols[3].caption(f"Distance: {dist:.4f}")

            venue = chunk.get("venue", "")
            if venue:
                st.caption(f"Venue: {venue}")


def highlight_citations_in_answer(answer: str, chunks: list[dict]) -> str:
    """Make (source_id, chunk_id) citations bold in the answer text.

    Only highlights citations that match a real chunk from the result
    (trust behavior — don't bold fabricated citations).
    """
    if not answer or not chunks:
        return answer or ""

    # Build set of valid (source_id, chunk_id) pairs from the chunks
    valid_citations = set()
    for chunk in chunks:
        sid = chunk.get("source_id", "")
        cid = chunk.get("chunk_id", "")
        if sid and cid:
            valid_citations.add((sid, cid))

    def _bold_if_valid(match: re.Match) -> str:
        source_id = match.group(1).strip()
        chunk_id = match.group(2).strip()
        if (source_id, chunk_id) in valid_citations:
            return f"**({source_id}, {chunk_id})**"
        return match.group(0)  # Leave unmatched citations as-is

    # Match (source_id, chunk_id) patterns — source_id is word chars,
    # chunk_id is like sec2.1_p3 or sec2.3_p1_1
    pattern = r"\((\w+),\s*(sec[\d.]+_p\d+(?:_\d+)?)\)"
    return re.sub(pattern, _bold_if_valid, answer)
