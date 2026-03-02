"""Artifact generation: evidence tables and synthesis memos from research threads.

Uses the Anthropic API to produce structured research artifacts, with
validation and caching for offline mode.
"""

import csv
import io
import json
import os
import re
from datetime import datetime, timezone
from typing import Optional

import anthropic

from src.artifacts.prompts import (
    EVIDENCE_TABLE_SYSTEM,
    EVIDENCE_TABLE_USER,
    SYNTHESIS_MEMO_SYSTEM,
    SYNTHESIS_MEMO_USER,
    format_chunks_for_prompt,
)
from src.cache.manager import CacheManager
from src.rag.generator import DEFAULT_MODEL


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_evidence_table(table: dict, available_chunks: list[dict]) -> dict:
    """Validate evidence table output.

    Returns: {"valid": bool, "issues": list[str], "row_count": int}
    """
    issues = []
    valid_ids = {(c.get("source_id"), c.get("chunk_id")) for c in available_chunks}

    rows = table.get("rows", [])
    if not rows:
        issues.append("No rows in evidence table")
    if len(rows) > 20:
        issues.append(f"Too many rows ({len(rows)}), expected 5-15")

    for i, row in enumerate(rows):
        for field in ["claim", "evidence", "source_id", "chunk_id", "confidence"]:
            if field not in row:
                issues.append(f"Row {i}: missing field '{field}'")

        pair = (row.get("source_id"), row.get("chunk_id"))
        is_gap_row = (
            row.get("confidence") == "low"
            and not row.get("source_id")
            and not row.get("chunk_id")
        )
        if not is_gap_row and pair not in valid_ids:
            issues.append(f"Row {i}: citation {pair} not in available chunks")

        if row.get("confidence") not in ("high", "medium", "low"):
            issues.append(f"Row {i}: invalid confidence '{row.get('confidence')}'")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "row_count": len(rows),
    }


def validate_synthesis_memo(memo: str, available_chunks: list[dict]) -> dict:
    """Validate synthesis memo output.

    Returns: {"valid": bool, "issues": list[str], "word_count": int,
              "citation_count": int, "invalid_citations": list}
    """
    issues = []
    valid_ids = {(c.get("source_id"), c.get("chunk_id")) for c in available_chunks}

    # Word count (exclude references section)
    body = memo.split("## References")[0] if "## References" in memo else memo
    word_count = len(body.split())
    if word_count < 700:
        issues.append(f"Too short: {word_count} words (target 800-1200)")
    elif word_count > 1400:
        issues.append(f"Too long: {word_count} words (target 800-1200)")

    # Citation extraction and validation
    citation_pattern = r"\((\w+),\s*(sec[\w._]+)\)"
    citations = re.findall(citation_pattern, memo)
    invalid = [(s, c) for s, c in citations if (s, c) not in valid_ids]
    if invalid:
        issues.append(f"Invalid citations: {invalid}")
    if len(citations) < 5:
        issues.append(f"Too few citations ({len(citations)}), expected 10-20")

    if "## References" not in memo:
        issues.append("Missing '## References' section")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "word_count": word_count,
        "citation_count": len(citations),
        "invalid_citations": invalid if invalid else [],
    }


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def export_evidence_table_csv(artifact: dict) -> str:
    """Convert evidence table rows to CSV string."""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["claim", "evidence", "source_id", "chunk_id", "confidence", "notes"],
        quoting=csv.QUOTE_ALL,
    )
    writer.writeheader()
    for row in artifact.get("rows", []):
        writer.writerow({
            "claim": row.get("claim", ""),
            "evidence": row.get("evidence", ""),
            "source_id": row.get("source_id", ""),
            "chunk_id": row.get("chunk_id", ""),
            "confidence": row.get("confidence", ""),
            "notes": row.get("notes", ""),
        })
    return output.getvalue()


def export_evidence_table_md(artifact: dict, query: str) -> str:
    """Convert evidence table to Markdown table with header."""
    lines = [
        f"# Evidence Table",
        f"",
        f"**Query:** {query}",
        f"**Generated:** {artifact.get('metadata', {}).get('generated_at', 'N/A')}",
        f"**Model:** {artifact.get('metadata', {}).get('model', 'N/A')}",
        f"",
        "| Claim | Evidence | Source | Chunk | Confidence | Notes |",
        "|-------|----------|--------|-------|------------|-------|",
    ]
    for row in artifact.get("rows", []):
        # Escape pipes in cell content
        claim = row.get("claim", "").replace("|", "\\|")
        evidence = row.get("evidence", "").replace("|", "\\|")
        notes = row.get("notes", "").replace("|", "\\|")
        lines.append(
            f"| {claim} | {evidence} | {row.get('source_id', '')} "
            f"| {row.get('chunk_id', '')} | {row.get('confidence', '')} | {notes} |"
        )
    return "\n".join(lines)


def export_synthesis_memo_md(artifact: dict, query: str) -> str:
    """Return memo content with metadata header."""
    header = (
        f"# Synthesis Memo\n\n"
        f"**Query:** {query}\n"
        f"**Generated:** {artifact.get('metadata', {}).get('generated_at', 'N/A')}\n"
        f"**Model:** {artifact.get('metadata', {}).get('model', 'N/A')}\n"
        f"**Word count:** {artifact.get('validation', {}).get('word_count', 'N/A')}\n\n"
        f"---\n\n"
    )
    return header + artifact.get("content", "")


def _sanitize_for_pdf(text: str) -> str:
    """Replace Unicode characters unsupported by built-in PDF fonts."""
    replacements = {
        "\u2014": "--",   # em dash
        "\u2013": "-",    # en dash
        "\u2018": "'",    # left single quote
        "\u2019": "'",    # right single quote
        "\u201c": '"',    # left double quote
        "\u201d": '"',    # right double quote
        "\u2026": "...",  # ellipsis
        "\u2022": "*",    # bullet
        "\u00a0": " ",    # non-breaking space
        "\u2212": "-",    # minus sign
        "\u00b1": "+/-",  # plus-minus
        "\u2264": "<=",   # less-than-or-equal
        "\u2265": ">=",   # greater-than-or-equal
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    return text


def export_synthesis_memo_pdf(artifact: dict, query: str) -> bytes:
    """Convert synthesis memo Markdown to PDF bytes using fpdf2."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Synthesis Memo", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Metadata
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    meta = artifact.get("metadata", {})
    pdf.cell(0, 5, _sanitize_for_pdf(f"Query: {query}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Generated: {meta.get('generated_at', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Model: {meta.get('model', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_text_color(0, 0, 0)

    # Body — parse Markdown line by line
    content = _sanitize_for_pdf(artifact.get("content", ""))
    w = pdf.epw  # effective page width (page width minus margins)
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## "):
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w, 8, stripped[3:])
            pdf.set_font("Helvetica", "", 11)
        elif stripped.startswith("# "):
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w, 8, stripped[2:])
            pdf.set_font("Helvetica", "", 11)
        elif stripped.startswith("- "):
            pdf.set_font("Helvetica", "", 9)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w, 4, stripped)
        elif stripped == "":
            pdf.ln(3)
        else:
            pdf.set_font("Helvetica", "", 11)
            # Strip bold markers for PDF
            clean = stripped.replace("**", "")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w, 5, clean)

    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# Artifact Generator
# ---------------------------------------------------------------------------

class ArtifactGenerator:
    """Generate and cache research artifacts from saved threads."""

    def __init__(self, cache: CacheManager):
        self.cache = cache
        self._client: Optional[anthropic.Anthropic] = None

    def _get_client(self) -> anthropic.Anthropic:
        """Lazy-init Anthropic client."""
        if self._client is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self._client = anthropic.Anthropic(api_key=api_key, timeout=120.0, max_retries=2)
        return self._client

    def _call_llm(self, system: str, user_prompt: str, max_tokens: int = 4096) -> Optional[str]:
        """Call Anthropic API with error handling.

        Returns raw text response or None on failure.
        """
        try:
            client = self._get_client()
            model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)

            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_prompt}],
            )

            text = ""
            for block in response.content:
                if block.type == "text":
                    text += block.text
            return text

        except (anthropic.APITimeoutError, anthropic.RateLimitError,
                anthropic.APIConnectionError, anthropic.APIStatusError, ValueError) as e:
            print(f"    [ArtifactGenerator] API error: {type(e).__name__}: {e}")
            return None

    def _get_chunks(self, thread: dict) -> list[dict]:
        """Get the best available chunks from a thread."""
        chunks = thread.get("reranked_chunks", [])
        if not chunks:
            chunks = thread.get("retrieved_chunks", [])[:10]
        return chunks

    def generate_evidence_table(self, thread: dict) -> Optional[dict]:
        """Generate evidence table from a saved research thread.

        Returns artifact dict or None if generation fails and no cache exists.
        """
        thread_id = thread.get("thread_id", "unknown")
        cache_key = CacheManager.make_artifact_key(thread_id, "evidence_table")

        # Check cache first
        cached = self.cache.get_artifact(cache_key)
        if cached:
            return cached

        # Need answer for evidence table (it extracts claims from the answer)
        answer = thread.get("answer")
        if not answer:
            return None

        chunks = self._get_chunks(thread)
        if not chunks:
            return None

        # Build prompt
        chunks_formatted = format_chunks_for_prompt(chunks)
        user_prompt = EVIDENCE_TABLE_USER.format(
            query=thread.get("query", ""),
            answer=answer,
            chunks_formatted=chunks_formatted,
        )

        # Call LLM
        raw = self._call_llm(EVIDENCE_TABLE_SYSTEM, user_prompt)
        if raw is None:
            return None

        # Parse JSON — strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```\w*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)

        try:
            table = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"    [ArtifactGenerator] JSON parse error: {e}")
            print(f"    [ArtifactGenerator] Raw response (first 200 chars): {cleaned[:200]}")
            return None

        # Validate
        validation = validate_evidence_table(table, chunks)

        # Build artifact
        model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
        artifact = {
            "type": "evidence_table",
            "rows": table.get("rows", []),
            "validation": validation,
            "metadata": {
                "thread_id": thread_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": model,
            },
        }

        # Cache
        self.cache.put_artifact(cache_key, artifact)

        return artifact

    def generate_synthesis_memo(self, thread: dict) -> Optional[dict]:
        """Generate synthesis memo from a saved research thread.

        The memo is synthesized from chunks only (NOT the answer),
        producing an independent analysis.

        Returns artifact dict or None if generation fails and no cache exists.
        """
        thread_id = thread.get("thread_id", "unknown")
        cache_key = CacheManager.make_artifact_key(thread_id, "synthesis_memo")

        # Check cache first
        cached = self.cache.get_artifact(cache_key)
        if cached:
            return cached

        chunks = self._get_chunks(thread)
        if not chunks:
            return None

        # Build prompt — memo gets chunks only, NOT the answer
        chunks_formatted = format_chunks_for_prompt(chunks)
        user_prompt = SYNTHESIS_MEMO_USER.format(
            query=thread.get("query", ""),
            chunks_formatted=chunks_formatted,
        )

        # Call LLM
        raw = self._call_llm(SYNTHESIS_MEMO_SYSTEM, user_prompt)
        if raw is None:
            return None

        # Validate
        validation = validate_synthesis_memo(raw, chunks)

        # Build artifact
        model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
        artifact = {
            "type": "synthesis_memo",
            "content": raw,
            "validation": validation,
            "metadata": {
                "thread_id": thread_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": model,
                "word_count": validation.get("word_count", 0),
            },
        }

        # Cache
        self.cache.put_artifact(cache_key, artifact)

        return artifact
