#!/usr/bin/env python3
"""
Direct command alias for Kiro Commit Buddy
Usage: python .kiro/scripts/kiro-commit.py
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main commit buddy
from commit_buddy import CommitBuddy

if __name__ == "__main__":
    buddy = CommitBuddy()
    # Always use --from-diff for this alias
    sys.exit(buddy.main(["--from-diff"]))
