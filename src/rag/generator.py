"""
generator.py — Generate citation-backed answers using the Anthropic API.

Requires ANTHROPIC_API_KEY environment variable to be set.

Default model: claude-sonnet-4-5-20250929 (cost-effective for eval runs).
Override with --model flag or ANTHROPIC_MODEL env var.
"""

import os
from typing import Optional

import anthropic

from src.rag.prompts import get_system_prompt, build_prompt, get_prompt_version


# Default model — Sonnet is cost-effective for running 20+ eval queries.
# Override via CLI flag or ANTHROPIC_MODEL env var.
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def get_client() -> anthropic.Anthropic:
    """Create an Anthropic API client.

    Reads ANTHROPIC_API_KEY from environment.

    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Set it with: set ANTHROPIC_API_KEY=your-key-here (Windows) "
            "or export ANTHROPIC_API_KEY=your-key-here (Linux/Mac)"
        )
    return anthropic.Anthropic(api_key=api_key)


def generate(
    query: str,
    chunks: list[dict],
    model: Optional[str] = None,
    max_tokens: int = 2048,
) -> dict:
    """Generate a citation-backed answer from retrieved chunks.

    Args:
        query: The user's research question.
        chunks: Ranked list of chunk dicts from retriever/reranker.
        model: Anthropic model name. Defaults to DEFAULT_MODEL.
        max_tokens: Maximum tokens in the response.

    Returns:
        Dict with keys:
            answer: The generated text.
            model: Model name used.
            prompt_version: Version string for logging.
            usage: Dict with input_tokens and output_tokens.
    """
    client = get_client()
    model = model or os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)

    system_prompt = get_system_prompt()
    messages = build_prompt(query, chunks)

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    )

    # Extract text from response
    answer = ""
    for block in response.content:
        if block.type == "text":
            answer += block.text

    return {
        "answer": answer,
        "model": model,
        "prompt_version": get_prompt_version(),
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }
