"""
Configuration module for Kiro Commit Buddy
Handles environment variables and application settings
"""

import os
from typing import Optional, Tuple

class Config:
    """Configuration class for Kiro Commit Buddy"""

    def __init__(self):
        # Groq API Configuration
        self.GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
        self.GROQ_MODEL: str = "llama-3.1-8b-instant"  # Updated to current available model
        self.GROQ_ENDPOINT: str = "https://api.groq.com/openai/v1/chat/completions"

        # Application Settings
        self.MAX_DIFF_SIZE: int = 8000  # Maximum characters for diff
        self.TIMEOUT: int = 10  # API timeout in seconds
        self.MAX_TOKENS: int = 150  # Maximum tokens for API response
        self.TEMPERATURE: float = 0.3  # API temperature setting

        # Validation
        self._validate_config()

    def _validate_config(self):
        """Validate configuration settings"""
        if self.MAX_DIFF_SIZE <= 0:
            raise ValueError("MAX_DIFF_SIZE must be positive")

        if self.TIMEOUT <= 0:
            raise ValueError("TIMEOUT must be positive")

        if not (0.0 <= self.TEMPERATURE <= 2.0):
            raise ValueError("TEMPERATURE must be between 0.0 and 2.0")

    def has_groq_api_key(self) -> bool:
        """Check if Groq API key is configured"""
        return self.GROQ_API_KEY is not None and len(self.GROQ_API_KEY.strip()) > 0

    def get_groq_api_key(self) -> str:
        """Get Groq API key, raise error if not configured"""
        if not self.has_groq_api_key():
            raise ValueError(
                "GROQ_API_KEY environment variable is not configured.\n"
                "To configure it:\n"
                "  Windows: set GROQ_API_KEY=your_api_key\n"
                "  Linux/Mac: export GROQ_API_KEY=your_api_key\n"
                "Get your API key at: https://console.groq.com/keys"
            )
        return self.GROQ_API_KEY.strip()

    def validate_api_key_format(self) -> Tuple[bool, str]:
        """
        Validate API key format
        Returns: (is_valid, error_message)
        """
        if not self.has_groq_api_key():
            return False, "GROQ_API_KEY is not configured"

        api_key = self.GROQ_API_KEY.strip()

        # Basic format validation
        if len(api_key) < 10:
            return False, "GROQ_API_KEY appears to be too short"

        if not api_key.startswith('gsk_'):
            return False, "GROQ_API_KEY must start with 'gsk_'"

        if ' ' in api_key:
            return False, "GROQ_API_KEY must not contain spaces"

        return True, ""

    def get_api_headers(self) -> dict:
        """Get headers for Groq API requests"""
        return {
            "Authorization": f"Bearer {self.get_groq_api_key()}",
            "Content-Type": "application/json"
        }

    def get_commit_prompt_template(self) -> str:
        """Get the prompt template for commit message generation"""
        return """Carefully analyze the following git diff and generate a specific and descriptive commit message following Conventional Commits.

IMPORTANT INSTRUCTIONS:
1. Read the diff line by line to understand WHAT is being changed exactly
2. Identify specific elements like: buttons, functions, classes, text, styles, etc.
3. Describe the specific action, don't use generic terms like "updates" or "modifies"
4. Be descriptive about WHAT is being added, removed or changed

PREFIXES:
- feat: new functionality (buttons, forms, pages, functions)
- fix: bug fixes
- docs: documentation (README, comments)
- style: style/format changes (CSS, indentation)
- refactor: code restructuring
- test: add or modify tests
- chore: maintenance tasks

EXAMPLES OF GOOD MESSAGES:
- "feat: add contact button in header"
- "feat: implement login form"
- "fix: correct email validation"
- "style: improve navigation spacing"
- "docs: add comments to calculate function"

EXAMPLES OF BAD MESSAGES (avoid):
- "docs: update index.html"
- "feat: modify file"
- "chore: various changes"

Diff to analyze:
{diff}

RESPOND ONLY WITH THE COMMIT MESSAGE. DO NOT include explanations, justifications or additional text.

Required format: "prefix: specific description"
Maximum 50 characters.

Commit message:"""
