#!/usr/bin/env python3
"""
Test script to verify Groq API integration fixes
Tests the complete flow and identifies any remaining issues
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from groq_client import GroqClient, GroqAPIError
from message_generator import MessageGenerator
from api_debugger import APIDebugger
from verbose_logger import enable_verbose_logging, get_logger

def test_api_key_configuration():
    """Test API key configuration and validation"""
    print("🔑 Testing API Key Configuration...")
    
    config = Config()
    
    # Test 1: Check if API key is configured
    has_key = config.has_groq_api_key()
    print(f"   API Key Configured: {'✅' if has_key else '❌'}")
    
    if has_key:
        # Test 2: Validate API key format
        is_valid, error_msg = config.validate_api_key_format()
        print(f"   API Key Format Valid: {'✅' if is_valid else '❌'} {error_msg if not is_valid else ''}")
        
        # Test 3: Show API key info (masked)
        api_key = os.getenv("GROQ_API_KEY", "")
        print(f"   API Key Preview: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
    else:
        print("   ⚠️  GROQ_API_KEY environment variable not set")
        print("   To set it:")
        print("     Windows: set GROQ_API_KEY=your_key_here")
        print("     Linux/Mac: export GROQ_API_KEY=your_key_here")
    
    return has_key

def test_groq_client_initialization():
    """Test Groq client initialization"""
    print("\n🔧 Testing Groq Client Initialization...")
    
    try:
        config = Config()
        client = GroqClient(config)
        print("   ✅ Groq client initialized successfully")
        return client
    except GroqAPIError as e:
        print(f"   ❌ Groq client initialization failed: {str(e)}")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return None

def test_api_availability(client):
    """Test API availability"""
    print("\n🌐 Testing API Availability...")
    
    if not client:
        print("   ❌ Cannot test - no client available")
        return False
    
    try:
        is_available = client.is_api_available()
        print(f"   API Available: {'✅' if is_available else '❌'}")
        return is_available
    except Exception as e:
        print(f"   ❌ Error checking availability: {str(e)}")
        return False

def test_message_generation(client):
    """Test actual message generation"""
    print("\n💬 Testing Message Generation...")
    
    if not client:
        print("   ❌ Cannot test - no client available")
        return False
    
    sample_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
     print("Hello, World!")
+    print("Added new functionality")
"""
    
    try:
        message = client.generate_commit_message(sample_diff)
        print(f"   ✅ Generated message: '{message}'")
        
        # Check if it follows conventional commits
        conventional_prefixes = ['feat:', 'fix:', 'docs:', 'refactor:', 'test:', 'chore:']
        follows_convention = any(message.lower().startswith(prefix) for prefix in conventional_prefixes)
        print(f"   Follows Conventional Commits: {'✅' if follows_convention else '❌'}")
        
        return True
    except GroqAPIError as e:
        print(f"   ❌ API error: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False

def test_message_generator_flow():
    """Test the complete MessageGenerator flow"""
    print("\n🔄 Testing MessageGenerator Flow...")
    
    try:
        config = Config()
        generator = MessageGenerator(config)
        
        sample_diff = """diff --git a/src/main.py b/src/main.py
index abc123..def456 100644
--- a/src/main.py
+++ b/src/main.py
@@ -10,6 +10,7 @@ def main():
     print("Starting application")
+    print("Added logging functionality")
     return 0
"""
        
        files = ["src/main.py"]
        message = generator.generate_message(sample_diff, files)
        
        print(f"   ✅ Generated message: '{message}'")
        
        # Check if it's using AI or fallback
        if "update" in message.lower() and len(message.split()) <= 4:
            print("   ⚠️  Appears to be using fallback message")
            return False
        else:
            print("   ✅ Appears to be using AI-generated message")
            return True
            
    except Exception as e:
        print(f"   ❌ Error in MessageGenerator: {str(e)}")
        return False

def test_verbose_logging():
    """Test verbose logging functionality"""
    print("\n📝 Testing Verbose Logging...")
    
    try:
        # Enable verbose logging
        enable_verbose_logging()
        logger = get_logger()
        
        # Test different log levels
        logger.debug("Test debug message", "TEST")
        logger.info("Test info message", "TEST")
        logger.warning("Test warning message", "TEST")
        logger.error("Test error message", "TEST")
        
        print("   ✅ Verbose logging working")
        return True
    except Exception as e:
        print(f"   ❌ Verbose logging error: {str(e)}")
        return False

def test_end_to_end_with_verbose():
    """Test end-to-end flow with verbose logging"""
    print("\n🎯 Testing End-to-End Flow with Verbose Logging...")
    
    try:
        # Enable verbose logging
        enable_verbose_logging()
        
        # Test the complete flow
        config = Config()
        generator = MessageGenerator(config)
        
        sample_diff = """diff --git a/feature.py b/feature.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/feature.py
@@ -0,0 +1,3 @@
+def new_feature():
+    # Implement new user authentication feature
+    return authenticate_user()
"""
        
        files = ["feature.py"]
        
        print("   Generating message with verbose logging...")
        message = generator.generate_message(sample_diff, files)
        
        print(f"   ✅ Final message: '{message}'")
        
        # Analyze the result
        if "feat:" in message.lower():
            print("   ✅ Correctly identified as feature")
            return True
        elif "update" in message.lower():
            print("   ⚠️  Used fallback message instead of AI")
            return False
        else:
            print("   ✅ Generated custom message")
            return True
            
    except Exception as e:
        print(f"   ❌ End-to-end test failed: {str(e)}")
        return False

def run_comprehensive_api_diagnostics():
    """Run the comprehensive API diagnostics"""
    print("\n🔍 Running Comprehensive API Diagnostics...")
    
    try:
        debugger = APIDebugger()
        debugger.set_verbose(True)
        report = debugger.run_comprehensive_diagnostic()
        return report
    except Exception as e:
        print(f"   ❌ Diagnostics failed: {str(e)}")
        return None

def main():
    """Main test function"""
    print("🧪 Kiro Commit Buddy - API Integration Test Suite")
    print("=" * 60)
    
    # Track test results
    results = {}
    
    # Test 1: API Key Configuration
    results['api_key'] = test_api_key_configuration()
    
    # Test 2: Groq Client Initialization
    client = test_groq_client_initialization()
    results['client_init'] = client is not None
    
    # Test 3: API Availability
    results['api_available'] = test_api_availability(client)
    
    # Test 4: Message Generation
    results['message_gen'] = test_message_generation(client)
    
    # Test 5: MessageGenerator Flow
    results['generator_flow'] = test_message_generator_flow()
    
    # Test 6: Verbose Logging
    results['verbose_logging'] = test_verbose_logging()
    
    # Test 7: End-to-End with Verbose
    results['end_to_end'] = test_end_to_end_with_verbose()
    
    # Test 8: Comprehensive Diagnostics
    print("\n" + "=" * 60)
    diagnostic_report = run_comprehensive_api_diagnostics()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    # Overall assessment
    if passed == total and results['generator_flow']:
        print("\n🎉 ALL TESTS PASSED! API integration should work correctly.")
        return 0
    elif results['api_key'] and results['client_init'] and results['api_available']:
        print("\n⚠️  API is configured and available, but message generation may have issues.")
        print("   Check the verbose logs above for details.")
        return 1
    else:
        print("\n❌ API integration has issues. Check the diagnostics above.")
        print("\n🔧 NEXT STEPS:")
        if not results['api_key']:
            print("   1. Configure GROQ_API_KEY environment variable")
        if not results['api_available']:
            print("   2. Check network connectivity and API key validity")
        if not results['generator_flow']:
            print("   3. Debug MessageGenerator fallback logic")
        return 1

if __name__ == "__main__":
    sys.exit(main())