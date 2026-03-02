"""Research Threads page — browse, load, and manage saved research threads."""

import os
import sys

import streamlit as st
import pandas as pd

# Ensure project root is on the path.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.threads.manager import ThreadManager
from src.cache.manager import CacheManager
from src.artifacts.generator import (
    ArtifactGenerator,
    export_evidence_table_csv,
    export_evidence_table_md,
    export_synthesis_memo_md,
    export_synthesis_memo_pdf,
)
from src.app.components.citation_card import render_citation_cards, highlight_citations_in_answer
from src.app.components.styles import inject_button_css

st.set_page_config(page_title="Threads", page_icon="\U0001F4C2", layout="wide")
inject_button_css()
st.title("Research Threads")

thread_mgr = ThreadManager()
cache_mgr = CacheManager()
artifact_gen = ArtifactGenerator(cache_mgr)

threads = thread_mgr.list_threads()

if not threads:
    st.info("No saved threads yet. Ask a question on the Ask Questions page and save it as a thread.")
else:
    # Thread selector
    thread_options = {
        t["thread_id"]: f"{t['query'][:80]}{'...' if len(t['query']) > 80 else ''} ({t['created_at'][:10]})"
        for t in threads
    }

    selected_id = st.selectbox(
        "Select a thread",
        options=list(thread_options.keys()),
        format_func=lambda tid: thread_options[tid],
    )

    if selected_id:
        thread = thread_mgr.load(selected_id)

        if thread is None:
            st.error(f"Thread {selected_id} not found.")
        else:
            # Thread header
            st.caption(f"Thread ID: {thread['thread_id']} | Created: {thread.get('created_at', 'N/A')}")

            # Query
            st.markdown("### Query")
            st.markdown(f"> {thread['query']}")

            # Filters used
            filters = thread.get("where_filters")
            if filters:
                st.caption(f"Filters: {filters}")

            # Answer
            st.markdown("### Answer")
            answer = thread.get("answer")
            reranked = thread.get("reranked_chunks", [])

            if answer:
                highlighted = highlight_citations_in_answer(answer, reranked)
                st.markdown(highlighted)
            else:
                st.info("No generated answer (offline mode — evidence only).")

            # Citation cards
            if reranked:
                st.markdown("### Sources")
                render_citation_cards(reranked)
            elif thread.get("retrieved_chunks"):
                st.markdown("### Sources")
                render_citation_cards(thread["retrieved_chunks"][:10])

            # Gap suggestions
            gap_suggestions = thread.get("gap_suggestions", [])
            if gap_suggestions:
                with st.expander("Evidence Gaps", expanded=False):
                    for i, gap in enumerate(gap_suggestions):
                        st.markdown(f"**{gap['gap']}**")
                        if st.button(
                            f"Search: {gap['suggested_query'][:60]}",
                            key=f"thread_gap_{i}",
                        ):
                            st.session_state["prefill_query"] = gap["suggested_query"]
                            st.switch_page("Ask_Questions.py")

            # Model info
            model = thread.get("model")
            if model:
                st.caption(
                    f"Model: {model} | "
                    f"Prompt: {thread.get('prompt_version', 'N/A')}"
                )

            # ----------------------------------------------------------
            # Artifacts
            # ----------------------------------------------------------
            st.markdown("### Artifacts")
            artifacts = thread.get("artifacts", {})

            # Generate buttons
            gen_col1, gen_col2 = st.columns(2)
            with gen_col1:
                has_answer = bool(thread.get("answer"))
                et_btn = st.button(
                    "Generate Evidence Table",
                    disabled=not has_answer,
                    help="Requires a generated answer" if not has_answer else None,
                )
            with gen_col2:
                sm_btn = st.button("Generate Synthesis Memo")

            # Evidence table generation
            if et_btn:
                with st.spinner("Generating evidence table..."):
                    et_artifact = artifact_gen.generate_evidence_table(thread)
                if et_artifact:
                    artifacts["evidence_table"] = {
                        "generated_at": et_artifact["metadata"]["generated_at"],
                        "model": et_artifact["metadata"]["model"],
                    }
                    thread["artifacts"] = artifacts
                    thread_mgr.save(thread)
                    st.rerun()
                else:
                    st.error("Failed to generate evidence table. Check API key or try again.")

            # Synthesis memo generation
            if sm_btn:
                with st.spinner("Generating synthesis memo..."):
                    sm_artifact = artifact_gen.generate_synthesis_memo(thread)
                if sm_artifact:
                    artifacts["synthesis_memo"] = {
                        "generated_at": sm_artifact["metadata"]["generated_at"],
                        "model": sm_artifact["metadata"]["model"],
                    }
                    thread["artifacts"] = artifacts
                    thread_mgr.save(thread)
                    st.rerun()
                else:
                    st.error("Failed to generate synthesis memo. Check API key or try again.")

            # Display existing evidence table
            et_cache_key = CacheManager.make_artifact_key(thread["thread_id"], "evidence_table")
            et_cached = cache_mgr.get_artifact(et_cache_key)
            if et_cached:
                st.markdown("#### Evidence Table")
                et_meta = et_cached.get("metadata", {})
                st.caption(
                    f"Generated: {et_meta.get('generated_at', 'N/A')} | "
                    f"Model: {et_meta.get('model', 'N/A')}"
                )

                # Validation warnings
                et_validation = et_cached.get("validation", {})
                if et_validation and not et_validation.get("valid", True):
                    st.warning(
                        "Validation issues: " + "; ".join(et_validation.get("issues", []))
                    )

                # Display as dataframe
                rows = et_cached.get("rows", [])
                if rows:
                    df = pd.DataFrame(rows)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                # Export buttons
                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    st.download_button(
                        label="Download CSV",
                        data=export_evidence_table_csv(et_cached),
                        file_name=f"evidence_table_{thread['thread_id']}.csv",
                        mime="text/csv",
                    )
                with exp_col2:
                    st.download_button(
                        label="Download Markdown",
                        data=export_evidence_table_md(et_cached, thread["query"]),
                        file_name=f"evidence_table_{thread['thread_id']}.md",
                        mime="text/markdown",
                    )

            # Display existing synthesis memo
            sm_cache_key = CacheManager.make_artifact_key(thread["thread_id"], "synthesis_memo")
            sm_cached = cache_mgr.get_artifact(sm_cache_key)
            if sm_cached:
                st.markdown("#### Synthesis Memo")
                sm_meta = sm_cached.get("metadata", {})
                st.caption(
                    f"Generated: {sm_meta.get('generated_at', 'N/A')} | "
                    f"Model: {sm_meta.get('model', 'N/A')} | "
                    f"Words: {sm_meta.get('word_count', 'N/A')}"
                )

                # Validation warnings
                sm_validation = sm_cached.get("validation", {})
                if sm_validation and not sm_validation.get("valid", True):
                    st.warning(
                        "Validation issues: " + "; ".join(sm_validation.get("issues", []))
                    )

                # Display memo
                st.markdown(sm_cached.get("content", ""))

                # Export buttons
                exp_col3, exp_col4 = st.columns(2)
                with exp_col3:
                    st.download_button(
                        label="Download Markdown",
                        data=export_synthesis_memo_md(sm_cached, thread["query"]),
                        file_name=f"synthesis_memo_{thread['thread_id']}.md",
                        mime="text/markdown",
                    )
                with exp_col4:
                    pdf_bytes = export_synthesis_memo_pdf(sm_cached, thread["query"])
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=f"synthesis_memo_{thread['thread_id']}.pdf",
                        mime="application/pdf",
                    )

            if not et_cached and not sm_cached and not artifacts:
                st.info("No artifacts generated yet. Use the buttons above to generate.")

            # Delete button
            st.divider()
            if st.button("Delete this thread", type="secondary"):
                thread_mgr.delete(selected_id)
                st.success(f"Thread {selected_id} deleted.")
                st.rerun()
