"""
tools.py
-------
Custom CrewAI tools that wrap the existing Map-Reduce and single-call logic.
These tools preserve all existing functionality while making them compatible with CrewAI agents.
"""

from typing import List, Dict
from crewai.tools import BaseTool
from pydantic import Field
from utils.llm import get_llm
from agents.prompts import (
    CONSISTENCY_SYSTEM, CONSISTENCY_CHUNK_PROMPT, CONSISTENCY_REDUCE_PROMPT,
    GRAMMAR_SYSTEM, GRAMMAR_PROMPT,
    NOVELTY_SYSTEM, NOVELTY_PROMPT,
    FACTCHECK_SYSTEM, FACTCHECK_CHUNK_PROMPT, FACTCHECK_REDUCE_PROMPT,
    FABRICATION_PROMPT,
)


class MapReduceTool(BaseTool):
    """Tool for performing Map-Reduce analysis on text chunks."""
    
    name: str = "map_reduce_analysis"
    description: str = "Analyze text chunks using Map-Reduce pattern for comprehensive evaluation"
    
    system_prompt: str = Field(description="System prompt for the analysis")
    chunk_prompt: str = Field(description="Prompt template for individual chunks")
    reduce_prompt: str = Field(description="Prompt template for reducing results")
    
    def _run(self, chunks: List[str]) -> str:
        """Execute Map-Reduce analysis on the provided chunks."""
        llm = get_llm()
        
        if not chunks:
            return "No content available for analysis."
        
        # MAP phase
        chunk_analyses = []
        for i, chunk in enumerate(chunks):
            prompt = self.chunk_prompt.format(chunk=chunk)
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
            response = llm.invoke(messages)
            analysis = response.content if hasattr(response, "content") else str(response)
            chunk_analyses.append(f"--- Chunk {i+1} ---\n{analysis}")
        
        # REDUCE phase
        combined = "\n\n".join(chunk_analyses)
        reduce_prompt = self.reduce_prompt.format(analyses=combined)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": reduce_prompt},
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)


class SingleCallTool(BaseTool):
    """Tool for single-call analysis without chunking."""
    
    name: str = "single_call_analysis"
    description: str = "Perform single-call analysis on provided text"
    
    system_prompt: str = Field(description="System prompt for the analysis")
    user_prompt: str = Field(description="User prompt template")
    
    def _run(self, text: str) -> str:
        """Execute single-call analysis on the provided text."""
        llm = get_llm()
        
        prompt = self.user_prompt.format(text=text)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)


class ConsistencyMapReduceTool(BaseTool):
    """Specialized tool for consistency analysis using Map-Reduce."""
    
    name: str = "consistency_analysis"
    description: str = "Analyze logical consistency between methodology and results"
    
    def _run(self, methodology_chunks: list, results_chunks: list) -> str:
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


class FactCheckMapReduceTool(BaseTool):
    """Specialized tool for fact-checking using Map-Reduce."""
    
    name: str = "fact_check_analysis"
    description: str = "Verify factual claims in research paper sections"
    
    def _run(self, abstract_chunks: list, methodology_chunks: list, results_chunks: list, conclusion_chunks: list) -> str:
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


class GrammarAnalysisTool(SingleCallTool):
    """Specialized tool for grammar and language analysis."""
    
    name: str = "grammar_analysis"
    description: str = "Evaluate grammar, tone, and language quality"
    
    def __init__(self):
        super().__init__(
            system_prompt=GRAMMAR_SYSTEM,
            user_prompt=GRAMMAR_PROMPT
        )


class NoveltyAnalysisTool(SingleCallTool):
    """Specialized tool for novelty assessment."""
    
    name: str = "novelty_analysis"
    description: str = "Assess novelty and originality of research contributions"
    
    def __init__(self):
        super().__init__(
            system_prompt=NOVELTY_SYSTEM,
            user_prompt=NOVELTY_PROMPT
        )


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
