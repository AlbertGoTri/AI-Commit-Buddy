# Troubleshooting Guide - Kiro Commit Buddy

This guide will help you resolve the most common problems you may encounter when using Kiro Commit Buddy.

## 🔍 Quick diagnosis

Before reviewing specific problems, run these commands to verify your configuration:

```bash
# Verify that you are in a Git repository
git status

# Verify that you have staged changes
git diff --staged

# Verify your API key (Windows PowerShell)
echo $env:GROQ_API_KEY

# Verify your API key (Linux/Mac)
echo $GROQ_API_KEY

# Verify that Python can import dependencies
python -c "import requests, colorama; print('Dependencies OK')"
```

## 🚨 Common problems

### 1. Error: "You are not in a Git repository"

**Symptoms:**
```
Error: You are not in a Git repository
Make sure to run this command from a directory that contains a Git repository.
```

**Possible causes:**
- Running the command outside of a Git repository
- The `.git` directory is corrupted or doesn't exist

**Solutions:**
1. Navigate to your Git repository:
   ```bash
   cd /path/to/your/project
   ```

2. Verify that it's a valid Git repository:
   ```bash
   git status
   ```

3. If it's not a repository, initialize it:
   ```bash
   git init
   ```

### 2. Error: "No staged changes for commit"

**Symptoms:**
```
No staged changes for commit.
Use 'git add <file>' to add changes to the staging area.
```

**Possible causes:**
- You haven't added files to the staging area
- All changes are already committed

**Solutions:**
1. Check the status of your repository:
   ```bash
   git status
   ```

2. Add files to staging:
   ```bash
   git add file1.py file2.js
   # or to add all changes:
   git add .
   ```

3. Verify that you have staged changes:
   ```bash
   git diff --staged
   ```

### 3. Error: "GROQ_API_KEY not configured"

**Symptoms:**
```
GROQ_API_KEY is not configured.
To configure it:
  Windows: set GROQ_API_KEY=your_api_key
  Linux/Mac: export GROQ_API_KEY=your_api_key
```

**Solutions:**

#### Windows (PowerShell):
```powershell
# Temporary (only for current session)
$env:GROQ_API_KEY = "gsk_your_api_key_here"

# Permanent (for current user)
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "gsk_your_api_key_here", "User")

# Verify
echo $env:GROQ_API_KEY
```

#### Windows (CMD):
```cmd
# Temporary
set GROQ_API_KEY=gsk_your_api_key_here

# Permanent: Control Panel > System > Advanced settings > Environment Variables
```

#### Linux/macOS:
```bash
# Temporary
export GROQ_API_KEY="gsk_your_api_key_here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export GROQ_API_KEY="gsk_your_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# Verify
echo $GROQ_API_KEY
```

### 4. Error: "Invalid API key"

**Symptoms:**
```
Authentication error with Groq API
Verify that your GROQ_API_KEY is correct
```

**Possible causes:**
- Incorrect or expired API key
- API key with incorrect format
- Extra spaces in the API key

**Solutions:**
1. Verify your API key format:
   - Must start with `gsk_`
   - Must not contain spaces
   - Must be at least 40 characters long

2. Generate a new API key:
   - Go to [console.groq.com](https://console.groq.com)
   - Navigate to "API Keys"
   - Create a new key
   - Replace the previous one

3. Verify there are no extra spaces:
   ```bash
   # Linux/Mac
   export GROQ_API_KEY="$(echo $GROQ_API_KEY | tr -d ' ')"
   ```

### 5. Error: "Connection timeout"

**Symptoms:**
```
⚠️ API not available, generating basic message...
Error: Connection timeout
```

**Possible causes:**
- Internet connectivity problems
- Firewall blocking the connection
- Groq server temporarily unavailable

**Solutions:**
1. Check your internet connection:
   ```bash
   ping google.com
   ```

2. Verify that you can access Groq:
   ```bash
   curl -I https://api.groq.com
   ```

3. If you're behind a corporate firewall, contact your system administrator

4. The tool will automatically use fallback mode, which continues working

### 6. Error: "ModuleNotFoundError"

**Symptoms:**
```
ModuleNotFoundError: No module named 'requests'
ModuleNotFoundError: No module named 'colorama'
```

**Possible causes:**
- Dependencies not installed
- Using the wrong Python (multiple versions)
- Virtual environment not activated

**Solutions:**
1. Install dependencies:
   ```bash
   pip install -r .kiro/scripts/requirements.txt
   ```

2. If you use multiple Python versions:
   ```bash
   python3 -m pip install -r .kiro/scripts/requirements.txt
   ```

3. If you use a virtual environment:
   ```bash
   # Activate the virtual environment first
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   
   # Then install
   pip install -r .kiro/scripts/requirements.txt
   ```

### 7. Error: "Permission denied"

**Symptoms (Windows):**
```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 8. Generated message is not appropriate

**Symptoms:**
- The message doesn't reflect the changes
- The type prefix is incorrect
- The message is in the wrong language

**Solutions:**
1. Use the edit option:
   ```
   Use this message? (y/n/e to edit): e
   ```

2. Verify that your staged changes are clear:
   ```bash
   git diff --staged
   ```

3. If the problem persists, report the issue with:
   - The diff that caused the problem
   - The generated message
   - The expected message

### 9. Kiro doesn't recognize the command

**Symptoms:**
```
Command not found: commit
```

**Possible causes:**
- The hook file is not in the correct location
- Kiro hasn't reloaded the configuration

**Solutions:**
1. Verify that the hook file exists:
   ```bash
   ls .kiro/hooks/commit.yml
   ```

2. Verify the hook content:
   ```bash
   cat .kiro/hooks/commit.yml
   ```

3. Restart Kiro or reload the configuration

4. Verify that the Python file is executable:
   ```bash
   python .kiro/scripts/commit_buddy.py --help
   ```

## 🔧 Diagnostic tools

### Diagnostic script

Create this script to automatically diagnose problems:

```python
#!/usr/bin/env python3
"""Kiro Commit Buddy Diagnostics"""

import os
import sys
import subprocess
from pathlib import Path

def check_git():
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
        print("✅ Git repository: OK")
        return True
    except:
        print("❌ Git repository: Not found")
        return False

def check_staged_changes():
    try:
        result = subprocess.run(['git', 'diff', '--staged'], capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Staged changes: OK")
            return True
        else:
            print("⚠️  Staged changes: No staged changes")
            return False
    except:
        print("❌ Staged changes: Error verifying")
        return False

def check_api_key():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY: Not configured")
        return False
    
    if not api_key.startswith('gsk_'):
        print("❌ GROQ_API_KEY: Incorrect format (must start with 'gsk_')")
        return False
    
    if len(api_key) < 40:
        print("❌ GROQ_API_KEY: Too short")
        return False
    
    print("✅ GROQ_API_KEY: OK")
    return True

def check_dependencies():
    try:
        import requests
        import colorama
        print("✅ Dependencies: OK")
        return True
    except ImportError as e:
        print(f"❌ Dependencies: {e}")
        return False

def check_files():
    files = [
        '.kiro/hooks/commit.yml',
        '.kiro/scripts/commit_buddy.py',
        '.kiro/scripts/requirements.txt'
    ]
    
    all_ok = True
    for file in files:
        if Path(file).exists():
            print(f"✅ {file}: OK")
        else:
            print(f"❌ {file}: Not found")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print("🔍 Kiro Commit Buddy Diagnostics\n")
    
    checks = [
        check_git(),
        check_staged_changes(),
        check_api_key(),
        check_dependencies(),
        check_files()
    ]
    
    if all(checks):
        print("\n🎉 Everything seems to be configured correctly!")
    else:
        print("\n⚠️  Some problems were found. Review the errors above.")
```

### Debug logs

To get more information about errors, you can temporarily modify the configuration file to enable detailed logs.

## 📞 Get additional help

If none of these solutions work:

1. **Run the diagnostic** using the script above
2. **Gather information**:
   - Operating system and version
   - Python version (`python --version`)
   - Git version (`git --version`)
   - Content of `.kiro/hooks/commit.yml`
   - Complete error message

3. **Search existing issues** in the project repository

4. **Create a new issue** with all the gathered information

## 🔄 Complete reinstallation

If everything else fails, you can do a complete reinstallation:

```bash
# 1. Backup current configuration
cp .kiro/hooks/commit.yml commit.yml.backup

# 2. Clean previous installation
rm -rf .kiro/scripts/__pycache__

# 3. Reinstall dependencies
pip uninstall -y requests colorama
pip install -r .kiro/scripts/requirements.txt

# 4. Verify installation
python .kiro/scripts/commit_buddy.py --help

# 5. Restore configuration
cp commit.yml.backup .kiro/hooks/commit.yml
```