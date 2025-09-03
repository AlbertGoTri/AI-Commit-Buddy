#!/usr/bin/env python3
"""
Test script for Kiro integration
Validates hook configuration and command execution
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path

def test_hook_configuration():
    """Test that the Kiro hook configuration is properly set up"""
    print("🔍 Testing Kiro hook configuration...")
    
    hook_file = Path(".kiro/hooks/commit.yml")
    
    # Check if hook file exists
    if not hook_file.exists():
        print("❌ Hook configuration file not found at .kiro/hooks/commit.yml")
        return False
    
    # Load and validate hook configuration
    try:
        with open(hook_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ['name', 'description', 'command', 'args', 'triggers']
        for field in required_fields:
            if field not in config:
                print(f"❌ Missing required field '{field}' in hook configuration")
                return False
        
        # Validate specific values
        if config['name'] != "Commit Buddy":
            print(f"❌ Expected name 'Commit Buddy', got '{config['name']}'")
            return False
        
        if config['command'] != "python .kiro/scripts/commit_buddy.py":
            print(f"❌ Expected command 'python .kiro/scripts/commit_buddy.py', got '{config['command']}'")
            return False
        
        if "--from-diff" not in config['args']:
            print(f"❌ Expected '--from-diff' in args, got {config['args']}")
            return False
        
        if "manual" not in config['triggers']:
            print(f"❌ Expected 'manual' in triggers, got {config['triggers']}")
            return False
        
        print("✅ Hook configuration is valid")
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ Error parsing hook configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading hook configuration: {e}")
        return False

def test_command_registration():
    """Test that the command is properly registered and executable"""
    print("🔍 Testing command registration...")
    
    script_path = Path(".kiro/scripts/commit_buddy.py")
    
    # Check if script exists
    if not script_path.exists():
        print("❌ Main script not found at .kiro/scripts/commit_buddy.py")
        return False
    
    # Test script execution with --help
    try:
        result = subprocess.run([
            sys.executable, str(script_path), "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ Script failed with exit code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
        
        # Check if help output contains expected content
        help_output = result.stdout
        if "--from-diff" not in help_output:
            print("❌ --from-diff option not found in help output")
            return False
        
        if "AI-powered commit message generator" not in help_output:
            print("❌ Expected description not found in help output")
            return False
        
        print("✅ Command registration is working")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Command execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing command execution: {e}")
        return False

def test_from_diff_execution():
    """Test that --from-diff command executes without errors"""
    print("🔍 Testing --from-diff execution...")
    
    script_path = Path(".kiro/scripts/commit_buddy.py")
    
    try:
        result = subprocess.run([
            sys.executable, str(script_path), "--from-diff"
        ], capture_output=True, text=True, timeout=15)
        
        # The command should exit with code 0 (no staged changes) or 1 (not a git repo)
        # Both are acceptable for this test
        if result.returncode not in [0, 1]:
            print(f"❌ Unexpected exit code {result.returncode}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            return False
        
        # Check for expected output patterns
        output = result.stdout + result.stderr
        expected_patterns = [
            "No hay cambios staged",  # No staged changes
            "No estás en un repositorio Git",  # Not a git repo
            "Error inesperado"  # Unexpected error (should not happen)
        ]
        
        found_expected = any(pattern in output for pattern in expected_patterns[:2])  # Only first two are acceptable
        
        if not found_expected:
            print(f"❌ Unexpected output: {output}")
            return False
        
        print("✅ --from-diff execution is working")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ --from-diff execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing --from-diff execution: {e}")
        return False

def test_directory_structure():
    """Test that all required files are in place"""
    print("🔍 Testing directory structure...")
    
    required_files = [
        ".kiro/hooks/commit.yml",
        ".kiro/scripts/commit_buddy.py",
        ".kiro/scripts/config.py",
        ".kiro/scripts/git_operations.py",
        ".kiro/scripts/groq_client.py",
        ".kiro/scripts/message_generator.py",
        ".kiro/scripts/user_interface.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files are present")
    return True

def main():
    """Run all integration tests"""
    print("🚀 Starting Kiro integration tests...\n")
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Hook Configuration", test_hook_configuration),
        ("Command Registration", test_command_registration),
        ("--from-diff Execution", test_from_diff_execution)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Kiro integration tests passed!")
        return 0
    else:
        print("💥 Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())