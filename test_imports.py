#!/usr/bin/env python3
"""
Test imports for the new structure.
"""

print("Testing imports...")

try:
    from agents.prompts.consistency import CONSISTENCY_SYSTEM
    print("✅ Consistency prompt import successful")
except Exception as e:
    print(f"❌ Consistency prompt import failed: {e}")

try:
    from agents.base.agent_base import AgentBase
    print("✅ Base agent import successful")
except Exception as e:
    print(f"❌ Base agent import failed: {e}")

try:
    from agents.consistency.agent import ConsistencyAgent
    print("✅ Consistency agent import successful")
except Exception as e:
    print(f"❌ Consistency agent import failed: {e}")

try:
    from utils.llm import get_llm
    print("✅ LLM utility import successful")
except Exception as e:
    print(f"❌ LLM utility import failed: {e}")

try:
    from utils.scraping import scrape_arxiv, parse_sections
    print("✅ Scraping utilities import successful")
except Exception as e:
    print(f"❌ Scraping utilities import failed: {e}")

try:
    from utils.processing import chunk_sections
    print("✅ Processing utilities import successful")
except Exception as e:
    print(f"❌ Processing utilities import failed: {e}")

try:
    from utils.config import settings
    print("✅ Config import successful")
except Exception as e:
    print(f"❌ Config import failed: {e}")

print("\nAll imports tested!")
