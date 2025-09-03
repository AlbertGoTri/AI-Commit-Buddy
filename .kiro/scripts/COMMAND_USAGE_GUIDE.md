# Kiro Commit Buddy - Command Usage Guide

## Issue Summary

The `kiro commit --from-diff` command shows a warning because Kiro's hook system 
in version 0.2.13 doesn't recognize the custom command registration properly.

**Warning shown:** "Warning: 'from-diff' is not in the list of known options"

## Root Cause

Kiro interprets `commit` as a filename to open rather than a registered hook command.
The `.kiro/hooks/commit.yml` configuration is not being recognized by Kiro's command system.

## Solutions (Choose One)

### 1. Direct Script Execution (Recommended)

```bash
# Instead of: kiro commit --from-diff
# Use this:
python .kiro/scripts/commit_buddy.py --from-diff
```

This is the most reliable method and works identically to the intended Kiro command.

### 2. Wrapper Scripts

**Windows:**
```cmd
.kiro/scripts/commit_buddy.bat --from-diff
```

**Linux/macOS:**
```bash
.kiro/scripts/commit_buddy.sh --from-diff
```

### 3. PowerShell Aliases (Windows)

```powershell
# Load the aliases (run once per session)
. .kiro/scripts/setup_aliases.ps1

# Then use:
kcommit -FromDiff
```

### 4. Shell Aliases (Linux/macOS)

```bash
# Add to ~/.bashrc or ~/.zshrc
alias kcommit='python .kiro/scripts/commit_buddy.py --from-diff'

# Then use:
kcommit
```

### 5. Direct Alias Script

```bash
python .kiro/scripts/kiro-commit.py
```

## Functionality Status

✅ **Working perfectly:**
- AI-powered commit message generation
- Groq API integration
- Fallback message generation
- Git operations
- User interface
- All core features

⚠️ **Only issue:**
- Kiro hook command recognition

## Recommended Workflow

1. **Make changes to your code**
2. **Stage changes:** `git add .`
3. **Generate commit:** `python .kiro/scripts/commit_buddy.py --from-diff`
4. **Review and confirm the generated message**

## Future Resolution

This issue may be resolved in future versions of Kiro when the hook system
is updated to properly recognize custom command registrations.

## Need Help?

If you encounter any issues with the workarounds:
1. Ensure Python 3.7+ is installed
2. Ensure you're in a Git repository
3. Ensure you have staged changes (`git status`)
4. Check that all dependencies are installed (`pip install -r .kiro/scripts/requirements.txt`)
