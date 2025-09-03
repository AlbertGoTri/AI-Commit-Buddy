@echo off
REM Kiro Commit Buddy - Windows Wrapper
REM This script provides a direct way to use Kiro Commit Buddy
REM Usage: .kiro/scripts/commit_buddy.bat [options]

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.7 or higher.
    exit /b 1
)

REM Check if we're in a Git repository
git status >nul 2>&1
if errorlevel 1 (
    echo Error: Not in a Git repository. Please run from a Git repository.
    exit /b 1
)

REM Run the commit buddy with all arguments
python commit_buddy.py %*
