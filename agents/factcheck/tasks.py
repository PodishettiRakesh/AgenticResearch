"""
Fact-check agent tasks.
"""

from typing import Any, Dict, List, Optional
from crewai import Task
from agents.base.task_base import TaskBase
from agents.prompts.factcheck import (
    FACTCHECK_CHUNK_PROMPT,
    FACTCHECK_REDUCE_PROMPT
)


class FactCheckTask(TaskBase):
    """Task for fact-checking using Map-Reduce pattern."""
    
    def __init__(self):
        description = """Verify factual claims, citations, and statistical assertions.
        
        You must perform a Map-Reduce analysis on these chunks:
        - All sections chunks: {all_chunks}
        
        Use this exact process:
        1. MAP: For each chunk, use this prompt: "{chunk_prompt}"
        2. REDUCE: Combine all analyses and use this prompt: "{reduce_prompt}"
        3. System prompt: "{system_prompt}"
        
        Examine for constants, formulas, historical facts, statistical assertions, and citations."""
        
        expected_output = """A comprehensive fact-check log including:
        1. VERIFIED CLAIMS: bullet list
        2. UNVERIFIED CLAIMS: bullet list
        3. SUSPICIOUS CLAIMS: bullet list
        4. FACT-CHECK SUMMARY: 2-3 sentences"""
        
        super().__init__(description, expected_output)
    
    def create_task(self, agent: Any, sections: Dict[str, str], 
                   chunked: Dict[str, List[str]], context: Optional[List] = None) -> Task:
        """Create a fact-check analysis task."""
        self._validate_inputs(sections, chunked)
        
        # Combine all chunks, limit to 6 total
        all_chunks = []
        for sec in ["abstract", "methodology", "results", "conclusion"]:
            all_chunks.extend(chunked.get(sec, []))
        all_chunks = all_chunks[:6]
        
        # Format task description
        formatted_desc = self._format_task_description(
            all_chunks=all_chunks,
            chunk_prompt=FACTCHECK_CHUNK_PROMPT,
            reduce_prompt=FACTCHECK_REDUCE_PROMPT,
            system_prompt=agent.get_system_prompt() if hasattr(agent, 'get_system_prompt') else ""
        )
        
        task = Task(
            description=formatted_desc,
            expected_output=self.expected_output,
            agent=agent,
            async_execution=False,
            context=context
        )
        
        return task
