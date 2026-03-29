#!/usr/bin/env python3
"""
Check available Gemini models using official Google Generative AI API
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

def check_available_models():
    """Check what Gemini models are actually available using Google's API"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found")
        return
    
    print("Configuring API key...")
    genai.configure(api_key=api_key)
    
    print("\nFetching available models from Google Generative AI API...")
    try:
        models = genai.list_models()
        print(f"\nFound {len(models)} models:")
        
        gemini_models = []
        for model in models:
            model_name = model.name
            print(f"  - {model_name}")
            
            # Filter for Gemini models that support text generation
            if "gemini" in model_name.lower() and ("generate" in model.supported_generation_methods or "generateContent" in str(model.supported_generation_methods)):
                gemini_models.append(model_name)
        
        print(f"\nGemini text models ({len(gemini_models)}):")
        for model in gemini_models:
            print(f"  - {model}")
        
        # Test the first available Gemini model
        if gemini_models:
            test_model = gemini_models[0]
            print(f"\nTesting with: {test_model}")
            try:
                model = genai.GenerativeModel(test_model)
                response = model.generate_content("Hello, test message")
                print(f"SUCCESS: {test_model} works!")
                print(f"Response: {response.text[:100]}...")
                return test_model
            except Exception as e:
                print(f"FAILED: {test_model} - {str(e)}")
        else:
            print("No Gemini text models found!")
            
    except Exception as e:
        print(f"Error listing models: {str(e)}")

if __name__ == "__main__":
    check_available_models()
