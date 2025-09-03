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
                if "sin stage" in status_msg:
                    self.ui.show_warning(status_msg)
                    self.ui.show_info("Sugerencia: Usa 'git add <archivo>' para stagear cambios específicos o 'git add .' para stagear todos los cambios.")
                else:
                    self.ui.show_info(status_msg)
                return 0

            self.ui.show_info(status_msg)

            # Step 3: Get staged diff with error handling
            try:
                staged_diff = self.git_ops.get_staged_diff()
            except GitOperationError as e:
                self.ui.show_error(f"Error obteniendo diff: {str(e)}")
                return 1

            # Step 4: Show diff summary to user
            self.ui.show_diff_summary(changed_files)

            # Step 5: Generate commit message with comprehensive error handling
            message_generator = MessageGenerator(self.config)

            try:
                commit_message = message_generator.generate_message(staged_diff, changed_files)
            except GroqAPIError as e:
                self.ui.show_warning(f"Error de API: {str(e)}")
                self.ui.show_info("Usando generación de mensaje local...")
                commit_message = message_generator.generate_fallback_message(changed_files)
            except Exception as e:
                self.ui.show_warning(f"Error generando mensaje: {str(e)}")
                self.ui.show_info("Usando generación de mensaje de respaldo...")
                commit_message = message_generator.generate_fallback_message(changed_files)

            # Step 6: Present message to user and handle response
            while True:
                user_choice = self.ui.show_proposed_message(commit_message)

                if user_choice == 'y':
                    # User confirmed, proceed with commit
                    break
                elif user_choice == 'n':
                    # User cancelled
                    self.ui.show_info("Commit cancelado")
                    return 0
                elif user_choice == 'e':
                    # User wants to edit
                    edited_message = self.ui.allow_message_editing(commit_message)
                    if edited_message is None:
                        # User cancelled editing
                        self.ui.show_info("Commit cancelado")
                        return 0
                    commit_message = edited_message
                    # Continue loop to show the edited message for confirmation
                else:
                    # This shouldn't happen due to UI validation, but handle it
                    self.ui.show_error("Respuesta inválida")
                    continue

            # Step 7: Execute the commit with detailed error handling
            self.ui.show_info("Ejecutando commit...")

            success, result_msg = self.git_ops.commit_with_message(commit_message)
            if success:
                self.ui.show_success(f"Commit {result_msg} creado: {commit_message}")
                return 0
            else:
                self.ui.show_error(result_msg)
                # Provide additional guidance based on the error
                if "configuración" in result_msg.lower():
                    self.ui.show_info("Después de configurar Git, intenta el commit nuevamente.")
                elif "staged" in result_msg.lower():
                    self.ui.show_info("Verifica que tienes cambios staged con 'git status'.")
                return 1

        except KeyboardInterrupt:
            print()  # New line after Ctrl+C
            self.ui.show_info("Operación cancelada por el usuario")
            return 0
        except GitOperationError as e:
            self.ui.show_error(f"Error de Git: {str(e)}")
            return 1
        except GroqAPIError as e:
            self.ui.show_error(f"Error de API: {str(e)}")
            self.ui.show_info("Intenta nuevamente o verifica tu configuración de GROQ_API_KEY.")
            return 1
        except Exception as e:
            self.ui.show_error(f"Error inesperado: {str(e)}")
            self.ui.show_info("Si el problema persiste, verifica tu configuración de Git y la conectividad de red.")
            return 1

if __name__ == "__main__":
    buddy = CommitBuddy()
    sys.exit(buddy.main())
