# Installation Guide - Kiro Commit Buddy

This guide will take you step by step through the installation and configuration process of Kiro Commit Buddy.

## ❓ Frequently Asked Questions about Installation

### Do I need to create a GitHub repository?
**It's not necessary.** The code already works perfectly on your local machine. If you want to share it or make backups:
- You can create your own repository: `https://github.com/YOUR_USERNAME/kiro-commit-buddy.git`
- Or simply use it locally

### What is a Kiro workspace?
A **Kiro workspace** is any directory that contains a `.kiro/` folder. It's like `.git/` for Git - it simply marks that the directory uses Kiro.

### Does it only work in Kiro projects?
**No!** It works in **any Git repository**, whether it has Kiro or not:
- **Command**: `python .kiro/scripts/commit_buddy.py --from-diff`

### How to use in other projects?
Simply copy the `.kiro/` folder to any other Git repository and it will work there too.

## 📋 Prerequisites

Before starting, make sure you have installed:

### Required requirements
- **Python 3.7 or higher** ([Download Python](https://www.python.org/downloads/))
- **Git** ([Download Git](https://git-scm.com/downloads))
- **Kiro IDE** (must be installed and working)

### Optional requirements
- **Groq account** for AI functionality ([Sign up for Groq](https://console.groq.com))

## 🚀 Step-by-step installation

### Step 1: Verify prerequisites

Open your terminal and verify that you have everything installed:

```bash
# Verify Python
python --version
# Should show: Python 3.7.x or higher

# Verify Git
git --version
# Should show: git version x.x.x

# Verify pip
pip --version
# Should show: pip x.x.x
```

### Step 2: Prepare the project

1. **Navigate to your Kiro workspace:**
   ```bash
   cd /path/to/your/workspace
   ```

2. **Verify that you are in a Git repository:**
   ```bash
   git status
   ```
   
   If it's not a Git repository, initialize it:
   ```bash
   git init
   ```

### Step 3: Install Kiro Commit Buddy

#### Option A: You already have the code

**If you already have these files in your project, you don't need to do anything else!** 
Kiro Commit Buddy is already installed and ready to use.

```bash
# Verify that you have the files
ls .kiro/hooks/commit.yml
ls .kiro/scripts/commit_buddy.py

# Install dependencies if you haven't done so
pip install -r .kiro/scripts/requirements.txt
```

#### Option B: Clone from repository

If you want to get the code from a repository:

```bash
# If the repository exists (you can create your own)
git clone https://github.com/YOUR_USERNAME/kiro-commit-buddy.git
cd kiro-commit-buddy

# Install using setup.py
pip install -e .
```

#### Option C: Manual installation

If you have the project files:

1. **Create the directory structure:**
   ```bash
   mkdir -p .kiro/hooks
   mkdir -p .kiro/scripts
   ```

2. **Copy the project files** to the correct locations:
   - Python files → `.kiro/scripts/`
   - Hook file → `.kiro/hooks/commit.yml`

3. **Install dependencies:**
   ```bash
   pip install -r .kiro/scripts/requirements.txt
   ```

### Step 4: Configure Groq API

#### 4.1 Get API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Create an account or sign in
3. Navigate to "API Keys" in the side panel
4. Click on "Create API Key"
5. Give your key a name (e.g.: "Kiro Commit Buddy")
6. Copy the generated API key (starts with `gsk_`)

#### 4.2 Configure the API Key

**Windows (PowerShell):**
```powershell
# Temporary configuration (only for this session)
$env:GROQ_API_KEY = "gsk_your_api_key_here"

# Permanent configuration
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "gsk_your_api_key_here", "User")

# Verify configuration
echo $env:GROQ_API_KEY
```

**Windows (CMD):**
```cmd
# Temporary configuration
set GROQ_API_KEY=gsk_your_api_key_here

# For permanent configuration:
# 1. Control Panel > System > Advanced system settings
# 2. Environment Variables > User variables > New
# 3. Name: GROQ_API_KEY
# 4. Value: gsk_your_api_key_here
```

**macOS/Linux:**
```bash
# Temporary configuration
export GROQ_API_KEY="gsk_your_api_key_here"

# Permanent configuration
echo 'export GROQ_API_KEY="gsk_your_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# For zsh users
echo 'export GROQ_API_KEY="gsk_your_api_key_here"' >> ~/.zshrc
source ~/.zshrc

# Verify configuration
echo $GROQ_API_KEY
```

### Step 5: Verify the installation

1. **Verify that the files are in place:**
   ```bash
   ls .kiro/hooks/commit.yml
   ls .kiro/scripts/commit_buddy.py
   ls .kiro/scripts/requirements.txt
   ```

2. **Test the script directly:**
   ```bash
   python .kiro/scripts/commit_buddy.py --help
   ```
   
   You should see the command help.

3. **Test with Kiro:**
   ```bash
   # Make some changes and add them to staging
   echo "test" > test.txt
   git add test.txt
   
   # Test the command
   python .kiro/scripts/commit_buddy.py --from-diff
   ```

### Step 6: Advanced configuration (Optional)

#### Customize configuration

You can create a `.env` file in your project root for additional configurations:

```bash
# .env
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama3-70b-8192
MAX_DIFF_SIZE=8000
TIMEOUT=10
```

#### Configure for multiple projects

If you want to use Kiro Commit Buddy in multiple projects:

1. **Install globally:**
   ```bash
   pip install -e . --user
   ```

2. **Copy the configuration to each project:**
   ```bash
   cp .kiro/hooks/commit.yml /other/project/.kiro/hooks/
   cp -r .kiro/scripts /other/project/.kiro/
   ```

## 🔧 System-specific configurations

### Windows with WSL

If you use Windows Subsystem for Linux:

```bash
# In WSL
export GROQ_API_KEY="gsk_your_api_key_here"

# To persist between sessions
echo 'export GROQ_API_KEY="gsk_your_api_key_here"' >> ~/.bashrc
```

### macOS with Homebrew

If you installed Python with Homebrew:

```bash
# Use python3 explicitly
python3 -m pip install -r .kiro/scripts/requirements.txt

# Verify it uses the correct version
which python3
python3 --version
```

### Linux with multiple Python versions

```bash
# Use a specific version
python3.9 -m pip install -r .kiro/scripts/requirements.txt

# Create an alias if necessary
echo 'alias python=python3.9' >> ~/.bashrc
```

## 🧪 Complete verification

Run this verification script to make sure everything is configured correctly:

```bash
# Create verification script
cat > verify_installation.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def verify_installation():
    print("🔍 Verifying Kiro Commit Buddy installation...\n")
    
    # Verify Python
    print(f"✅ Python: {sys.version}")
    
    # Verify Git
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        print(f"✅ Git: {result.stdout.strip()}")
    except:
        print("❌ Git: Not found")
        return False
    
    # Verify files
    files = [
        '.kiro/hooks/commit.yml',
        '.kiro/scripts/commit_buddy.py',
        '.kiro/scripts/requirements.txt'
    ]
    
    for file in files:
        if Path(file).exists():
            print(f"✅ {file}: Exists")
        else:
            print(f"❌ {file}: Not found")
            return False
    
    # Verify dependencies
    try:
        import requests
        import colorama
        print("✅ Dependencies: Installed")
    except ImportError as e:
        print(f"❌ Dependencies: {e}")
        return False
    
    # Verify API key
    api_key = os.getenv('GROQ_API_KEY')
    if api_key and api_key.startswith('gsk_'):
        print("✅ GROQ_API_KEY: Configured")
    else:
        print("⚠️  GROQ_API_KEY: Not configured (limited AI functionality)")
    
    # Verify that the script works
    try:
        result = subprocess.run([
            sys.executable, '.kiro/scripts/commit_buddy.py', '--help'
        ], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Script: Functional")
        else:
            print("❌ Script: Error executing")
            return False
    except:
        print("❌ Script: Cannot execute")
        return False
    
    print("\n🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Make some changes to your code")
    print("2. Add them to staging: git add .")
    print("3. Run: python .kiro/scripts/commit_buddy.py --from-diff")
    
    return True

if __name__ == "__main__":
    verify_installation()
EOF

# Run verification
python verify_installation.py
```

## 🆘 Installation troubleshooting

### Error: "pip not found"

```bash
# Windows
python -m ensurepip --upgrade

# macOS
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3-pip
```

### Error: "Permission denied"

```bash
# Use --user to install only for your user
pip install --user -r .kiro/scripts/requirements.txt

# Or use a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r .kiro/scripts/requirements.txt
```

### Error: "Command not found: kiro"

1. Verify that Kiro IDE is installed and working
2. Restart Kiro IDE
3. Verify that the `.kiro/hooks/commit.yml` file exists
4. Try running directly: `python .kiro/scripts/commit_buddy.py --from-diff`

## 📞 Get help

If you encounter problems during installation:

1. Review the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Run the verification script above
3. Search in the repository issues
4. Create a new issue with:
   - Your operating system
   - Python version
   - Complete error message
   - Steps you followed

Welcome to Kiro Commit Buddy! 🎉