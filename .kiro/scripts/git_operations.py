"""
Git operations module for Kiro Commit Buddy
Handles all Git repository interactions
"""

from typing import List, Optional, Tuple
import subprocess
import os

class GitOperationError(Exception):
    """Custom exception for Git operation errors"""
    pass

class GitOperations:
    """Handles Git repository operations"""

    def __init__(self):
        pass

    def is_git_repository(self) -> bool:
        """Check if current directory is a Git repository"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
        except Exception:
            return False

    def validate_git_environment(self) -> Tuple[bool, str]:
        """
        Validate Git environment and provide detailed error information
        Returns: (is_valid, error_message)
        """
        try:
            # Check if git command is available
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return False, "Git is not installed or not available in PATH"
        except FileNotFoundError:
            return False, "Git is not installed. Please install Git to continue."
        except subprocess.TimeoutExpired:
            return False, "Timeout checking Git installation"
        except Exception as e:
            return False, f"Error checking Git: {str(e)}"

        try:
            # Check if we're in a Git repository
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                # Try to get more specific error information
                if "not a git repository" in result.stderr.lower():
                    return False, "You are not in a Git repository. Run 'git init' or navigate to an existing repository."
                else:
                    return False, f"Git error: {result.stderr.strip() or 'Invalid Git repository'}"
        except subprocess.TimeoutExpired:
            return False, "Timeout checking Git repository"
        except PermissionError:
            return False, "No permissions to access Git repository"
        except Exception as e:
            return False, f"Error checking Git repository: {str(e)}"

        try:
            # Check if we can access the working directory
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return False, f"Cannot access repository status: {result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return False, "Timeout checking repository status"
        except Exception as e:
            return False, f"Error checking repository status: {str(e)}"

        return True, ""

    def get_staged_diff(self) -> str:
        """Get the diff of staged changes"""
        try:
            # First try normal diff
            result = subprocess.run(
                ['git', 'diff', '--staged'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # If the diff contains "Binary files differ", try with --text flag
            if result.returncode == 0:
                diff_output = result.stdout
                
                if "Binary files" in diff_output and "differ" in diff_output:
                    # Force text diff for better analysis
                    result = subprocess.run(
                        ['git', 'diff', '--staged', '--text'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    diff_output = result.stdout
                
                # Clean up null characters and other encoding issues
                diff_output = self._clean_diff_output(diff_output)
                return diff_output
            else:
                raise GitOperationError(f"Error getting diff: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            raise GitOperationError("Timeout getting staged changes diff")
        except FileNotFoundError:
            raise GitOperationError("Git is not available")
        except Exception as e:
            raise GitOperationError(f"Unexpected error getting diff: {str(e)}")
    
    def _clean_diff_output(self, diff: str) -> str:
        """Clean diff output from encoding issues"""
        # Remove null characters that can appear in UTF-16 encoded files
        diff = diff.replace('\x00', '')
        
        # Remove other problematic characters
        diff = diff.replace('\ufeff', '')  # BOM character
        
        # Normalize line endings
        diff = diff.replace('\r\n', '\n').replace('\r', '\n')
        
        return diff

    def check_staged_changes(self) -> Tuple[bool, str, List[str]]:
        """
        Check for staged changes and provide detailed information
        Returns: (has_changes, status_message, changed_files)
        """
        try:
            # Get staged files
            result = subprocess.run(
                ['git', 'diff', '--staged', '--name-only'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return False, f"Error checking staged changes: {result.stderr.strip()}", []

            staged_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]

            if not staged_files:
                # Check if there are unstaged changes
                unstaged_result = subprocess.run(
                    ['git', 'diff', '--name-only'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if unstaged_result.returncode == 0:
                    unstaged_files = [f.strip() for f in unstaged_result.stdout.split('\n') if f.strip()]
                    if unstaged_files:
                        return False, f"No staged changes. There are {len(unstaged_files)} modified file(s) not staged. Use 'git add' to stage changes.", unstaged_files
                    else:
                        return False, "No changes to commit. Working directory is clean.", []
                else:
                    return False, "No staged changes for commit. Use 'git add <file>' to stage changes.", []

            return True, f"Found {len(staged_files)} file(s) staged for commit", staged_files

        except subprocess.TimeoutExpired:
            return False, "Timeout checking staged changes", []
        except Exception as e:
            return False, f"Error checking changes: {str(e)}", []

    def get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--staged', '--name-only'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                return [f for f in files if f]  # Filter out empty strings
            return []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def commit_with_message(self, message: str) -> Tuple[bool, str]:
        """
        Execute git commit with the provided message
        Returns: (success, error_message_or_commit_hash)
        """
        if not message or not message.strip():
            return False, "Commit message cannot be empty"

        try:
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0:
                # Try to get the commit hash
                try:
                    hash_result = subprocess.run(
                        ['git', 'rev-parse', 'HEAD'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if hash_result.returncode == 0:
                        commit_hash = hash_result.stdout.strip()[:8]  # Short hash
                        return True, commit_hash
                    else:
                        return True, "commit created successfully"
                except:
                    return True, "commit created successfully"
            else:
                # Parse common Git commit errors
                error_msg = result.stderr.strip()
                if "nothing to commit" in error_msg.lower():
                    return False, "No staged changes for commit"
                elif "please tell me who you are" in error_msg.lower():
                    return False, "Incomplete Git configuration. Run:\ngit config --global user.email 'your@email.com'\ngit config --global user.name 'Your Name'"
                elif "pathspec" in error_msg.lower():
                    return False, "Error in files specified for commit"
                elif "lock" in error_msg.lower():
                    return False, "Repository is locked. Try again in a few seconds."
                else:
                    return False, f"Error executing commit: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Timeout executing commit. The process took too long."
        except FileNotFoundError:
            return False, "Git is not available"
        except Exception as e:
            return False, f"Unexpected error executing commit: {str(e)}"
