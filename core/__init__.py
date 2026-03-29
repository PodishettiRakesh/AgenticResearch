"""
Core components for the AgenticResearch pipeline.
"""

from .interfaces import AgentInterface, TaskInterface
from .exceptions import (
    AgentError,
    TaskError,
    PipelineError,
    ConfigurationError
)

__all__ = [
    'AgentInterface', 
    'TaskInterface',
    'AgentError',
    'TaskError', 
    'PipelineError',
    'ConfigurationError'
]
