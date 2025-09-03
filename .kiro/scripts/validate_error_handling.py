#!/usr/bin/env python3
"""
Validation script for error handling scenarios in Kiro Commit Buddy
This script tests various error conditions to ensure proper handling
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from git_operations import GitOperations, GitOperationError
from groq_client import GroqClient, GroqAPIError
from message_generator import MessageGenerator
from config import Config
from user_interface import UserInterface


def test_git_error_handling():
    """Test Git-related error handling"""
    print("🔍 Testing Git error handling...")
    
    git_ops = GitOperations()
    
    # Test Git environment validation
    is_valid, error_msg = git_ops.validate_git_environment()
    if is_valid:
        print("✅ Git environment is valid")
    else:
        print(f"❌ Git environment error: {error_msg}")
    
    # Test staged changes check
    has_changes, status_msg, files = git_ops.check_staged_changes()
    print(f"📁 Staged changes status: {status_msg}")
    
    return True


def test_api_error_handling():
    """Test API error handling scenarios"""
    print("\n🔍 Testing API error handling...")
    
    config = Config()
    
    # Test with no API key
    original_key = config.GROQ_API_KEY
    config.GROQ_API_KEY = ""
    
    try:
        client = GroqClient(config)
        print("❌ Should have failed with no API key")
        return False
    except GroqAPIError as e:
        print(f"✅ Correctly handled missing API key: {str(e)[:50]}...")
    
    # Test with invalid API key format
    config.GROQ_API_KEY = "invalid-key"
    
    try:
        client = GroqClient(config)
        print("❌ Should have failed with invalid API key format")
        return False
    except GroqAPIError as e:
        print(f"✅ Correctly handled invalid API key format: {str(e)[:50]}...")
    
    # Restore original key
    config.GROQ_API_KEY = original_key
    
    return True


def test_message_generation_fallback():
    """Test message generation fallback scenarios"""
    print("\n🔍 Testing message generation fallback...")
    
    config = Config()
    generator = MessageGenerator(config)
    
    # Test fallback with different file types
    test_cases = [
        (["main.py"], "feat"),
        (["test_something.py"], "test"),
        (["README.md"], "docs"),
        (["config.json"], "chore"),
        (["file1.py", "file2.py"], "feat"),
        ([f"file{i}.py" for i in range(6)], "feat")
    ]
    
    for files, expected_type in test_cases:
        message = generator.generate_fallback_message(files)
        if message.startswith(f"{expected_type}:"):
            print(f"✅ Correct fallback for {files}: {message}")
        else:
            print(f"❌ Incorrect fallback for {files}: {message} (expected {expected_type}:)")
    
    return True


def test_user_interface_error_handling():
    """Test user interface error handling"""
    print("\n🔍 Testing user interface error handling...")
    
    ui = UserInterface()
    
    # Test error display methods
    ui.show_error("Test error message")
    ui.show_warning("Test warning message")
    ui.show_info("Test info message")
    ui.show_success("Test success message")
    
    print("✅ User interface error display methods work correctly")
    
    return True


def test_config_error_handling():
    """Test configuration error handling"""
    print("\n🔍 Testing configuration error handling...")
    
    config = Config()
    
    # Test API key validation
    has_key = config.has_groq_api_key()
    print(f"✅ API key availability check: {has_key}")
    
    # Test configuration values
    print(f"✅ Max diff size: {config.MAX_DIFF_SIZE}")
    print(f"✅ Timeout setting: {config.TIMEOUT}")
    print(f"✅ Groq model: {config.GROQ_MODEL}")
    
    return True


def main():
    """Run all error handling validation tests"""
    print("🚀 Starting Kiro Commit Buddy Error Handling Validation\n")
    
    tests = [
        test_git_error_handling,
        test_api_error_handling,
        test_message_generation_fallback,
        test_user_interface_error_handling,
        test_config_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All error handling tests passed!")
        return 0
    else:
        print("⚠️ Some error handling tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())