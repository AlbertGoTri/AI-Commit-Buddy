#!/usr/bin/env python3
"""
Kiro Commit Buddy - AI-powered commit message generator
Main CLI entry point
"""

import sys
import os
import argparse
from pathlib import Path

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from git_operations import GitOperations, GitOperationError
from groq_client import GroqClient, GroqAPIError
from message_generator import MessageGenerator
from user_interface import UserInterface
from verbose_logger import get_logger, enable_verbose_logging

class CommitBuddy:
    """Main CLI handler for Kiro Commit Buddy"""

    def __init__(self):
        self.config = Config()
        self.git_ops = GitOperations()
        self.ui = UserInterface()
        self.logger = get_logger()

    def main(self, args=None):
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="AI-powered commit message generator for Kiro"
        )
        parser.add_argument(
            "--from-diff",
            action="store_true",
            help="Generate commit message from staged changes"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose logging for debugging"
        )
        parser.add_argument(
            "--debug-api",
            action="store_true",
            help="Run API diagnostics instead of generating commit"
        )
        parser.add_argument(
            "--detailed",
            action="store_true",
            help="Generate detailed multi-line commit messages with file breakdown"
        )
        parser.add_argument(
            "--simple",
            action="store_true",
            help="Generate simple single-line commit messages"
        )

        parsed_args = parser.parse_args(args)

        # Enable verbose logging if requested
        if parsed_args.verbose or os.getenv("KIRO_COMMIT_BUDDY_VERBOSE"):
            enable_verbose_logging()
            self.logger.info("Verbose logging enabled", "MAIN")

        if parsed_args.debug_api:
            return self.run_api_diagnostics()
        elif parsed_args.from_diff:
            return self.handle_from_diff()
        else:
            parser.print_help()
            return 0

    def run_api_diagnostics(self):
        """Run comprehensive API diagnostics"""
        try:
            from api_debugger import APIDebugger
            debugger = APIDebugger()
            debugger.set_verbose(True)
            debugger.run_comprehensive_diagnostic()
            return 0
        except ImportError:
            self.ui.show_error("API debugger not available. Please ensure api_debugger.py is present.")
            return 1
        except Exception as e:
            self.ui.show_error(f"Error running diagnostics: {str(e)}")
            return 1

    def handle_from_diff(self):
        """Handle the --from-diff command"""
        self.logger.info("Starting commit message generation from diff", "MAIN")
        
        try:
            # Step 1: Comprehensive Git environment validation
            is_valid, error_msg = self.git_ops.validate_git_environment()
            if not is_valid:
                self.ui.show_error(error_msg)
                return 1

            # Step 2: Check for staged changes with detailed feedback
            has_changes, status_msg, changed_files = self.git_ops.check_staged_changes()
            if not has_changes:
                if status_msg and "not staged" in status_msg:
                    self.ui.show_warning(status_msg)
                    self.ui.show_info("Suggestion: Use 'git add <file>' to stage specific changes or 'git add .' to stage all changes.")
                else:
                    self.ui.show_info(status_msg or "No staged changes found")
                return 0

            self.ui.show_info(status_msg)

            # Step 3: Get staged diff with error handling
            try:
                staged_diff = self.git_ops.get_staged_diff()
            except GitOperationError as e:
                self.ui.show_error(f"Error getting diff: {str(e)}")
                return 1

            # Step 4: Show diff summary to user
            self.ui.show_diff_summary(changed_files)

            # Step 5: Generate commit message with comprehensive error handling
            message_generator = MessageGenerator(self.config)

            try:
                commit_message = message_generator.generate_message(staged_diff, changed_files)
            except GroqAPIError as e:
                self.ui.show_warning(f"API error: {str(e)}")
                self.ui.show_info("Using local message generation...")
                commit_message = message_generator.generate_fallback_message(changed_files)
            except Exception as e:
                self.ui.show_warning(f"Error generating message: {str(e)}")
                self.ui.show_info("Using fallback message generation...")
                commit_message = message_generator.generate_fallback_message(changed_files)

            # Step 6: Present message to user and handle response
            while True:
                user_choice = self.ui.show_proposed_message(commit_message)

                if user_choice == 'y':
                    # User confirmed, proceed with commit
                    break
                elif user_choice == 'n':
                    # User cancelled
                    self.ui.show_info("Commit cancelled")
                    return 0
                elif user_choice == 'e':
                    # User wants to edit
                    edited_message = self.ui.allow_message_editing(commit_message)
                    if edited_message is None:
                        # User cancelled editing
                        self.ui.show_info("Commit cancelled")
                        return 0
                    commit_message = edited_message
                    # Continue loop to show the edited message for confirmation
                else:
                    # This shouldn't happen due to UI validation, but handle it
                    self.ui.show_error("Invalid response")
                    continue

            # Step 7: Execute the commit with detailed error handling
            self.ui.show_info("Executing commit...")

            success, result_msg = self.git_ops.commit_with_message(commit_message)
            if success:
                self.ui.show_success(f"Commit {result_msg} created: {commit_message}")
                return 0
            else:
                self.ui.show_error(result_msg)
                # Provide additional guidance based on the error
                if "configuration" in result_msg.lower():
                    self.ui.show_info("After configuring Git, try the commit again.")
                elif "staged" in result_msg.lower():
                    self.ui.show_info("Verify that you have staged changes with 'git status'.")
                return 1

        except KeyboardInterrupt:
            print()  # New line after Ctrl+C
            self.ui.show_info("Operation cancelled by user")
            return 0
        except GitOperationError as e:
            self.ui.show_error(f"Git error: {str(e)}")
            return 1
        except GroqAPIError as e:
            self.ui.show_error(f"API error: {str(e)}")
            self.ui.show_info("Try again or verify your GROQ_API_KEY configuration.")
            return 1
        except Exception as e:
            self.ui.show_error(f"Unexpected error: {str(e)}")
            self.ui.show_info("If the problem persists, verify your Git configuration and network connectivity.")
            return 1

if __name__ == "__main__":
    buddy = CommitBuddy()
    sys.exit(buddy.main())
