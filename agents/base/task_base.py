"""
Base task class with common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from crewai import Task
from core.interfaces import TaskInterface


class TaskBase(TaskInterface):
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
    
    @abstractmethod
    def create_task(self, agent: Any, sections: Dict[str, str], 
                   chunked: Dict[str, List[str]], context: Optional[List] = None) -> Task:
        """Create a CrewAI task for the specified agent."""
        pass
    
    def _format_task_description(self, **kwargs) -> str:
        """Format task description with provided parameters."""
        try:
            return self.description.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for task description: {e}")
    
    def _validate_inputs(self, sections: Dict[str, str], 
                        chunked: Dict[str, List[str]]) -> None:
        """Validate required inputs for task creation."""
        if not sections:
            raise ValueError("Sections dictionary cannot be empty")
        if not chunked:
            raise ValueError("Chunked dictionary cannot be empty")
