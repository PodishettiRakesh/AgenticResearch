"""
Fabrication aggregator agent tasks.
"""

from typing import Any, Dict, List, Optional
from crewai import Task
from agents.base.task_base import TaskBase
from agents.prompts.fabrication import FABRICATION_PROMPT


class FabricationTask(TaskBase):
    """Task for aggregating all agent results and calculating fabrication probability."""
    
    def __init__(self):
        description = """Synthesize all agent analyses and calculate fabrication probability.
        
        You must aggregate all previous results and calculate fabrication probability.
        
        Use this exact prompt template: "{fabrication_prompt}"
        
        Extract these values from the previous analyses:
        - Consistency score (from consistency analysis)
        - Grammar rating (from grammar analysis)  
        - Novelty index (from novelty analysis)
        - Fact-check summary (from fact-check analysis)
        
        Provide overall fabrication probability assessment, risk level, executive summary, and final recommendation."""
        
        expected_output = """A final integrity assessment including:
        1. FABRICATION PROBABILITY: (0-100%)
        2. RISK LEVEL: (Low / Medium / High / Critical)
        3. EXECUTIVE SUMMARY: 3-4 sentences
        4. RECOMMENDATION: PASS or FAIL with justification"""
        
        super().__init__(description, expected_output)
    
    def create_task(self, agent: Any, sections: Dict[str, str], 
                   chunked: Dict[str, List[str]], context: Optional[List] = None) -> Task:
        """Create a fabrication aggregation task."""
        self._validate_inputs(sections, chunked)
        
        # Format task description
        formatted_desc = self._format_task_description(
            fabrication_prompt=FABRICATION_PROMPT
        )
        
        task = Task(
            description=formatted_desc,
            expected_output=self.expected_output,
            agent=agent,
            async_execution=False,
            context=context
        )
        
        return task
