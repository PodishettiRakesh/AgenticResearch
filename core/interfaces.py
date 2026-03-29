"""
Core interfaces for the AgenticResearch system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class AgentInterface(ABC):
    """Abstract interface for all agents."""
    
    @abstractmethod
    def create_agent(self, llm: Any) -> Any:
        """Create and configure the agent with the specified LLM."""
        pass
    
    @abstractmethod
    def get_role(self) -> str:
        """Get the agent's role description."""
        pass
    
    @abstractmethod
    def get_goal(self) -> str:
        """Get the agent's primary goal."""
        pass
    
    @abstractmethod
    def get_backstory(self) -> str:
        """Get the agent's backstory/context."""
        pass


class TaskInterface(ABC):
    """Abstract interface for all tasks."""
    
    @abstractmethod
    def create_task(self, agent: Any, sections: Dict[str, str], 
                   chunked: Dict[str, List[str]], context: Optional[List] = None) -> Any:
        """Create a task for the specified agent."""
        pass
    
    @abstractmethod
    def get_expected_output(self) -> str:
        """Get the expected output format for this task."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get the task description."""
        pass


class ToolInterface(ABC):
    """Abstract interface for agent tools."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the tool name."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get the tool description."""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> str:
        """Execute the tool with given arguments."""
        pass


class PipelineInterface(ABC):
    """Abstract interface for research pipeline."""
    
    @abstractmethod
    def run(self, arxiv_url: str, **kwargs) -> Dict[str, Any]:
        """Run the complete research pipeline."""
        pass
    
    @abstractmethod
    def validate_inputs(self, arxiv_url: str) -> bool:
        """Validate pipeline inputs."""
        pass
