"""
prompts.py — Citation-enforcing prompt templates for RAG generation.

These prompts ensure the LLM:
  - Grounds every claim in retrieved evidence
  - Uses (source_id, chunk_id) citation format
  - Refuses to invent citations
  - Flags missing or conflicting evidence
"""

SYSTEM_PROMPT = """\
You are a research assistant for a domain expert studying ML failure modes \
in space debris tracking and collision avoidance. Your role is to answer \
questions using ONLY the provided evidence chunks.

RULES:
1. Every factual claim MUST include an inline citation in the format \
(source_id, chunk_id), e.g. (acciarini2021, sec2.1_p3).
2. Only cite chunks that are provided in the EVIDENCE section below. \
Do NOT invent or fabricate citations.
3. If the evidence is insufficient to answer the question, say so explicitly. \
State what information is missing and what sources might help.
4. If evidence from different sources conflicts, note the disagreement and \
cite both sides.
5. Do not speculate beyond what the evidence supports.
6. End your response with a REFERENCES section listing each cited source \
once, formatted as: source_id — Title (Year).\
"""

PROMPT_VERSION = "v1.0"


def build_prompt(query: str, chunks: list[dict]) -> list[dict]:
    """Build the messages list for the Anthropic API.

    Args:
        query: The user's research question.
        chunks: List of chunk dicts (must have source_id, chunk_id, text,
                section_title, year, authors).

    Returns:
        List of message dicts for the Anthropic messages API:
        [{"role": "user", "content": "..."}]
        (system prompt is passed separately)
    """
    # Format evidence chunks
    evidence_parts = []
    for i, chunk in enumerate(chunks, 1):
        evidence_parts.append(
            f"[{i}] ({chunk['source_id']}, {chunk['chunk_id']}) "
            f"| Section: {chunk.get('section_title', 'N/A')} "
            f"| Year: {chunk.get('year', 'N/A')} "
            f"| Authors: {chunk.get('authors', 'N/A')}\n"
            f"{chunk['text']}"
        )

    evidence_block = "\n\n".join(evidence_parts)

    user_content = f"""\
EVIDENCE:
{evidence_block}

QUESTION:
{query}

Answer the question using the evidence above. Cite every claim using \
(source_id, chunk_id) format. If the evidence is insufficient, say so.\
"""

    return [{"role": "user", "content": user_content}]


def get_system_prompt() -> str:
    """Return the system prompt string."""
    return SYSTEM_PROMPT


def get_prompt_version() -> str:
    """Return the current prompt version for logging."""
    return PROMPT_VERSION
