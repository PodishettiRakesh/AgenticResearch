#!/usr/bin/env python3
"""
Test script to verify LLM initialization works
"""

import sys
import os

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(__file__))

from utils.llm import get_llm

def test_llm():
    try:
        print("Testing LLM initialization...")
        llm = get_llm()
        print("✅ LLM initialized successfully!")
        print(f"Model: {llm.model}")
        return True
    except Exception as e:
        print(f"❌ Error initializing LLM: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_llm()
