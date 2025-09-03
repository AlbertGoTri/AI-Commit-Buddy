#!/usr/bin/env python3
"""
Basic test for configuration module
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config


def test_config_basic():
    """Test basic configuration functionality"""
    config = Config()
    
    # Test basic properties
    assert config.GROQ_MODEL == "llama3-70b-8192"
    assert config.MAX_DIFF_SIZE == 8000
    assert config.TIMEOUT == 10
    assert config.MAX_TOKENS == 150
    assert config.TEMPERATURE == 0.3
    
    print("✓ Basic configuration properties work")
    
    # Test API key handling
    original_key = os.environ.get("GROQ_API_KEY")
    
    # Test without API key
    if "GROQ_API_KEY" in os.environ:
        del os.environ["GROQ_API_KEY"]
    
    config_no_key = Config()
    assert not config_no_key.has_groq_api_key()
    print("✓ API key detection works when not set")
    
    # Test with API key
    os.environ["GROQ_API_KEY"] = "test_key_123"
    config_with_key = Config()
    assert config_with_key.has_groq_api_key()
    assert config_with_key.get_groq_api_key() == "test_key_123"
    print("✓ API key detection works when set")
    
    # Test API headers
    headers = config_with_key.get_api_headers()
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_key_123"
    assert headers["Content-Type"] == "application/json"
    print("✓ API headers generation works")
    
    # Test prompt template
    template = config_with_key.get_commit_prompt_template()
    assert "{diff}" in template
    assert "Conventional Commits" in template
    print("✓ Prompt template works")
    
    # Restore original API key
    if original_key:
        os.environ["GROQ_API_KEY"] = original_key
    elif "GROQ_API_KEY" in os.environ:
        del os.environ["GROQ_API_KEY"]
    
    print("All configuration tests passed! ✓")


if __name__ == "__main__":
    test_config_basic()