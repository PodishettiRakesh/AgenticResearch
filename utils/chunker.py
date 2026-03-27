"""
chunker.py
----------
Splits long text into overlapping chunks to stay within the 16k token limit.

Rule of thumb: 1 token ≈ 4 characters (English text).
Default chunk_size=4800 chars ≈ 1200 tokens — safe for a single LLM call
that also carries a system prompt + instructions (~800 tokens overhead).
"""

from typing import Optional


# ── Constants ──────────────────────────────────────────────────────────────────
DEFAULT_CHUNK_SIZE = 4800   # characters per chunk  (~1 200 tokens)
DEFAULT_OVERLAP    = 400    # overlap between chunks (~100 tokens)
MAX_ABSTRACT_CHARS = 3000   # abstracts are kept whole up to this limit


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:
    """
    Split `text` into overlapping chunks.

    Args:
        text:       The input string to chunk.
        chunk_size: Maximum characters per chunk.
        overlap:    Number of characters shared between consecutive chunks.

    Returns:
        A list of string chunks.
    """
    if not text:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


def chunk_sections(sections: dict, skip_abstract: bool = True) -> dict:
    """
    Apply chunking to each section in the sections dict.

    Args:
        sections:      Dict of {section_name: text}.
        skip_abstract: If True, keep the abstract as a single chunk
                       (it's usually short enough).

    Returns:
        Dict of {section_name: list[str]}
    """
    chunked: dict[str, list[str]] = {}

    for section, text in sections.items():
        if not text:
            chunked[section] = []
            continue

        if skip_abstract and section == "abstract":
            # Keep abstract whole; truncate only if extremely long
            chunked[section] = [text[:MAX_ABSTRACT_CHARS]]
        else:
            chunked[section] = chunk_text(text)

    _log_chunks(chunked)
    return chunked


def _log_chunks(chunked: dict):
    print("[Chunker] Chunk counts per section:")
    for section, chunks in chunked.items():
        total_chars = sum(len(c) for c in chunks)
        print(f"  {section:15s}: {len(chunks):>3} chunk(s), {total_chars:>7} chars total")
