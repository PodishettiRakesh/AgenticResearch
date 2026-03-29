"""
Novelty agent tasks.
"""

from typing import Any, Dict, List, Optional
from crewai import Task
from agents.base.task_base import TaskBase
from agents.prompts.novelty import NOVELTY_PROMPT


class NoveltyTask(TaskBase):
    """Task for novelty and originality assessment."""
    
    def __init__(self):
        description = """Assess the novelty and originality of research contributions.
        
        You must analyze these texts using this exact prompt:
        Abstract: {abstract_text}
        Conclusion: {conclusion_text}
        
        Use this prompt template: "{novelty_prompt}"
        System prompt: "{system_prompt}"
        
        Evaluate originality compared to existing literature, significance of contributions, and potential impact."""
        
        expected_output = """A thorough novelty assessment including:
        1. NOVELTY INDEX: (Highly Novel / Moderately Novel / Incremental / Low Novelty)
        2. CLAIMED CONTRIBUTIONS: bullet list
        3. LIKELY PRIOR WORK: mention related areas
        4. ORIGINALITY ASSESSMENT: 3-4 sentences
        5. SUGGESTED RELATED FIELDS: comma-separated list"""
        
        super().__init__(description, expected_output)
    
    def create_task(self, agent: Any, sections: Dict[str, str], 
                   chunked: Dict[str, List[str]], context: Optional[List] = None) -> Task:
        """Create a novelty assessment task."""
        self._validate_inputs(sections, chunked)
        
        # Get abstract and conclusion for novelty analysis
        abstract_text = sections.get("abstract", "Not available")[:2000]
        conclusion_text = sections.get("conclusion", "Not available")[:2000]
        
        # Format task description
        formatted_desc = self._format_task_description(
            abstract_text=abstract_text,
            conclusion_text=conclusion_text,
            novelty_prompt=NOVELTY_PROMPT,
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
