"""
section_parser.py
-----------------
Splits the scraped paper text into logical sections:
  abstract, methodology, results, conclusion.

Strategy:
  1. Keyword-based heading detection (fast, no LLM cost).
  2. If a section is missing, the caller can optionally use the LLM fallback.
"""

import re
from typing import Optional

# ── Keyword map ────────────────────────────────────────────────────────────────
SECTION_MAP = {
    "abstract": ["abstract"],
    "introduction": ["introduction", "background", "overview"],
    "methodology": [
        "method", "methods", "methodology", "approach", "proposed",
        "framework", "architecture", "model", "system design",
        "experimental setup", "implementation",
    ],
    "results": [
        "result", "results", "experiment", "experiments",
        "evaluation", "performance", "analysis", "findings",
        "benchmark", "comparison",
    ],
    "conclusion": [
        "conclusion", "conclusions", "summary", "future work",
        "discussion", "closing remarks",
    ],
}


def _normalize(text: str) -> str:
    return text.lower().strip()


def _detect_section(heading: str) -> Optional[str]:
    """Return the canonical section name for a heading, or None."""
    h = _normalize(heading)
    for section, keywords in SECTION_MAP.items():
        for kw in keywords:
            if kw in h:
                return section
    return None


def parse_sections(full_text: str) -> dict:
    """
    Parse `full_text` into a dict of sections.

    Returns:
        {
            "abstract":     str,
            "introduction": str,
            "methodology":  str,
            "results":      str,
            "conclusion":   str,
            "other":        str,   # anything not matched
        }
    """
    sections = {
        "abstract": "",
        "introduction": "",
        "methodology": "",
        "results": "",
        "conclusion": "",
        "other": "",
    }

    # Split on lines that look like headings:
    # e.g. "1. Introduction", "## Methods", "RESULTS", "Conclusion"
    heading_pattern = re.compile(
        r"^(?:\d+[\.\)]\s*)?([A-Z][A-Za-z &\-]{2,60})$",
        re.MULTILINE,
    )

    lines = full_text.split("\n")
    current_section = "other"
    buffer: list[str] = []

    def flush():
        nonlocal buffer
        text = "\n".join(buffer).strip()
        if text:
            if sections[current_section]:
                sections[current_section] += "\n\n" + text
            else:
                sections[current_section] = text
        buffer = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            buffer.append("")
            continue

        # Check if this line is a heading
        if heading_pattern.match(stripped):
            detected = _detect_section(stripped)
            if detected:
                flush()
                current_section = detected
                continue  # don't add the heading itself to content

        buffer.append(line)

    flush()  # flush last section

    # ── Heuristic: if abstract is empty, grab first 800 chars ──────────────
    if not sections["abstract"] and full_text:
        sections["abstract"] = full_text[:800].strip()

    _log_sections(sections)
    return sections


def _log_sections(sections: dict):
    print("[SectionParser] Section lengths:")
    for k, v in sections.items():
        print(f"  {k:15s}: {len(v):>6} chars")
