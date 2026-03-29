#!/usr/bin/env python3
"""
Check available Gemini models
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def check_models():
    """Check what Gemini models are available"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found")
        return
    
    print("Testing different Gemini model names...")
    
    models_to_try = [
        "gemini-pro",
        "gemini-pro-vision", 
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest",
        "gemini-1.5-pro-001",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest", 
        "gemini-1.5-flash-001",
        "models/gemini-pro",
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash"
    ]
    
    for model in models_to_try:
        try:
            print(f"\nTesting: {model}")
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=0.1,
                max_output_tokens=10,
            )
            
            # Simple test
            response = llm.invoke("Hi")
            print(f"SUCCESS: {model} works!")
            print(f"   Response: {response.content[:50]}...")
            break
            
        except Exception as e:
            print(f"FAILED: {model} - {str(e)[:100]}...")

if __name__ == "__main__":
    check_models()
