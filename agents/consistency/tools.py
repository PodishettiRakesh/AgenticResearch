"""
Consistency agent tools.
"""

from typing import List
from crewai.tools import BaseTool
from pydantic import Field
from utils.llm_hybrid import get_llm
from agents.prompts.consistency import (
    CONSISTENCY_SYSTEM,
    CONSISTENCY_CHUNK_PROMPT,
    CONSISTENCY_REDUCE_PROMPT
)


class ConsistencyAnalysisTool(BaseTool):
    """Tool for consistency analysis using Map-Reduce pattern."""
    
    name: str = "consistency_analysis"
    description: str = "Analyze logical consistency between methodology and results"
    
    def _run(self, methodology_chunks: List[str], results_chunks: List[str]) -> str:
        """Execute consistency analysis on methodology and results chunks."""
        llm = get_llm()
        
        # Combine methodology and results chunks, limit to 6 total
        all_chunks = (methodology_chunks + results_chunks)[:6]
        
        if not all_chunks:
            return "No content available for consistency analysis."
        
        # MAP phase
        chunk_analyses = []
        for i, chunk in enumerate(all_chunks):
            prompt = CONSISTENCY_CHUNK_PROMPT.format(chunk=chunk)
            messages = [
                {"role": "system", "content": CONSISTENCY_SYSTEM},
                {"role": "user", "content": prompt},
            ]
            response = llm.invoke(messages)
            analysis = response.content if hasattr(response, "content") else str(response)
            chunk_analyses.append(f"--- Chunk {i+1} ---\n{analysis}")
        
        # REDUCE phase
        combined = "\n\n".join(chunk_analyses)
        reduce_prompt = CONSISTENCY_REDUCE_PROMPT.format(analyses=combined)
        messages = [
            {"role": "system", "content": CONSISTENCY_SYSTEM},
            {"role": "user", "content": reduce_prompt},
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
