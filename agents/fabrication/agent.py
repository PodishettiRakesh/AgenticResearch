"""
Fabrication aggregator agent for synthesizing analyses.
"""

from typing import Any
from agents.base.agent_base import AgentBase


class FabricationAgent(AgentBase):
    """Agent for synthesizing all analyses and calculating fabrication probability."""
    
    def __init__(self):
        role = "Research Integrity Analyst"
        goal = "Synthesize all analyses and calculate fabrication probability"
        backstory = """You are an expert research integrity analyst with deep experience 
        in identifying potentially fabricated or fraudulent research. You synthesize 
        multiple evaluation dimensions to provide an overall assessment of research 
        authenticity and integrity."""
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False
        )
    
    def create_agent(self, llm: Any) -> Any:
        """Create the fabrication aggregator agent."""
        agent = super().create_agent(llm)
        return agent
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return "You are an expert research integrity analyst."
