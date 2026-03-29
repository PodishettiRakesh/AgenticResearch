"""
Fact-check agent for verifying factual claims.
"""

from typing import Any
from agents.base.agent_base import AgentBase
from agents.prompts.factcheck import FACTCHECK_SYSTEM


class FactCheckAgent(AgentBase):
    """Agent for verifying factual claims, citations, and statistical assertions."""
    
    def __init__(self):
        role = "Research Fact-Checker"
        goal = "Verify factual claims, citations, and statistical assertions"
        backstory = """You are a meticulous fact-checker and domain expert who verifies 
        all verifiable claims in research papers including constants, formulas, 
        historical data, and statistical assertions. You have extensive experience 
        identifying suspicious or exaggerated claims."""
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False
        )
    
    def create_agent(self, llm: Any) -> Any:
        """Create the fact-check agent with specific system prompt."""
        agent = super().create_agent(llm)
        return agent
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return FACTCHECK_SYSTEM
