"""
llm.py
------
Initialises the Gemini LLM for use with CrewAI.

CrewAI accepts any LangChain-compatible chat model.
We use langchain-google-genai which wraps the Gemini API.
"""

import os
import asyncio
import threading
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def _ensure_event_loop():
    """Ensure there's an event loop in the current thread."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop in this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def get_llm(
    model: str = "gemini-1.5-flash",
    temperature: float = 0.3,
    max_output_tokens: int = 2048,
) -> ChatGoogleGenerativeAI:
    """
    Return a configured Gemini LLM instance.

    Args:
        model:             Gemini model name.
                           'gemini-1.5-flash' is free-tier friendly and fast.
        temperature:       Sampling temperature (lower = more deterministic).
        max_output_tokens: Cap on response length.

    Returns:
        A LangChain ChatGoogleGenerativeAI instance ready for CrewAI.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY not found. "
            "Please set it in your .env file or environment variables."
        )

    # Fix for event loop issue in Streamlit/ScriptRunner thread
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
