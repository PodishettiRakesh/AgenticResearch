"""
Novelty agent tools.
"""

from typing import List
from crewai.tools import BaseTool
from pydantic import Field
from utils.llm_hybrid import get_llm
from agents.prompts.novelty import NOVELTY_SYSTEM, NOVELTY_PROMPT


class NoveltyAnalysisTool(BaseTool):
    """Tool for novelty and originality assessment."""
    
    name: str = "novelty_analysis"
    description: str = "Assess novelty and originality of research contributions"
    
    def _run(self, abstract: str, conclusion: str) -> str:
        """Execute novelty analysis on abstract and conclusion."""
        llm = get_llm()
        
        prompt = NOVELTY_PROMPT.format(abstract=abstract, conclusion=conclusion)
        messages = [
            {"role": "system", "content": NOVELTY_SYSTEM},
            {"role": "user", "content": prompt},
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
