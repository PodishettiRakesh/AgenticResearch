"""
Consistency agent tasks.
"""

from typing import Any, Dict, List, Optional
from crewai import Task
from agents.base.task_base import TaskBase
from agents.prompts.consistency import (
    CONSISTENCY_CHUNK_PROMPT,
    CONSISTENCY_REDUCE_PROMPT
)


class ConsistencyTask(TaskBase):
    """Task for consistency analysis using Map-Reduce pattern."""
    
    def __init__(self):
        description = """Analyze logical consistency between methodology and results sections.
        
        You must perform a Map-Reduce analysis on these chunks:
        - Methodology chunks: {methodology_chunks}
        - Results chunks: {results_chunks}
        
        Use this exact process:
        1. MAP: For each chunk, use this prompt: "{chunk_prompt}"
        2. REDUCE: Combine all analyses and use this prompt: "{reduce_prompt}"
        3. System prompt: "{system_prompt}"
        
        Focus on identifying gaps between what the methodology promises and what 
        the results claim. Provide a detailed consistency analysis."""
        
        expected_output = """A detailed consistency analysis including:
        1. OVERALL CONSISTENCY SCORE: (integer 0-100)
        2. MAJOR INCONSISTENCIES: bullet list
        3. MINOR ISSUES: bullet list
        4. SUMMARY: 2-3 sentences"""
        
        super().__init__(description, expected_output)
    
    def create_task(self, agent: Any, sections: Dict[str, str], 
                   chunked: Dict[str, List[str]], context: Optional[List] = None) -> Task:
        """Create a consistency analysis task."""
        self._validate_inputs(sections, chunked)
        
        # Get methodology and results chunks
        methodology_chunks = chunked.get("methodology", [])
        results_chunks = chunked.get("results", [])
        
        # Limit to 6 chunks total
        all_chunks = (methodology_chunks + results_chunks)[:6]
        
        # Format task description
        formatted_desc = self._format_task_description(
            methodology_chunks=methodology_chunks,
            results_chunks=results_chunks,
            chunk_prompt=CONSISTENCY_CHUNK_PROMPT,
            reduce_prompt=CONSISTENCY_REDUCE_PROMPT,
            system_prompt=agent.get_system_prompt() if hasattr(agent, 'get_system_prompt') else ""
        )
        
        task = Task(
            description=formatted_desc,
            expected_output=self.expected_output,
            agent=agent,
            async_execution=False
        )
        
        return task
