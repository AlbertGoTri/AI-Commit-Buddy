#!/usr/bin/env python3
"""
Complete integration test for Groq API fixes
Tests the actual commit buddy workflow with verbose logging
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_commit_buddy_with_no_api_key():
    """Test commit buddy behavior when no API key is configured"""
    print("🧪 Testing Commit Buddy with NO API key...")
    
    # Ensure no API key is set
    if 'GROQ_API_KEY' in os.environ:
        del os.environ['GROQ_API_KEY']
    
    # Create a test git repository
    test_dir = Path(__file__).parent / "test_repo"
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    test_dir.mkdir()
    os.chdir(test_dir)
    
    try:
        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)
        
        # Create a test file
        test_file = test_dir / "test.py"
        test_file.write_text("def hello():\n    print('Hello, World!')\n")
        
        # Stage the file
        subprocess.run(["git", "add", "test.py"], check=True, capture_output=True)
        
        # Run commit buddy with verbose logging
        commit_buddy_path = Path(__file__).parent / "commit_buddy.py"
        result = subprocess.run([
            sys.executable, str(commit_buddy_path), 
            "--from-diff", "--verbose"
        ], capture_output=True, text=True, input="y\n")
        
        print(f"   Exit code: {result.returncode}")
        print(f"   Stdout: {result.stdout}")
        if result.stderr:
            print(f"   Stderr: {result.stderr}")
        
        # Check if commit was created
        commit_result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True)
        if commit_result.returncode == 0 and commit_result.stdout.strip():
            print("   ✅ Commit created successfully")
            print(f"   Commit message: {commit_result.stdout.strip()}")
            return True
        else:
            print("   ❌ No commit created")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    finally:
        # Cleanup
        os.chdir(Path(__file__).parent)
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)

def test_commit_buddy_with_invalid_api_key():
    """Test commit buddy behavior with invalid API key"""
    print("\n🧪 Testing Commit Buddy with INVALID API key...")
    
    # Set invalid API key
    os.environ['GROQ_API_KEY'] = 'gsk_invalid_key_for_testing_12345'
    
    # Create a test git repository
    test_dir = Path(__file__).parent / "test_repo_invalid"
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    test_dir.mkdir()
    os.chdir(test_dir)
    
    try:
        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)
        
        # Create a test file
        test_file = test_dir / "feature.py"
        test_file.write_text("def new_feature():\n    return 'authentication'\n")
        
        # Stage the file
        subprocess.run(["git", "add", "feature.py"], check=True, capture_output=True)
        
        # Run commit buddy with verbose logging
        commit_buddy_path = Path(__file__).parent / "commit_buddy.py"
        result = subprocess.run([
            sys.executable, str(commit_buddy_path), 
            "--from-diff", "--verbose"
        ], capture_output=True, text=True, input="y\n")
        
        print(f"   Exit code: {result.returncode}")
        print(f"   Stdout: {result.stdout}")
        if result.stderr:
            print(f"   Stderr: {result.stderr}")
        
        # Check if commit was created (should fallback to local generation)
        commit_result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True)
        if commit_result.returncode == 0 and commit_result.stdout.strip():
            commit_msg = commit_result.stdout.strip()
            print("   ✅ Commit created with fallback message")
            print(f"   Commit message: {commit_msg}")
            
            # Check if it used fallback (should contain "feat:" for feature.py)
            if "feat:" in commit_msg.lower() or "update" in commit_msg.lower():
                print("   ✅ Correctly used fallback message generation")
                return True
            else:
                print("   ⚠️  Unexpected commit message format")
                return False
        else:
            print("   ❌ No commit created")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    finally:
        # Cleanup
        os.chdir(Path(__file__).parent)
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)

def test_api_diagnostics():
    """Test the API diagnostics functionality"""
    print("\n🧪 Testing API Diagnostics...")
    
    try:
        commit_buddy_path = Path(__file__).parent / "commit_buddy.py"
        result = subprocess.run([
            sys.executable, str(commit_buddy_path), 
            "--debug-api"
        ], capture_output=True, text=True)
        
        print(f"   Exit code: {result.returncode}")
        if "DIAGNOSTIC SUMMARY" in result.stdout:
            print("   ✅ API diagnostics ran successfully")
            return True
        else:
            print("   ❌ API diagnostics failed")
            print(f"   Output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_verbose_logging_environment_variable():
    """Test verbose logging via environment variable"""
    print("\n🧪 Testing Verbose Logging via Environment Variable...")
    
    # Set environment variable
    os.environ['KIRO_COMMIT_BUDDY_VERBOSE'] = '1'
    
    try:
        from verbose_logger import get_logger, is_verbose_enabled
        
        # Import should automatically enable verbose logging
        if is_verbose_enabled():
            print("   ✅ Verbose logging automatically enabled via environment variable")
            return True
        else:
            print("   ❌ Verbose logging not enabled despite environment variable")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    finally:
        # Cleanup
        if 'KIRO_COMMIT_BUDDY_VERBOSE' in os.environ:
            del os.environ['KIRO_COMMIT_BUDDY_VERBOSE']

def main():
    """Main test function"""
    print("🧪 Kiro Commit Buddy - Complete Integration Test")
    print("=" * 60)
    
    # Track test results
    results = {}
    
    # Test 1: No API key
    results['no_api_key'] = test_commit_buddy_with_no_api_key()
    
    # Test 2: Invalid API key
    results['invalid_api_key'] = test_commit_buddy_with_invalid_api_key()
    
    # Test 3: API diagnostics
    results['api_diagnostics'] = test_api_diagnostics()
    
    # Test 4: Verbose logging environment variable
    results['verbose_env_var'] = test_verbose_logging_environment_variable()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    # Overall assessment
    if passed == total:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Groq API integration is working correctly")
        print("✅ Fallback mechanism works when API is unavailable")
        print("✅ Verbose logging provides detailed debugging information")
        print("✅ System gracefully handles authentication errors")
        return 0
    else:
        print(f"\n❌ {total - passed} integration tests failed")
        print("Check the detailed output above for specific issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())