#!/usr/bin/env python3
"""
Test different Groq models to find which ones are currently available
"""

import sys
import os
import requests
from pathlib import Path

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_model(model_name, api_key):
    """Test if a specific model is available"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 1,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Available"
        elif response.status_code == 400:
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Unknown error")
                if "decommissioned" in error_msg.lower():
                    return False, "Decommissioned"
                else:
                    return False, f"Error: {error_msg}"
            except:
                return False, f"HTTP 400: {response.text[:100]}"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Exception: {str(e)}"

def main():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not set")
        return 1
    
    # List of models to test
    models_to_test = [
        "llama3-8b-8192",
        "llama3-70b-8192", 
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "llama-3.2-1b-preview",
        "llama-3.2-3b-preview",
        "llama-3.2-11b-text-preview",
        "llama-3.2-90b-text-preview",
        "mixtral-8x7b-32768",
        "gemma-7b-it",
        "gemma2-9b-it"
    ]
    
    print("🧪 Testing Groq Model Availability")
    print("=" * 50)
    
    available_models = []
    
    for model in models_to_test:
        print(f"Testing {model}...", end=" ")
        is_available, status = test_model(model, api_key)
        
        if is_available:
            print(f"✅ {status}")
            available_models.append(model)
        else:
            print(f"❌ {status}")
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if available_models:
        print(f"✅ Available models ({len(available_models)}):")
        for model in available_models:
            print(f"  - {model}")
        
        print(f"\n🔧 Recommended model to use: {available_models[0]}")
    else:
        print("❌ No available models found")
        print("This could indicate:")
        print("  - API key issues")
        print("  - Network connectivity problems")
        print("  - All tested models are decommissioned")
    
    return 0 if available_models else 1

if __name__ == "__main__":
    sys.exit(main())