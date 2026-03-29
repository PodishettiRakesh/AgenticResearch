"""
Custom exceptions for the AgenticResearch system.
"""


class AgenticResearchError(Exception):
    """Base exception for all AgenticResearch errors."""
    pass


class AgentError(AgenticResearchError):
    """Exception raised when agent operations fail."""
    pass


class TaskError(AgenticResearchError):
    """Exception raised when task operations fail."""
    pass


class PipelineError(AgenticResearchError):
    """Exception raised when pipeline operations fail."""
    pass


class ConfigurationError(AgenticResearchError):
    """Exception raised when configuration is invalid."""
    pass


class LLMError(AgenticResearchError):
    """Exception raised when LLM operations fail."""
    pass


class ScrapingError(AgenticResearchError):
    """Exception raised when scraping operations fail."""
    pass


class ProcessingError(AgenticResearchError):
    """Exception raised when text processing operations fail."""
    pass


class ReportGenerationError(AgenticResearchError):
    """Exception raised when report generation fails."""
    pass
