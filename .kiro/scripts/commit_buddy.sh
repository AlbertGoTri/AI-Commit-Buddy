#!/bin/bash
# Kiro Commit Buddy - Shell Wrapper
# This script provides a direct way to use Kiro Commit Buddy
# Usage: .kiro/scripts/commit_buddy.sh [options]

cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.7 or higher."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if we're in a Git repository
if ! git status &> /dev/null; then
    echo "Error: Not in a Git repository. Please run from a Git repository."
    exit 1
fi

# Run the commit buddy with all arguments
"$PYTHON_CMD" commit_buddy.py "$@"
