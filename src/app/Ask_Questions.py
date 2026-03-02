"""Personal Research Portal — Ask Questions page (main entry point).

Run with: streamlit run src/app/Ask_Questions.py
"""

import os
import sys
import time

import anthropic
import streamlit as st
from dotenv import load_dotenv

# Ensure project root is on the path so imports work when Streamlit runs this file.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

load_dotenv()

from src.cache.manager import CacheManager
from src.rag.pipeline import RAGPipeline
from src.threads.manager import ThreadManager
from src.app.components.mode_banner import render_mode_banner
from src.app.components.filters import render_filters
from src.app.components.citation_card import render_citation_cards, highlight_citations_in_answer
from src.app.components.styles import inject_button_css


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Research Portal", page_icon="\U0001F50D", layout="wide")
inject_button_css()
st.title("Personal Research Portal")
st.subheader("ML Failure Modes in Space Debris Tracking")


# ---------------------------------------------------------------------------
# Initialise session state
# ---------------------------------------------------------------------------
if "mode" not in st.session_state:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    st.session_state.mode = "live" if api_key else "offline"

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ---------------------------------------------------------------------------
# Cached resources (survive Streamlit reruns)
# ---------------------------------------------------------------------------
@st.cache_resource
def get_pipeline() -> RAGPipeline:
    """Load the RAG pipeline once (embedding model + ChromaDB collection)."""
    return RAGPipeline()


@st.cache_resource
def get_cache() -> CacheManager:
    """Initialise the cache manager once."""
    return CacheManager()


thread_mgr = ThreadManager()

MIN_QUERY_INTERVAL = 2.0  # seconds between API calls


def rate_limit_check() -> bool:
    """Enforce minimum interval between API calls to avoid rate limits."""
    last_call = st.session_state.get("last_api_call", 0)
    if time.time() - last_call < MIN_QUERY_INTERVAL:
        st.warning("Please wait a moment between queries.")
        return False
    st.session_state.last_api_call = time.time()
    return True


# ---------------------------------------------------------------------------
# Sidebar filters (renders regardless of query state)
# ---------------------------------------------------------------------------
where_filters = render_filters()


# ---------------------------------------------------------------------------
# Mode banner
# ---------------------------------------------------------------------------
render_mode_banner()


# ---------------------------------------------------------------------------
# Query interface
# ---------------------------------------------------------------------------
if "prefill_query" in st.session_state:
    st.session_state["query_input"] = st.session_state.pop("prefill_query")

query = st.text_input(
    "Ask a research question:",
    key="query_input",
    placeholder="e.g., What are the main failure modes of ML for collision avoidance?",
)

if query:
    pipeline = get_pipeline()
    cache = get_cache()
    use_reranker = True

    cache_key = CacheManager.make_query_key(query, use_reranker, where_filters)
    cached = cache.get_query(cache_key)

    if cached:
        # ---- Cache hit ----
        result = cached
        st.caption("Served from cache")
    elif st.session_state.mode == "live":
        # ---- Live query ----
        if not rate_limit_check():
            st.stop()
        with st.spinner("Retrieving and generating answer..."):
            try:
                result = pipeline.run(
                    query,
                    use_reranker=use_reranker,
                    where=where_filters,
                    include_gaps=True,
                )
                cache.put_query(cache_key, result)
            except anthropic.RateLimitError:
                st.warning("API rate limit reached. Showing retrieved evidence only.")
                result = pipeline.retrieve_only(
                    query, use_reranker=use_reranker, where=where_filters,
                )
                result["answer"] = None
            except anthropic.APIConnectionError:
                st.error("Could not connect to Anthropic API. Check your internet connection.")
                result = pipeline.retrieve_only(
                    query, use_reranker=use_reranker, where=where_filters,
                )
                result["answer"] = None
            except anthropic.APIStatusError as e:
                st.error(f"API error (status {e.status_code}). Showing retrieved evidence only.")
                result = pipeline.retrieve_only(
                    query, use_reranker=use_reranker, where=where_filters,
                )
                result["answer"] = None
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                result = pipeline.retrieve_only(
                    query, use_reranker=use_reranker, where=where_filters,
                )
                result["answer"] = None
    else:
        # ---- Offline, no cache hit ----
        with st.spinner("Retrieving evidence (offline mode)..."):
            result = pipeline.retrieve_only(
                query,
                use_reranker=use_reranker,
                where=where_filters,
            )
            result["answer"] = None
        st.warning(
            "This query is not in the cache. "
            "Showing retrieved evidence only (no generation in offline mode)."
        )

    # Store result
    st.session_state.last_result = result
    st.session_state.query_history.append((query, result))

    # ---- Display answer ----
    st.divider()

    reranked = result.get("reranked_chunks", [])
    retrieved = result.get("retrieved_chunks", [])
    chunks_to_show = reranked if reranked else retrieved[:10]

    if result.get("answer"):
        st.markdown("### Answer")
        highlighted = highlight_citations_in_answer(result["answer"], chunks_to_show)
        st.markdown(highlighted)
    else:
        st.markdown("### Retrieved Evidence")
        st.info("No generated answer available. Showing top retrieved chunks.")

    # ---- Citation cards ----
    render_citation_cards(chunks_to_show)

    # ---- Gap finder suggestions ----
    gap_suggestions = result.get("gap_suggestions", [])
    if gap_suggestions:
        with st.expander("Evidence Gaps", expanded=False):
            for i, gap in enumerate(gap_suggestions):
                st.markdown(f"**{gap['gap']}**")
                if st.button(
                    f"Search: {gap['suggested_query'][:60]}",
                    key=f"gap_{i}",
                ):
                    st.session_state["prefill_query"] = gap["suggested_query"]
                    st.rerun()

    # ---- Model info ----
    if result.get("model"):
        st.caption(
            f"Model: {result.get('model', 'N/A')} | "
            f"Prompt: {result.get('prompt_version', 'N/A')} | "
            f"Tokens: {result.get('usage', {}).get('input_tokens', '?')} in / "
            f"{result.get('usage', {}).get('output_tokens', '?')} out"
        )

    # ---- Save to Thread ----
    if st.button("Save to Thread"):
        thread = {
            "query": query,
            "where_filters": where_filters,
            "use_reranker": use_reranker,
            "answer": result.get("answer"),
            "retrieved_chunks": result.get("retrieved_chunks", []),
            "reranked_chunks": result.get("reranked_chunks", []),
            "model": result.get("model"),
            "prompt_version": result.get("prompt_version"),
            "gap_suggestions": result.get("gap_suggestions", []),
        }
        thread_id = thread_mgr.save(thread)
        st.success(f"Saved as thread `{thread_id}`")
