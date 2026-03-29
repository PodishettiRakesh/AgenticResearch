#!/usr/bin/env python3
"""
Check available Ollama models using Ollama API
"""

import requests
import json
from typing import List, Dict, Optional
from utils.config.settings import settings


def check_ollama_connection() -> bool:
    """Check if Ollama server is running and accessible."""
    try:
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_available_models() -> List[Dict[str, str]]:
    """Get list of available Ollama models."""
    if not check_ollama_connection():
        print("ERROR: Ollama server not accessible")
        print(f"Make sure Ollama is running: ollama serve")
        return []
    
    try:
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        models = []
        for model in data.get('models', []):
            models.append({
                'name': model.get('name', 'Unknown'),
                'size': model.get('size', 0),
                'modified': model.get('modified', 'Unknown')
            })
        
        return models
    except requests.RequestException as e:
        print(f"Error fetching models: {e}")
        return []


def test_model(model_name: str) -> bool:
    """Test if a specific model is working."""
    if not check_ollama_connection():
        return False
    
    try:
        payload = {
            "model": model_name,
            "prompt": "Hello, test message",
            "stream": False
        }
        response = requests.post(f"{settings.OLLAMA_BASE_URL}/api/generate", 
                               json=payload, timeout=30)
        return response.status_code == 200
    except requests.RequestException:
        return False


def check_specific_model(model_name: str) -> Optional[Dict[str, str]]:
    """Check if a specific model is available and working."""
    models = get_available_models()
    
    for model in models:
        if model_name in model['name']:
            print(f"Found model: {model['name']}")
            
            # Test the model
            if test_model(model['name']):
                print(f"✅ {model['name']} is working!")
                return model
            else:
                print(f"❌ {model['name']} failed test")
                return None
    
    print(f"Model {model_name} not found")
    return None


def pull_model(model_name: str) -> bool:
    """Pull a new model from Ollama."""
    if not check_ollama_connection():
        print("ERROR: Ollama server not accessible")
        return False
    
    try:
        payload = {"name": model_name}
        response = requests.post(f"{settings.OLLAMA_BASE_URL}/api/pull", 
                               json=payload, timeout=300)  # 5 minute timeout
        
        if response.status_code == 200:
            print(f"✅ Successfully pulled {model_name}")
            return True
        else:
            print(f"❌ Failed to pull {model_name}")
            return False
    except requests.RequestException as e:
        print(f"Error pulling model: {e}")
        return False


def main():
    """Main function to check Ollama setup."""
    print("🔍 Checking Ollama setup...")
    print(f"Server: {settings.OLLAMA_BASE_URL}")
    print(f"Default model: {settings.OLLAMA_MODEL}")
    print()
    
    # Check connection
    if not check_ollama_connection():
        print("❌ Ollama server is not running")
        print("Start it with: ollama serve")
        return
    
    print("✅ Ollama server is running")
    print()
    
    # Get available models
    models = get_available_models()
    
    if not models:
        print("❌ No models found")
        print("Pull a model with: ollama pull llama3:8b")
        return
    
    print(f"📋 Found {len(models)} models:")
    for model in models:
        size_gb = model['size'] / (1024**3) if model['size'] > 0 else "Unknown"
        print(f"  - {model['name']} ({size_gb:.1f} GB)")
    
    print()
    
    # Check default model
    print(f"🔍 Testing default model: {settings.OLLAMA_MODEL}")
    if check_specific_model(settings.OLLAMA_MODEL):
        print("✅ Default model is working!")
    else:
        print(f"❌ Default model {settings.OLLAMA_MODEL} not available")
        print("Pull it with: ollama pull llama3:8b")


if __name__ == "__main__":
    main()
