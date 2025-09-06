"""
User interface module for Kiro Commit Buddy
Handles all user interactions and display formatting
"""

import sys
import os
from typing import Optional
try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)  # Initialize colorama for cross-platform color support
    COLORS_AVAILABLE = True
except ImportError:
    # Fallback if colorama is not available
    COLORS_AVAILABLE = False
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""
    class Back:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = ""

class UserInterface:
    """Handles user interaction and display with color formatting"""

    def __init__(self):
        self.colors_enabled = COLORS_AVAILABLE and sys.stdout.isatty()
        # Check if we can use emoji characters (avoid encoding issues on Windows)
        self.use_emoji = self._can_use_emoji()

    def _can_use_emoji(self) -> bool:
        """Check if the terminal can handle emoji characters"""
        try:
            # Try to encode a simple emoji
            "✅".encode(sys.stdout.encoding or 'utf-8')
            return True
        except (UnicodeEncodeError, LookupError):
            return False

    def _colorize(self, text: str, color: str = "", style: str = "") -> str:
        """Apply color and style to text if colors are enabled"""
        if not self.colors_enabled:
            return text
        return f"{style}{color}{text}{Style.RESET_ALL}"

    def show_proposed_message(self, message: str) -> str:
        """
        Show proposed commit message and get user confirmation
        Returns: 'y' for yes, 'n' for no, 'e' for edit
        """
        print()
        icon = "📝" if self.use_emoji else ">>>"
        print(self._colorize(f"{icon} Proposed commit message:", Fore.CYAN, Style.BRIGHT))
        print()

        # Display the message with highlighting
        print(self._colorize(f"  {message}", Fore.GREEN, Style.BRIGHT))
        print()

        # Show options with colors
        options_text = (
            f"{self._colorize('y', Fore.GREEN, Style.BRIGHT)} = use this message  "
            f"{self._colorize('n', Fore.RED, Style.BRIGHT)} = cancel  "
            f"{self._colorize('e', Fore.YELLOW, Style.BRIGHT)} = edit"
        )
        print(f"Use this message? ({options_text}): ", end="")

        while True:
            try:
                response = input().lower().strip()
                if response in ['y', 'yes', '']:
                    return 'y'
                elif response in ['n', 'no']:
                    return 'n'
                elif response in ['e', 'edit']:
                    return 'e'
                else:
                    print(f"Please enter {self._colorize('y', Fore.GREEN)}, {self._colorize('n', Fore.RED)}, or {self._colorize('e', Fore.YELLOW)}: ", end="")
            except (EOFError, KeyboardInterrupt):
                print()
                return 'n'

    def allow_message_editing(self, message: str) -> Optional[str]:
        """
        Allow user to edit the commit message
        Returns the edited message or None if cancelled
        """
        print()
        icon = "✏️" if self.use_emoji else "EDIT:"
        print(self._colorize(f"{icon} Editing commit message:", Fore.YELLOW, Style.BRIGHT))
        print(self._colorize("(Press Enter for an empty line to finish, Ctrl+C to cancel)", Fore.YELLOW))
        print()

        # Show current message
        print(self._colorize("Current message:", Fore.CYAN))
        print(f"  {message}")
        print()

        print(self._colorize("New message:", Fore.CYAN))

        lines = []
        try:
            while True:
                line = input("  ")
                if line.strip() == "" and lines:
                    break
                lines.append(line)
                if not lines:  # First line is empty, break immediately
                    break
        except (EOFError, KeyboardInterrupt):
            print()
            cancel_icon = "❌" if self.use_emoji else "CANCELLED:"
            print(self._colorize(f"{cancel_icon} Edit cancelled", Fore.RED))
            return None

        edited_message = "\n".join(lines).strip()
        if not edited_message:
            warning_icon = "❌" if self.use_emoji else "WARNING:"
            print(self._colorize(f"{warning_icon} Empty message, using original message", Fore.YELLOW))
            return message

        return edited_message

    def show_error(self, error: str) -> None:
        """Display error message to user with red color"""
        error_icon = "❌" if self.use_emoji else "ERROR:"
        colored_error = self._colorize(f"{error_icon} {error}", Fore.RED, Style.BRIGHT)
        print(colored_error, file=sys.stderr)

    def show_success(self, message: str) -> None:
        """Display success message to user with green color"""
        success_icon = "✅" if self.use_emoji else "SUCCESS:"
        colored_message = self._colorize(f"{success_icon} {message}", Fore.GREEN, Style.BRIGHT)
        print(colored_message)

    def show_info(self, message: str) -> None:
        """Display informational message to user with blue color"""
        info_icon = "ℹ️" if self.use_emoji else "INFO:"
        colored_message = self._colorize(f"{info_icon} {message}", Fore.BLUE)
        print(colored_message)

    def show_warning(self, message: str) -> None:
        """Display warning message to user with yellow color"""
        warning_icon = "⚠️" if self.use_emoji else "WARNING:"
        colored_message = self._colorize(f"{warning_icon} {message}", Fore.YELLOW, Style.BRIGHT)
        print(colored_message)

    def show_diff_summary(self, files: list, additions: int = 0, deletions: int = 0) -> None:
        """Display a summary of changed files with formatting"""
        if not files:
            return

        print()
        folder_icon = "📁" if self.use_emoji else "FILES:"
        print(self._colorize(f"{folder_icon} Modified files:", Fore.CYAN, Style.BRIGHT))

        for file in files[:5]:  # Show max 5 files
            print(f"  • {self._colorize(file, Fore.WHITE)}")

        if len(files) > 5:
            remaining = len(files) - 5
            print(f"  ... and {self._colorize(str(remaining), Fore.YELLOW)} more files")

        if additions > 0 or deletions > 0:
            stats = []
            if additions > 0:
                stats.append(self._colorize(f"+{additions}", Fore.GREEN))
            if deletions > 0:
                stats.append(self._colorize(f"-{deletions}", Fore.RED))
            print(f"  ({' '.join(stats)})")
        print()

    def confirm_action(self, message: str, default: bool = False) -> bool:
        """
        Ask user for confirmation with y/n prompt
        Returns True if confirmed, False otherwise
        """
        default_text = "Y/n" if default else "y/N"
        prompt = f"{message} ({default_text}): "

        try:
            response = input(prompt).lower().strip()
            if response == "":
                return default
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            print()
            return False
