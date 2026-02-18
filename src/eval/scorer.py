"""
scorer.py — LLM-as-Judge scoring for RAG evaluation.

Scores each RAG response on two dimensions:
  - Groundedness (1–4): Is the answer supported by the retrieved chunks?
  - Citation Correctness (1–4): Do citations resolve to real chunks that support the claims?

Uses a separate Anthropic API call with a structured scoring prompt.
The judge model can differ from the generation model (e.g., use Sonnet for both,
or use a different model for judging).

Scoring rubric (1–4):
  4: Fully grounded/correct; citations accurate; uncertainty stated when evidence is weak
  3: Mostly correct; minor missing nuance or minor citation issues
  2: Partially correct; key omissions, weak grounding, or vague citations
  1: Not usable; hallucinated claims, fabricated citations, or structural failure
"""

import json
import os
import re
from typing import Optional

import anthropic
from pathlib import Path
from dotenv import load_dotenv

_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env", override=True)
load_dotenv(_project_root / "grader.env", override=True)

# ---------------------------------------------------------------------------
# Scoring prompt template
# ---------------------------------------------------------------------------

SCORING_PROMPT = """You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system
focused on ML failure modes in space debris tracking and collision avoidance.

You will be given:
1. A user QUERY
2. The RETRIEVED CHUNKS that were provided as context to the RAG system
3. The RAG system's ANSWER (which should cite chunks using (source_id, chunk_id) format)

Score the answer on two dimensions using the rubric below.

## Groundedness (1–4)
How well is the answer supported by the retrieved chunks?
- 4: Every claim is directly supported by retrieved chunk content. Uncertainty is stated when evidence is weak or absent.
- 3: Most claims are supported. Minor unsupported nuance or slight extrapolation beyond chunk content.
- 2: Some claims are supported, but key claims lack grounding or are extrapolated significantly.
- 1: Major claims are hallucinated or contradicted by the retrieved chunks.

## Citation Correctness (1–4)
Do the citations accurately point to chunks that support the associated claims?
- 4: All citations use correct (source_id, chunk_id) format AND each cited chunk actually supports the claim it's attached to.
- 3: Most citations are correct. Minor issues: a citation is slightly off-target, or one claim is missing a citation.
- 2: Multiple citation errors: wrong chunk_ids, citations that don't support their claims, or many uncited claims.
- 1: Citations are fabricated, use wrong format, or systematically fail to match claim content.

## Special cases
- If the answer correctly states that evidence is insufficient or not found in the corpus, and the retrieved chunks genuinely lack relevant content, score Groundedness as 4 (this is correct trust behavior).
- If the answer refuses to answer when evidence IS present in the chunks, score Groundedness as 1.

Respond with ONLY a JSON object in this exact format (no markdown, no backticks):
{{
  "groundedness_score": <1-4>,
  "groundedness_rationale": "<1-2 sentence explanation>",
  "citation_score": <1-4>,
  "citation_rationale": "<1-2 sentence explanation>",
  "failure_tags": ["<tag1>", "<tag2>"]
}}

Valid failure tags (use any that apply, or empty list if none):
- HALLUCINATED_CLAIM: answer contains claims not in the retrieved chunks
- FABRICATED_CITATION: citation points to a chunk that doesn't exist or doesn't support the claim
- MISSING_CITATION: a significant claim lacks any citation
- WRONG_FORMAT: citations don't use (source_id, chunk_id) format
- MISSED_EVIDENCE: retrieved chunks contain relevant info the answer ignores
- FALSE_REFUSAL: answer says evidence is missing when it's present in chunks
- OVER_EXTRAPOLATION: answer goes significantly beyond what chunks support
- CONTRADICTS_SOURCE: answer contradicts information in the retrieved chunks

---

QUERY:
{query}

RETRIEVED CHUNKS:
{chunks}

ANSWER:
{answer}
"""


def format_chunks_for_scoring(chunks: list[dict]) -> str:
    """Format retrieved chunks into a readable string for the judge prompt.
    
    Args:
        chunks: List of chunk dicts. Expected keys: source_id, chunk_id, text.
                May also have: section_title, distance/score.
    
    Returns:
        Formatted string with one chunk per block.
    """
    parts = []
    for i, chunk in enumerate(chunks, 1):
        sid = chunk.get("source_id", "unknown")
        cid = chunk.get("chunk_id", "unknown")
        text = chunk.get("text", chunk.get("document", ""))
        section = chunk.get("section_title", "")
        
        header = f"[Chunk {i}] ({sid}, {cid})"
        if section:
            header += f" — {section}"
        
        parts.append(f"{header}\n{text}")
    
    return "\n\n".join(parts)


def score_response(
    query: str,
    answer: str,
    chunks: list[dict],
    model: str = "claude-opus-4-6",
) -> dict:
    """Score a single RAG response using LLM-as-judge.
    
    Args:
        query: The original user query.
        answer: The RAG pipeline's generated answer.
        chunks: The retrieved (and possibly reranked) chunks provided to the generator.
        model: Anthropic model to use for judging.
    
    Returns:
        Dict with keys: groundedness_score, groundedness_rationale,
        citation_score, citation_rationale, failure_tags, judge_model.
    """
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    
    formatted_chunks = format_chunks_for_scoring(chunks)
    
    prompt = SCORING_PROMPT.format(
        query=query,
        chunks=formatted_chunks,
        answer=answer,
    )
    
    response = client.messages.create(
        model=model,
        max_tokens=500,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )
    
    raw_text = response.content[0].text.strip()
    
    # Parse the JSON response
    try:
        # Strip any accidental markdown fences
        cleaned = re.sub(r"^```json\s*", "", raw_text)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        # If parsing fails, return a default with the raw text for debugging
        result = {
            "groundedness_score": 0,
            "groundedness_rationale": f"PARSE_ERROR: {raw_text[:200]}",
            "citation_score": 0,
            "citation_rationale": "PARSE_ERROR",
            "failure_tags": ["JUDGE_PARSE_ERROR"],
        }
    
    result["judge_model"] = model
    result["judge_input_tokens"] = response.usage.input_tokens
    result["judge_output_tokens"] = response.usage.output_tokens
    
    return result
