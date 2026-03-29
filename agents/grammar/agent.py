"""
Grammar agent for evaluating language quality.
"""

from typing import Any
from agents.base.agent_base import AgentBase
from agents.prompts.grammar import GRAMMAR_SYSTEM


class GrammarAgent(AgentBase):
    """Agent for evaluating grammar, tone, and professional writing quality."""
    
    def __init__(self):
        role = "Academic Language Editor"
        goal = "Assess grammar, tone, and professional writing quality"
        backstory = """You are an expert academic editor with a PhD in linguistics and 
        extensive experience reviewing research papers. You evaluate professional tone, 
        grammatical correctness, clarity, and adherence to academic writing standards."""
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False
        )
    
    def create_agent(self, llm: Any) -> Any:
        """Create the grammar agent with specific system prompt."""
        agent = super().create_agent(llm)
        return agent
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return GRAMMAR_SYSTEM
