"""
Grammar agent tools.
"""

from typing import List
from crewai.tools import BaseTool
from pydantic import Field
from utils.llm_hybrid import get_llm
from agents.prompts.grammar import GRAMMAR_SYSTEM, GRAMMAR_PROMPT


class GrammarAnalysisTool(BaseTool):
    """Tool for grammar and language analysis."""
    
    name: str = "grammar_analysis"
    description: str = "Evaluate grammar, tone, and language quality"
    
    text: str = Field(description="Text to analyze for grammar and quality")
    
    def _run(self, text: str) -> str:
        """Execute grammar analysis on the provided text."""
        llm = get_llm()
        
        prompt = GRAMMAR_PROMPT.format(text=text)
        messages = [
            {"role": "system", "content": GRAMMAR_SYSTEM},
            {"role": "user", "content": prompt},
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
