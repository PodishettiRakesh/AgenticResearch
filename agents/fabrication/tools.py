"""
Fabrication aggregator agent tools.
"""

from typing import List
from crewai.tools import BaseTool
from pydantic import Field
from utils.llm_hybrid import get_llm
from agents.prompts.fabrication import FABRICATION_PROMPT


class FabricationAggregatorTool(BaseTool):
    """Tool for aggregating all agent results and calculating fabrication probability."""
    
    name: str = "fabrication_aggregation"
    description: str = "Calculate fabrication probability based on all agent analyses"
    
    def _run(self, context: str) -> str:
        """Aggregate all results and calculate fabrication probability."""
        llm = get_llm()
        
        # The context should contain all previous task outputs
        # Extract scores from the context
        import re
        
        # Default values
        consistency_score = 70
        grammar_rating = "Medium"
        novelty_index = "Moderately Novel"
        factcheck_summary = "Fact-check analysis completed."
        
        # Extract consistency score
        consistency_match = re.search(r"OVERALL CONSISTENCY SCORE[:\s]+(\d{1,3})", context, re.IGNORECASE)
        if consistency_match:
            consistency_score = min(int(consistency_match.group(1)), 100)
        
        # Extract grammar rating
        grammar_match = re.search(r"GRAMMAR RATING[:\s]+(High|Medium|Low)", context, re.IGNORECASE)
        if grammar_match:
            grammar_rating = grammar_match.group(1).capitalize()
        
        # Extract novelty index
        novelty_match = re.search(
            r"NOVELTY INDEX[:\s]+(Highly Novel|Moderately Novel|Incremental|Low Novelty)",
            context, re.IGNORECASE
        )
        if novelty_match:
            novelty_index = novelty_match.group(1)
        
        # Extract fact-check summary
        factcheck_match = re.search(
            r"FACT-CHECK SUMMARY[:\s]+(.*?)(?:\n\n|\d+\.|\Z)",
            context, re.IGNORECASE | re.DOTALL
        )
        if factcheck_match:
            factcheck_summary = factcheck_match.group(1).strip()[:500]
        
        fab_prompt = FABRICATION_PROMPT.format(
            consistency_score=consistency_score,
            grammar_rating=grammar_rating,
            novelty_index=novelty_index,
            factcheck_summary=factcheck_summary,
        )
        
        messages = [
            {"role": "system", "content": "You are an expert research integrity analyst."},
            {"role": "user", "content": fab_prompt},
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
