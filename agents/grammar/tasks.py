"""
Grammar agent tasks.
"""

from typing import Any, Dict, List, Optional
from crewai import Task
from agents.base.task_base import TaskBase
from agents.prompts.grammar import GRAMMAR_PROMPT


class GrammarTask(TaskBase):
    """Task for grammar and language analysis."""
    
    def __init__(self):
        description = """Evaluate grammar, language quality, and professional academic tone.
        
        You must analyze this text using this exact prompt:
        Text to analyze: {grammar_text}
        
        Use this prompt template: "{grammar_prompt}"
        System prompt: "{system_prompt}"
        
        Analyze for grammatical correctness, professional academic tone, clarity, and adherence to academic writing standards."""
        
        expected_output = """A comprehensive grammar evaluation including:
        1. GRAMMAR RATING: (High / Medium / Low)
        2. TONE ASSESSMENT: (Professional / Acceptable / Informal)
        3. NOTABLE ISSUES: bullet list (max 10)
        4. POSITIVE ASPECTS: bullet list (max 5)
        5. OVERALL LANGUAGE SUMMARY: 2-3 sentences"""
        
        super().__init__(description, expected_output)
    
    def create_task(self, agent: Any, sections: Dict[str, str], 
                   chunked: Dict[str, List[str]], context: Optional[List] = None) -> Task:
        """Create a grammar analysis task."""
        self._validate_inputs(sections, chunked)
        
        # Combine abstract and introduction for grammar analysis
        grammar_text = (sections.get("abstract", "") + "\n\n" + 
                       sections.get("introduction", ""))[:4000]
        
        # Format task description
        formatted_desc = self._format_task_description(
            grammar_text=grammar_text,
            grammar_prompt=GRAMMAR_PROMPT,
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
