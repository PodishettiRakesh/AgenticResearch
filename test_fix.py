#!/usr/bin/env python3
"""
Test script to verify the event loop fix works
"""

import sys
import os
import asyncio

# Set environment variable to force synchronous transport before any imports
os.environ["GRPC_ASYNCIO_TRANSPORT"] = "None"

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(__file__))

# Fix event loop issue
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

print("Testing LLM initialization with fixed event loop...")

try:
    from utils.llm import get_llm
    llm = get_llm()
    print("✅ SUCCESS: LLM initialized without event loop error!")
    print(f"Model: {llm.model}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting agent setup...")
try:
    from agents.crew_setup import run_agents
    print("✅ SUCCESS: Agent setup imported successfully!")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
