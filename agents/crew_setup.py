"""
crew_setup.py
-------------
Defines the four CrewAI Agents and their Tasks, then runs the crew sequentially.

Agents:
  1. Consistency Agent  – Map-Reduce over methodology + results chunks
  2. Grammar Agent      – Evaluates abstract + introduction
  3. Novelty Agent      – Evaluates abstract + conclusion
  4. Fact-Check Agent   – Map-Reduce over all section chunks

The crew runs sequentially (process=Process.sequential) so each agent's
output is available to the next one.
"""

import re
from crewai import Agent, Task, Crew, Process

from utils.llm import get_llm
from agents.prompts import (
    CONSISTENCY_SYSTEM, CONSISTENCY_CHUNK_PROMPT, CONSISTENCY_REDUCE_PROMPT,
    GRAMMAR_SYSTEM, GRAMMAR_PROMPT,
    NOVELTY_SYSTEM, NOVELTY_PROMPT,
    FACTCHECK_SYSTEM, FACTCHECK_CHUNK_PROMPT, FACTCHECK_REDUCE_PROMPT,
    FABRICATION_PROMPT,
)


# ── Helper: Map-Reduce over chunks ────────────────────────────────────────────

def _map_reduce(llm, system_prompt: str, chunk_prompt_tpl: str,
                reduce_prompt_tpl: str, chunks: list[str]) -> str:
    """
    Run a map step (one LLM call per chunk) then a reduce step (one final call).
    Falls back gracefully if chunks list is empty.
    """
    if not chunks:
        return "No content available for analysis."

    # MAP
    chunk_analyses = []
    for i, chunk in enumerate(chunks):
        prompt = chunk_prompt_tpl.format(chunk=chunk)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt},
        ]
        response = llm.invoke(messages)
        analysis = response.content if hasattr(response, "content") else str(response)
        chunk_analyses.append(f"--- Chunk {i+1} ---\n{analysis}")
        print(f"  [Map] Chunk {i+1}/{len(chunks)} processed.")

    # REDUCE
    combined = "\n\n".join(chunk_analyses)
    reduce_prompt = reduce_prompt_tpl.format(analyses=combined)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": reduce_prompt},
    ]
    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)


def _single_call(llm, system_prompt: str, user_prompt: str) -> str:
    """Single LLM call (no chunking needed)."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]
    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_agents(sections: dict, chunked: dict) -> dict:
    """
    Run all four agents and return a results dict.

    Args:
        sections: {section_name: full_text}
        chunked:  {section_name: [chunk1, chunk2, ...]}

    Returns:
        {
            "consistency": str,
            "grammar":     str,
            "novelty":     str,
            "fact_check":  str,
            "fabrication": str,
        }
    """
    llm = get_llm()

    results = {}

    # ── 1. Consistency Agent (Map-Reduce on methodology + results) ────────
    print("\n[Agent 1/4] Consistency Agent running...")
    consistency_chunks = (
        chunked.get("methodology", []) + chunked.get("results", [])
    )
    # Limit to avoid rate limits: max 6 chunks
    consistency_chunks = consistency_chunks[:6]
    results["consistency"] = _map_reduce(
        llm,
        CONSISTENCY_SYSTEM,
        CONSISTENCY_CHUNK_PROMPT,
        CONSISTENCY_REDUCE_PROMPT,
        consistency_chunks,
    )
    print("[Agent 1/4] Consistency analysis complete.")

    # ── 2. Grammar Agent (abstract + introduction, single call) ───────────
    print("\n[Agent 2/4] Grammar Agent running...")
    grammar_text = (
        sections.get("abstract", "") + "\n\n" + sections.get("introduction", "")
    )[:4000]  # cap at ~1000 tokens
    grammar_prompt = GRAMMAR_PROMPT.format(text=grammar_text)
    results["grammar"] = _single_call(llm, GRAMMAR_SYSTEM, grammar_prompt)
    print("[Agent 2/4] Grammar analysis complete.")

    # ── 3. Novelty Agent (abstract + conclusion, single call) ─────────────
    print("\n[Agent 3/4] Novelty Agent running...")
    novelty_prompt = NOVELTY_PROMPT.format(
        abstract=sections.get("abstract", "Not available")[:2000],
        conclusion=sections.get("conclusion", "Not available")[:2000],
    )
    results["novelty"] = _single_call(llm, NOVELTY_SYSTEM, novelty_prompt)
    print("[Agent 3/4] Novelty analysis complete.")

    # ── 4. Fact-Check Agent (Map-Reduce on all sections) ──────────────────
    print("\n[Agent 4/4] Fact-Check Agent running...")
    all_chunks = []
    for sec in ["abstract", "methodology", "results", "conclusion"]:
        all_chunks.extend(chunked.get(sec, []))
    all_chunks = all_chunks[:6]  # max 6 chunks
    results["fact_check"] = _map_reduce(
        llm,
        FACTCHECK_SYSTEM,
        FACTCHECK_CHUNK_PROMPT,
        FACTCHECK_REDUCE_PROMPT,
        all_chunks,
    )
    print("[Agent 4/4] ✅ Fact-check complete.")

    # ── 5. Fabrication / Aggregation (single call) ────────────────────────
    print("\n[Aggregator] 📊 Calculating Fabrication Probability...")
    consistency_score = _extract_consistency_score(results["consistency"])
    grammar_rating    = _extract_grammar_rating(results["grammar"])
    novelty_index     = _extract_novelty_index(results["novelty"])
    factcheck_summary = _extract_factcheck_summary(results["fact_check"])

    fab_prompt = FABRICATION_PROMPT.format(
        consistency_score=consistency_score,
        grammar_rating=grammar_rating,
        novelty_index=novelty_index,
        factcheck_summary=factcheck_summary,
    )
    results["fabrication"] = _single_call(llm, "", fab_prompt)
    print("[Aggregator] ✅ Fabrication score calculated.")

    return results


# ── Extraction helpers ────────────────────────────────────────────────────────

def _extract_consistency_score(text: str) -> int:
    """Pull the integer score from the consistency agent output."""
    match = re.search(r"OVERALL CONSISTENCY SCORE[:\s]+(\d{1,3})", text, re.IGNORECASE)
    if match:
        return min(int(match.group(1)), 100)
    # Fallback: look for any standalone number 0-100
    match = re.search(r"\b([0-9]{1,3})\b", text)
    return int(match.group(1)) if match else 70


def _extract_grammar_rating(text: str) -> str:
    """Pull High/Medium/Low from grammar agent output."""
    match = re.search(r"GRAMMAR RATING[:\s]+(High|Medium|Low)", text, re.IGNORECASE)
    return match.group(1).capitalize() if match else "Medium"


def _extract_novelty_index(text: str) -> str:
    """Pull the novelty label from novelty agent output."""
    match = re.search(
        r"NOVELTY INDEX[:\s]+(Highly Novel|Moderately Novel|Incremental|Low Novelty)",
        text, re.IGNORECASE,
    )
    return match.group(1) if match else "Moderately Novel"


def _extract_factcheck_summary(text: str) -> str:
    """Pull the fact-check summary paragraph."""
    match = re.search(
        r"FACT-CHECK SUMMARY[:\s]+(.*?)(?:\n\n|\Z)", text, re.IGNORECASE | re.DOTALL
    )
    return match.group(1).strip() if match else text[:500]
