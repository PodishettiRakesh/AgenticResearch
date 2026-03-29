"""
llm_hybrid.py
------------
Hybrid LLM setup supporting both Gemini (cloud) and Ollama (local) providers.
Intelligent provider selection with individual controls and fallback capabilities.
"""

import os
import asyncio
from dotenv import load_dotenv
from typing import Union, Optional
from utils.config.settings import settings
from core.exceptions import ConfigurationError

load_dotenv()


def _ensure_event_loop():
    """Ensure there's an event loop in the current thread."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop in this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def get_gemini_llm(
    model: str = None,
    temperature: float = None,
    max_output_tokens: int = None,
):
    """Get Gemini LLM instance (cloud-based)."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        config = settings.get_llm_config()
        if config["provider"] != "gemini":
            raise ConfigurationError(f"Gemini requested but active provider is {config['provider']}")
        
        api_key = config["api_key"]
        if not api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY not found for Gemini provider. "
                "Please set it in your .env file or environment variables."
            )

        # Use config defaults if not specified
        model = model or config["model"]
        temperature = temperature or config["temperature"]
        max_output_tokens = max_output_tokens or config["max_output_tokens"]

        # Fix for event loop issue
        _ensure_event_loop()
        
        # Force use of synchronous transport to avoid async issues
        os.environ["GRPC_ASYNCIO_TRANSPORT"] = "None"
        
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            convert_system_message_to_human=True,  # Gemini quirk
        )

        print(f"[LLM] SUCCESS: Gemini model loaded: {model}")
        return llm
        
    except ImportError as e:
        raise ImportError(
            f"Failed to import Gemini dependencies: {e}. "
            "Install with: pip install langchain-google-genai"
        )


def get_ollama_llm(
    model: str = "llama3:8b",  # Lightweight model for low-resource systems
    temperature: float = 0.3,
    max_output_tokens: int = 2048,
):
    """Get Ollama LLM instance (local-based)."""
    try:
        from langchain_community.llms import Ollama
        
        # Check if Ollama is available
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                raise ConnectionError("Ollama server not running")
        except (requests.RequestException, ConnectionError):
            raise ConnectionError(
                "Ollama server not accessible. "
                "Start Ollama with: ollama serve"
            )
        
        llm = Ollama(
            model=model,
            temperature=temperature,
            max_tokens=max_output_tokens,
        )

        print(f"[LLM] SUCCESS: Ollama model loaded: {model}")
        return llm
        
    except ImportError as e:
        raise ImportError(
            f"Failed to import Ollama dependencies: {e}. "
            "Install with: pip install langchain-community"
        )


def get_llm(
    provider: str = None,
    **kwargs
) -> Union:
    """
    Get LLM instance based on intelligent provider selection.
    
    Args:
        provider: Override LLM provider ("gemini" or "ollama")
        **kwargs: Additional parameters for LLM initialization
    
    Returns:
        LLM instance (Gemini or Ollama)
    """
    # Use provider from parameter or intelligent selection
    if provider:
        selected_provider = provider.lower()
    else:
        selected_provider = settings.get_active_provider()
    
    print(f"[LLM] Initializing provider: {selected_provider}")
    
    if selected_provider == "ollama":
        return get_ollama_llm(**kwargs)
    elif selected_provider == "gemini":
        return get_gemini_llm(**kwargs)
    else:
        raise ConfigurationError(
            f"Unsupported LLM provider: {selected_provider}. "
            "Supported providers: 'gemini', 'ollama'"
        )


def get_provider_info():
    """Get current LLM provider information."""
    config = settings.get_llm_config()
    available = settings.get_available_providers()
    
    return {
        "active_provider": config["provider"],
        "type": "local" if config["provider"] == "ollama" else "cloud",
        "model": config["model"],
        "available_providers": available,
        "gemini_enabled": available["gemini"],
        "ollama_enabled": available["ollama"],
        "selection_method": "explicit" if settings.LLM_PROVIDER in available else "auto"
    }


if __name__ == "__main__":
    # Test LLM initialization
    print("Testing hybrid LLM setup...")
    print(f"Active provider: {settings.get_active_provider()}")
    print(f"Available providers: {settings.get_available_providers()}")
    
    try:
        llm = get_llm()
        print(f"✅ LLM initialized successfully!")
        print(f"Provider info: {get_provider_info()}")
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
