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
    Enhanced to handle arXiv HTML continuous text format.

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

    # Enhanced patterns for arXiv HTML content
    # Look for section boundaries in continuous text
    section_patterns = {
        "abstract": [
            r"(?i)abstract[:\s]+(.*?)(?=\s*(?:1\s+\.?\s*[Ii]ntroduction|[Ii]ntroduction|1\s+\.?\s*[Rr]elated|[Rr]elated|2\s+\.?\s*[Bb]ackground|[Bb]ackground))",
            r"(?i)abstract[:\s]+(.*?)(?=\s*\d+\s+)",
        ],
        "introduction": [
            r"(?i)(?:1\s+\.?\s*)?[Ii]ntroduction[:\s]+(.*?)(?=\s*(?:2\s+\.?\s*[Rr]elated|[Rr]elated|[Rr]elated\s+[Ww]ork|3\s+\.?\s*[Bb]ackground|[Bb]ackground|[Mm]ethod|[Mm]ethodology))",
            r"(?i)(?:1\s+\.?\s*)?[Ii]ntroduction[:\s]+(.*?)(?=\s*\d+\s+)",
        ],
        "methodology": [
            r"(?i)(?:\d+\s+\.?\s*)?[Mm]ethod(?:s|ology)?[:\s]+(.*?)(?=\s*(?:\d+\s+\.?\s*[Ee]xperiment|[Ee]xperiment|[Rr]esult|[Rr]esults|4\s+\.?\s*[Ee]xperiment|[Ee]xperiments))",
            r"(?i)(?:\d+\s+\.?\s*)?[Bb]ackground[:\s]+(.*?)(?=\s*(?:\d+\s+\.?\s*[Mm]ethod|[Mm]ethod|[Ee]xperiment|[Rr]esult))",
        ],
        "results": [
            r"(?i)(?:\d+\s+\.?\s*)?[Rr]esult[s]?[:\s]+(.*?)(?=\s*(?:\d+\s+\.?\s*[Dd]iscussion|[Dd]iscussion|[Cc]onclusion|5\s+\.?\s*[Cc]onclusion|[Cc]onclusions|[Aa]nalysis))",
            r"(?i)(?:\d+\s+\.?\s*)?[Ee]xperiment[s]?[:\s]+(.*?)(?=\s*(?:\d+\s+\.?\s*[Dd]iscussion|[Dd]iscussion|[Cc]onclusion|[Aa]nalysis))",
        ],
        "conclusion": [
            r"(?i)(?:\d+\s+\.?\s*)?[Cc]onclusion[s]?[:\s]+(.*?)(?=\s*(?:\d+\s+\.?\s*[Rr]eferences|[Rr]eferences|[Aa]ppendix))",
            r"(?i)(?:\d+\s+\.?\s*)?[Dd]iscussion[:\s]+(.*?)(?=\s*(?:\d+\s+\.?\s*[Rr]eferences|[Rr]eferences))",
        ]
    }

    # Try to extract sections using patterns
    for section_name, patterns in section_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, full_text, re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()
                break

    # If no sections found, try fallback approach
    if not any(sections[s] for s in ["introduction", "methodology", "results", "conclusion"]):
        # Fallback: split on numbered sections
        numbered_sections = re.split(r'\n(?=\d+\s+)', full_text)
        current_section = "other"
        
        for section_text in numbered_sections:
            section_text = section_text.strip()
            if not section_text:
                continue
                
            # Detect section type from content
            detected = _detect_section_from_content(section_text)
            if detected:
                current_section = detected
            
            if sections[current_section]:
                sections[current_section] += "\n\n" + section_text
            else:
                sections[current_section] = section_text

    # Heuristic: if abstract is empty, grab first 800 chars
    if not sections["abstract"] and full_text:
        # Look for "Abstract" keyword first
        abstract_match = re.search(r'(?i)abstract[:\s]+(.*?)(?=\s*(?:1\s+\.?\s*[Ii]ntroduction|[Ii]ntroduction|\d+\s+))', full_text, re.DOTALL)
        if abstract_match:
            sections["abstract"] = abstract_match.group(1).strip()[:800]
        else:
            sections["abstract"] = full_text[:800].strip()

    _log_sections(sections)
    # print(f"sections from parse_sections: {sections}")
    return sections


def _detect_section_from_content(text: str) -> str:
    """Detect section type from content keywords."""
    text_lower = text.lower()
    
    # Check for section indicators in first 200 chars
    sample = text_lower[:200]
    
    if "abstract" in sample:
        return "abstract"
    elif any(kw in sample for kw in ["introduction", "background", "overview"]):
        return "introduction"
    elif any(kw in sample for kw in ["method", "methodology", "approach", "framework", "architecture"]):
        return "methodology"
    elif any(kw in sample for kw in ["result", "experiment", "evaluation", "performance", "analysis"]):
        return "results"
    elif any(kw in sample for kw in ["conclusion", "discussion", "summary", "future work"]):
        return "conclusion"
    
    return "other"


def _log_sections(sections: dict):
    print("[SectionParser] Section lengths:")
    for k, v in sections.items():
        print(f"  {k:15s}: {len(v):>6} chars")
