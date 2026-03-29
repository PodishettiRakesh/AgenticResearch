"""
Base agent class with common functionality.
"""

from typing import Any, Dict
from crewai import Agent
from core.interfaces import AgentInterface


class AgentBase(AgentInterface):
    """Base class for all agents with common functionality."""
    
    def __init__(self, role: str, goal: str, backstory: str, 
                 verbose: bool = True, allow_delegation: bool = False):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        self._agent = None
    
    def create_agent(self, llm: Any) -> Agent:
        """Create and configure the CrewAI agent."""
        self._agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=llm,
            verbose=self.verbose,
            allow_delegation=self.allow_delegation
        )
        return self._agent
    
    def get_role(self) -> str:
        """Get the agent's role description."""
        return self.role
    
    def get_goal(self) -> str:
        """Get the agent's primary goal."""
        return self.goal
    
    def get_backstory(self) -> str:
        """Get the agent's backstory/context."""
        return self.backstory
    
    def get_agent(self) -> Agent:
        """Get the created CrewAI agent."""
        if self._agent is None:
            raise RuntimeError("Agent not created yet. Call create_agent() first.")
        return self._agent


class TaskBase:
    """Base class for all tasks with common functionality."""
    
    def __init__(self, description: str, expected_output: str):
        self.description = description
        self.expected_output = expected_output
    
    def get_description(self) -> str:
        """Get the task description."""
        return self.description
    
    def get_expected_output(self) -> str:
        """Get the expected output format."""
        return self.expected_output
