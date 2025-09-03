#!/usr/bin/env python3
"""
Test Kiro Command Integration
Validates that the Kiro command works end-to-end
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def test_kiro_command_integration():
    """Test the complete Kiro command integration"""
    print("🧪 Testing Kiro Command Integration")
    print("=" * 50)
    
    original_cwd = os.getcwd()
    temp_repo = None
    
    try:
        # Create temporary Git repository
        temp_repo = tempfile.mkdtemp()
        os.chdir(temp_repo)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], capture_output=True, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], capture_output=True, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], capture_output=True, check=True)
        
        # Create initial commit
        with open('README.md', 'w') as f:
            f.write('# Test Repository\n')
        subprocess.run(['git', 'add', 'README.md'], capture_output=True, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], capture_output=True, check=True)
        
        # Copy Kiro structure to temp repo
        kiro_source = Path(original_cwd) / '.kiro'
        kiro_dest = Path(temp_repo) / '.kiro'
        shutil.copytree(kiro_source, kiro_dest)
        
        print("✅ Test repository set up")
        
        # Test 1: No staged changes
        print("\n🧪 Test 1: No staged changes")
        result = subprocess.run([
            'python', '.kiro/scripts/commit_buddy.py', '--from-diff'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and 'No hay cambios' in result.stdout:
            print("✅ Correctly handled no staged changes")
        else:
            print(f"❌ Failed no staged changes test: {result.stdout}")
            return False
        
        # Test 2: With staged changes (cancel)
        print("\n🧪 Test 2: With staged changes (user cancels)")
        with open('test_file.py', 'w') as f:
            f.write('def test():\n    return True\n')
        subprocess.run(['git', 'add', 'test_file.py'], capture_output=True, check=True)
        
        result = subprocess.run([
            'python', '.kiro/scripts/commit_buddy.py', '--from-diff'
        ], capture_output=True, text=True, input='n\n')
        
        if result.returncode == 0 and 'cancelado' in result.stdout:
            print("✅ Correctly handled user cancellation")
        else:
            print(f"❌ Failed cancellation test: {result.stdout}")
            return False
        
        # Test 3: With staged changes (accept)
        print("\n🧪 Test 3: With staged changes (user accepts)")
        result = subprocess.run([
            'python', '.kiro/scripts/commit_buddy.py', '--from-diff'
        ], capture_output=True, text=True, input='y\n')
        
        if result.returncode == 0 and 'Commit' in result.stdout and 'creado' in result.stdout:
            print("✅ Successfully created commit")
        else:
            print(f"❌ Failed commit creation test: {result.stdout}")
            return False
        
        # Test 4: Help message
        print("\n🧪 Test 4: Help message")
        result = subprocess.run([
            'python', '.kiro/scripts/commit_buddy.py', '--help'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and 'AI-powered commit message generator' in result.stdout:
            print("✅ Help message works correctly")
        else:
            print(f"❌ Failed help test: {result.stdout}")
            return False
        
        # Test 5: Invalid Git repository
        print("\n🧪 Test 5: Invalid Git repository")
        invalid_repo = tempfile.mkdtemp()
        os.chdir(invalid_repo)
        
        # Copy just the script
        script_source = Path(original_cwd) / '.kiro' / 'scripts'
        script_dest = Path(invalid_repo) / '.kiro' / 'scripts'
        script_dest.parent.mkdir(exist_ok=True)
        shutil.copytree(script_source, script_dest)
        
        result = subprocess.run([
            'python', '.kiro/scripts/commit_buddy.py', '--from-diff'
        ], capture_output=True, text=True)
        
        if result.returncode == 1 and 'repositorio Git' in result.stdout:
            print("✅ Correctly handled invalid Git repository")
        else:
            print(f"❌ Failed invalid repo test: {result.stdout}")
            return False
        
        print("\n🎉 All Kiro command integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
        
    finally:
        # Cleanup
        os.chdir(original_cwd)
        if temp_repo and os.path.exists(temp_repo):
            try:
                def handle_remove_readonly(func, path, exc):
                    import stat
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                
                shutil.rmtree(temp_repo, onerror=handle_remove_readonly)
            except Exception as e:
                print(f"Warning: Could not clean up temp repo: {e}")

if __name__ == "__main__":
    success = test_kiro_command_integration()
    sys.exit(0 if success else 1)