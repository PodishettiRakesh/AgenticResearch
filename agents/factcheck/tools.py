"""
Fact-check agent tools.
"""

from typing import List
from crewai.tools import BaseTool
from pydantic import Field
from utils.llm_hybrid import get_llm
from agents.prompts.factcheck import (
    FACTCHECK_SYSTEM,
    FACTCHECK_CHUNK_PROMPT,
    FACTCHECK_REDUCE_PROMPT
)


class FactCheckAnalysisTool(BaseTool):
    """Tool for fact-checking using Map-Reduce pattern."""
    
    name: str = "fact_check_analysis"
    description: str = "Verify factual claims in research paper sections"
    
    def _run(self, abstract_chunks: List[str], methodology_chunks: List[str], 
             results_chunks: List[str], conclusion_chunks: List[str]) -> str:
        """Execute fact-check analysis on all section chunks."""
        llm = get_llm()
        
        # Combine all chunks, limit to 6 total
        all_chunks = (abstract_chunks + methodology_chunks + results_chunks + conclusion_chunks)[:6]
        
        if not all_chunks:
            return "No content available for fact-check analysis."
        
        # MAP phase
        chunk_analyses = []
        for i, chunk in enumerate(all_chunks):
            prompt = FACTCHECK_CHUNK_PROMPT.format(chunk=chunk)
            messages = [
                {"role": "system", "content": FACTCHECK_SYSTEM},
                {"role": "user", "content": prompt},
            ]
            response = llm.invoke(messages)
            analysis = response.content if hasattr(response, "content") else str(response)
            chunk_analyses.append(f"--- Chunk {i+1} ---\n{analysis}")
        
        # REDUCE phase
        combined = "\n\n".join(chunk_analyses)
        reduce_prompt = FACTCHECK_REDUCE_PROMPT.format(analyses=combined)
        messages = [
            {"role": "system", "content": FACTCHECK_SYSTEM},
            {"role": "user", "content": reduce_prompt},
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
