"""
llm_hybrid.py
------------
Hybrid LLM setup supporting both Gemini (cloud) and Ollama (local) providers.
Environment-based selection allows flexible switching between providers.
"""

import os
import asyncio
from dotenv import load_dotenv
from typing import Union

load_dotenv()

# Environment configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # "gemini" or "ollama"


def _ensure_event_loop():
    """Ensure there's an event loop in the current thread."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop in this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def get_gemini_llm(
    model: str = "gemini-2.0-flash",
    temperature: float = 0.3,
    max_output_tokens: int = 2048,
):
    """Get Gemini LLM instance (cloud-based)."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY not found for Gemini provider. "
                "Please set it in your .env file or environment variables."
            )

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
    Get LLM instance based on environment configuration.
    
    Args:
        provider: Override LLM provider ("gemini" or "ollama")
        **kwargs: Additional parameters for LLM initialization
    
    Returns:
        LLM instance (Gemini or Ollama)
    """
    # Use provider from parameter or environment
    provider = (provider or LLM_PROVIDER).lower()
    
    print(f"[LLM] Initializing provider: {provider}")
    
    if provider == "ollama":
        return get_ollama_llm(**kwargs)
    elif provider == "gemini":
        return get_gemini_llm(**kwargs)
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            "Supported providers: 'gemini', 'ollama'"
        )


def get_provider_info():
    """Get current LLM provider information."""
    return {
        "provider": LLM_PROVIDER,
        "type": "local" if LLM_PROVIDER == "ollama" else "cloud",
        "model": "llama3:8b" if LLM_PROVIDER == "ollama" else "gemini-2.0-flash",
        "advantages": {
            "ollama": ["Free", "No quota limits", "Offline", "Private"],
            "gemini": ["High quality", "No setup required", "Cloud-based"]
        }[LLM_PROVIDER]
    }


if __name__ == "__main__":
    # Test LLM initialization
    print("Testing hybrid LLM setup...")
    print(f"Current provider: {LLM_PROVIDER}")
    
    try:
        llm = get_llm()
        print(f"✅ LLM initialized successfully!")
        print(f"Provider info: {get_provider_info()}")
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
