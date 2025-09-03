"""
API Debugger for Kiro Commit Buddy
Comprehensive diagnostic tools for Groq API integration
"""

import os
import sys
import json
import requests
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from groq_client import GroqClient, GroqAPIError

class APIDebugger:
    """Comprehensive API debugging utilities"""

    def __init__(self):
        self.config = Config()
        self.verbose = False

    def set_verbose(self, verbose: bool = True):
        """Enable verbose logging"""
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")

    def validate_api_key(self) -> Tuple[bool, str]:
        """
        Validate API key configuration and format
        Returns: (is_valid, detailed_message)
        """
        self.log("Starting API key validation...")

        # Check if environment variable exists
        raw_key = os.getenv("GROQ_API_KEY")
        if raw_key is None:
            return False, "GROQ_API_KEY environment variable is not set"

        self.log(f"Raw API key found: {raw_key[:10]}..." if len(raw_key) > 10 else f"Raw API key: {raw_key}")

        # Check if key is empty or whitespace
        if not raw_key.strip():
            return False, "GROQ_API_KEY is empty or contains only whitespace"

        # Use config validation
        is_valid, error_msg = self.config.validate_api_key_format()
        if not is_valid:
            return False, f"API key format validation failed: {error_msg}"

        self.log("API key format validation passed")
        return True, "API key is properly configured and formatted"

    def test_api_connectivity(self) -> Tuple[bool, str]:
        """
        Test basic connectivity to Groq API
        Returns: (is_connected, detailed_message)
        """
        self.log("Testing API connectivity...")

        try:
            # Validate API key first
            is_valid, key_msg = self.validate_api_key()
            if not is_valid:
                return False, f"API key validation failed: {key_msg}"

            # Test basic connectivity with minimal request
            headers = self.config.get_api_headers()
            self.log(f"Using endpoint: {self.config.GROQ_ENDPOINT}")
            self.log(f"Headers: {json.dumps({k: v[:20] + '...' if k == 'Authorization' else v for k, v in headers.items()}, indent=2)}")

            test_payload = {
                "model": self.config.GROQ_MODEL,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
                "temperature": 0.1
            }

            self.log(f"Test payload: {json.dumps(test_payload, indent=2)}")

            response = requests.post(
                self.config.GROQ_ENDPOINT,
                headers=headers,
                json=test_payload,
                timeout=self.config.TIMEOUT
            )

            self.log(f"Response status: {response.status_code}")
            self.log(f"Response headers: {dict(response.headers)}")

            if response.status_code == 200:
                return True, "API connectivity test successful"
            elif response.status_code == 401:
                return False, "Authentication failed - invalid API key"
            elif response.status_code == 429:
                return False, "Rate limit exceeded - API is accessible but throttled"
            elif response.status_code == 500:
                return False, "Server error - API is accessible but experiencing issues"
            else:
                try:
                    error_data = response.json()
                    self.log(f"Error response: {json.dumps(error_data, indent=2)}")
                    return False, f"API returned status {response.status_code}: {error_data}"
                except:
                    return False, f"API returned status {response.status_code}: {response.text[:200]}"

        except requests.exceptions.ConnectionError as e:
            return False, f"Connection error: {str(e)}"
        except requests.exceptions.Timeout as e:
            return False, f"Timeout error: {str(e)}"
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def test_sample_api_call(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Test a complete API call with sample diff
        Returns: (success, message, debug_info)
        """
        self.log("Testing sample API call...")

        debug_info = {
            "api_key_valid": False,
            "connectivity_ok": False,
            "api_call_success": False,
            "response_data": None,
            "error_details": None
        }

        try:
            # Step 1: Validate API key
            is_valid, key_msg = self.validate_api_key()
            debug_info["api_key_valid"] = is_valid
            if not is_valid:
                debug_info["error_details"] = key_msg
                return False, f"API key validation failed: {key_msg}", debug_info

            # Step 2: Test connectivity
            is_connected, conn_msg = self.test_api_connectivity()
            debug_info["connectivity_ok"] = is_connected
            if not is_connected:
                debug_info["error_details"] = conn_msg
                return False, f"Connectivity test failed: {conn_msg}", debug_info

            # Step 3: Test actual commit message generation
            sample_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
     print("Hello, World!")
+    print("This is a test change")
"""

            self.log("Creating Groq client...")
            groq_client = GroqClient(self.config)

            self.log("Generating commit message...")
            commit_message = groq_client.generate_commit_message(sample_diff)

            debug_info["api_call_success"] = True
            debug_info["response_data"] = {"commit_message": commit_message}

            self.log(f"Generated message: {commit_message}")
            return True, f"Sample API call successful. Generated message: '{commit_message}'", debug_info

        except GroqAPIError as e:
            debug_info["error_details"] = str(e)
            return False, f"Groq API error: {str(e)}", debug_info
        except Exception as e:
            debug_info["error_details"] = str(e)
            return False, f"Unexpected error: {str(e)}", debug_info

    def debug_fallback_triggers(self) -> Dict[str, Any]:
        """
        Debug why fallback messages are being triggered
        Returns: Dictionary with debugging information
        """
        self.log("Debugging fallback triggers...")

        debug_info = {
            "api_key_configured": False,
            "api_key_valid": False,
            "groq_client_initialized": False,
            "api_available": False,
            "sample_call_works": False,
            "fallback_reasons": []
        }

        # Check API key configuration
        debug_info["api_key_configured"] = self.config.has_groq_api_key()
        if not debug_info["api_key_configured"]:
            debug_info["fallback_reasons"].append("GROQ_API_KEY not configured")

        # Check API key validity
        if debug_info["api_key_configured"]:
            is_valid, _ = self.validate_api_key()
            debug_info["api_key_valid"] = is_valid
            if not is_valid:
                debug_info["fallback_reasons"].append("API key format is invalid")

        # Try to initialize Groq client
        if debug_info["api_key_valid"]:
            try:
                groq_client = GroqClient(self.config)
                debug_info["groq_client_initialized"] = True
                self.log("Groq client initialized successfully")

                # Test API availability
                debug_info["api_available"] = groq_client.is_api_available()
                if not debug_info["api_available"]:
                    debug_info["fallback_reasons"].append("API is not available (network/server issues)")

                # Test sample call
                if debug_info["api_available"]:
                    try:
                        sample_diff = "diff --git a/test.py b/test.py\n+print('test')"
                        message = groq_client.generate_commit_message(sample_diff)
                        debug_info["sample_call_works"] = True
                        debug_info["sample_message"] = message
                        self.log(f"Sample call successful: {message}")
                    except Exception as e:
                        debug_info["fallback_reasons"].append(f"Sample API call failed: {str(e)}")

            except GroqAPIError as e:
                debug_info["fallback_reasons"].append(f"Groq client initialization failed: {str(e)}")
            except Exception as e:
                debug_info["fallback_reasons"].append(f"Unexpected error initializing client: {str(e)}")

        return debug_info

    def run_comprehensive_diagnostic(self) -> Dict[str, Any]:
        """
        Run all diagnostic tests and return comprehensive report
        Returns: Complete diagnostic report
        """
        print("🔍 Running comprehensive API diagnostic...")
        print("=" * 50)

        report = {
            "timestamp": str(os.popen("date").read().strip()) if os.name != 'nt' else str(os.popen("echo %date% %time%").read().strip()),
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "groq_api_key_set": bool(os.getenv("GROQ_API_KEY"))
            },
            "tests": {}
        }

        # Test 1: API Key Validation
        print("\n1. Testing API Key Configuration...")
        is_valid, msg = self.validate_api_key()
        report["tests"]["api_key_validation"] = {"success": is_valid, "message": msg}
        print(f"   {'✅' if is_valid else '❌'} {msg}")

        # Test 2: API Connectivity
        print("\n2. Testing API Connectivity...")
        is_connected, msg = self.test_api_connectivity()
        report["tests"]["api_connectivity"] = {"success": is_connected, "message": msg}
        print(f"   {'✅' if is_connected else '❌'} {msg}")

        # Test 3: Sample API Call
        print("\n3. Testing Sample API Call...")
        success, msg, debug_info = self.test_sample_api_call()
        report["tests"]["sample_api_call"] = {"success": success, "message": msg, "debug_info": debug_info}
        print(f"   {'✅' if success else '❌'} {msg}")

        # Test 4: Fallback Analysis
        print("\n4. Analyzing Fallback Triggers...")
        fallback_info = self.debug_fallback_triggers()
        report["tests"]["fallback_analysis"] = fallback_info
        
        if not fallback_info["fallback_reasons"]:
            print("   ✅ No fallback triggers detected - API should work properly")
        else:
            print("   ❌ Fallback triggers detected:")
            for reason in fallback_info["fallback_reasons"]:
                print(f"      - {reason}")

        # Summary
        print("\n" + "=" * 50)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 50)

        all_tests_passed = all(test["success"] for test in report["tests"].values() if isinstance(test, dict) and "success" in test)
        
        if all_tests_passed and not fallback_info["fallback_reasons"]:
            print("✅ All tests passed! API integration should work correctly.")
        else:
            print("❌ Issues detected. API will likely use fallback messages.")
            print("\n🔧 RECOMMENDED ACTIONS:")
            
            if not report["tests"]["api_key_validation"]["success"]:
                print("   1. Configure GROQ_API_KEY environment variable")
                print("      - Get your API key from: https://console.groq.com/keys")
                print("      - Windows: set GROQ_API_KEY=your_key_here")
                print("      - Linux/Mac: export GROQ_API_KEY=your_key_here")
            
            if not report["tests"]["api_connectivity"]["success"]:
                print("   2. Check network connectivity and firewall settings")
                print("   3. Verify API key is valid and not expired")
            
            if fallback_info["fallback_reasons"]:
                print("   4. Address specific fallback triggers listed above")

        return report

def main():
    """Main function for running diagnostics"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Groq API Debugger for Kiro Commit Buddy")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--test", choices=["key", "connectivity", "sample", "fallback", "all"], 
                       default="all", help="Specific test to run")
    
    args = parser.parse_args()
    
    debugger = APIDebugger()
    debugger.set_verbose(args.verbose)
    
    if args.test == "key":
        success, msg = debugger.validate_api_key()
        print(f"API Key Validation: {'✅' if success else '❌'} {msg}")
    elif args.test == "connectivity":
        success, msg = debugger.test_api_connectivity()
        print(f"API Connectivity: {'✅' if success else '❌'} {msg}")
    elif args.test == "sample":
        success, msg, debug_info = debugger.test_sample_api_call()
        print(f"Sample API Call: {'✅' if success else '❌'} {msg}")
        if args.verbose:
            print(f"Debug Info: {json.dumps(debug_info, indent=2)}")
    elif args.test == "fallback":
        fallback_info = debugger.debug_fallback_triggers()
        print(f"Fallback Analysis: {json.dumps(fallback_info, indent=2)}")
    else:
        debugger.run_comprehensive_diagnostic()

if __name__ == "__main__":
    main()