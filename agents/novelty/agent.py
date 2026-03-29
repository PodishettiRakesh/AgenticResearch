"""
Novelty agent for assessing research originality.
"""

from typing import Any
from agents.base.agent_base import AgentBase
from agents.prompts.novelty import NOVELTY_SYSTEM


class NoveltyAgent(AgentBase):
    """Agent for evaluating the novelty and originality of research contributions."""
    
    def __init__(self):
        role = "Research Novelty Assessor"
        goal = "Evaluate the novelty and originality of research contributions"
        backstory = """You are a senior research scientist with broad knowledge across 
        computer science, AI, physics, biology, and engineering. You assess novelty by 
        comparing claimed contributions against existing literature and identifying 
        truly original work."""
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False
        )
    
    def create_agent(self, llm: Any) -> Any:
        """Create the novelty agent with specific system prompt."""
        agent = super().create_agent(llm)
        return agent
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return NOVELTY_SYSTEM
