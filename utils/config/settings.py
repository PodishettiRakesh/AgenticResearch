"""
Configuration management for AgenticResearch.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from core.exceptions import ConfigurationError

load_dotenv()


class Settings:
    """Centralized configuration management."""
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    # Individual Provider Controls
    GEMINI_ENABLED: bool = os.getenv("GEMINI_ENABLED", "true").lower() == "true"
    OLLAMA_ENABLED: bool = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
    
    # Provider Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3:8b")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Task Configuration
    MAX_CHUNKS_PER_TASK: int = int(os.getenv("MAX_CHUNKS_PER_TASK", "6"))
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "4000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))
    
    # Scraping Configuration
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    USER_AGENT: str = os.getenv("USER_AGENT", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Processing Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Report Configuration
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "reports")
    REPORT_FORMAT: str = os.getenv("REPORT_FORMAT", "markdown")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "agentic_research.log")
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings."""
        errors = []
        
        # Validate LLM provider
        if cls.LLM_PROVIDER not in ["gemini", "ollama"]:
            errors.append(f"Invalid LLM provider: {cls.LLM_PROVIDER}")
        
        # Validate Gemini configuration
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY required when using Gemini provider")
        
        # Validate numeric values
        if cls.TEMPERATURE < 0 or cls.TEMPERATURE > 2:
            errors.append(f"Invalid temperature: {cls.TEMPERATURE}. Must be between 0 and 2")
        
        if cls.MAX_OUTPUT_TOKENS < 1:
            errors.append(f"Invalid max_output_tokens: {cls.MAX_OUTPUT_TOKENS}. Must be > 0")
        
        if cls.CHUNK_SIZE < 100:
            errors.append(f"Invalid chunk_size: {cls.CHUNK_SIZE}. Must be >= 100")
        
        if errors:
            raise ConfigurationError("Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors))
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """Get availability status of all providers."""
        return {
            "gemini": cls.GEMINI_ENABLED and bool(cls.GEMINI_API_KEY),
            "ollama": cls.OLLAMA_ENABLED
        }
    
    @classmethod
    def get_active_provider(cls) -> str:
        """Determine the best available provider."""
        available = cls.get_available_providers()
        
        # If LLM_PROVIDER is explicitly set and available, use it
        if cls.LLM_PROVIDER in available and available[cls.LLM_PROVIDER]:
            return cls.LLM_PROVIDER
        
        # Auto-select best available provider
        if available["ollama"]:
            return "ollama"
        elif available["gemini"]:
            return "gemini"
        else:
            raise ConfigurationError("No LLM provider is available. Configure GEMINI_API_KEY or enable Ollama.")
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM-specific configuration."""
        provider = cls.get_active_provider()
        
        if provider == "gemini":
            return {
                "provider": "gemini",
                "model": cls.GEMINI_MODEL,
                "api_key": cls.GEMINI_API_KEY,
                "temperature": cls.TEMPERATURE,
                "max_output_tokens": cls.MAX_OUTPUT_TOKENS
            }
        elif provider == "ollama":
            return {
                "provider": "ollama",
                "model": cls.OLLAMA_MODEL,
                "base_url": cls.OLLAMA_BASE_URL,
                "temperature": cls.TEMPERATURE,
                "max_tokens": cls.MAX_OUTPUT_TOKENS
            }
        else:
            raise ConfigurationError(f"Unsupported LLM provider: {provider}")
    
    @classmethod
    def get_processing_config(cls) -> Dict[str, Any]:
        """Get text processing configuration."""
        return {
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "max_chunks_per_task": cls.MAX_CHUNKS_PER_TASK,
            "max_text_length": cls.MAX_TEXT_LENGTH
        }
    
    @classmethod
    def get_scraping_config(cls) -> Dict[str, Any]:
        """Get scraping configuration."""
        return {
            "timeout": cls.REQUEST_TIMEOUT,
            "user_agent": cls.USER_AGENT
        }
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert all settings to dictionary."""
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith('_') and not callable(getattr(cls, attr))
        }


# Global settings instance
settings = Settings()

# Validate configuration on import
try:
    settings.validate()
except ConfigurationError as e:
    print(f"Configuration Warning: {e}")
    print("Please check your .env file or environment variables.")
