"""
Message generation module for Kiro Commit Buddy
Handles AI-powered and fallback message generation
"""

from typing import List, Optional
import re
import os
from config import Config
from groq_client import GroqClient, GroqAPIError

class MessageGenerator:
    """Handles commit message generation with AI and fallback logic"""

    # Conventional Commits prefixes and their patterns
    CONVENTIONAL_PREFIXES = {
        'feat': ['add', 'implement', 'create', 'new', 'feature'],
        'fix': ['fix', 'resolve', 'correct', 'repair', 'bug'],
        'docs': ['doc', 'readme', 'comment', 'documentation'],
        'refactor': ['refactor', 'restructure', 'reorganize', 'clean'],
        'test': ['test', 'spec', 'unittest', 'testing'],
        'chore': ['update', 'modify', 'change', 'maintenance', 'config']
    }

    def __init__(self, config: Config):
        self.config = config
        self.groq_client = None

        # Only initialize Groq client if API key is available
        if config.has_groq_api_key():
            try:
                self.groq_client = GroqClient(config)
            except GroqAPIError:
                # If client initialization fails, we'll use fallback
                self.groq_client = None

    def generate_message(self, diff: str, files: List[str]) -> str:
        """
        Generate commit message using AI or fallback

        Args:
            diff: Git diff content to analyze
            files: List of changed files

        Returns:
            Generated commit message following Conventional Commits format

        Raises:
            GroqAPIError: If there's a critical API error that should be reported to user
        """
        # Try AI generation first if available
        if self.groq_client and self._should_use_ai(diff):
            try:
                if not self.groq_client.is_api_available():
                    # API is not available, but this is expected in some cases
                    # Don't raise an error, just use fallback
                    pass
                else:
                    ai_message = self.groq_client.generate_commit_message(diff)

                    # Validate the AI-generated message
                    if self.validate_conventional_format(ai_message):
                        return ai_message
                    else:
                        # If AI message doesn't follow format, try to fix it
                        fixed_message = self._fix_conventional_format(ai_message, files)
                        if fixed_message:
                            return fixed_message

            except GroqAPIError as e:
                # Check if this is a critical error that should be reported
                error_msg = str(e).lower()
                if any(critical in error_msg for critical in ['invalid api key', 'unauthorized', 'authentication']):
                    # Critical authentication errors should be reported
                    raise e
                elif 'rate limit' in error_msg:
                    # Rate limit errors should be reported but are recoverable
                    raise GroqAPIError("Límite de API excedido. Intenta nuevamente en unos minutos o usa el mensaje de respaldo.")
                else:
                    # Other API errors can fall back silently
                    pass

        # Use fallback message generation
        return self.generate_fallback_message(files)

    def generate_fallback_message(self, files: List[str]) -> str:
        """
        Generate fallback commit message when AI is not available

        Args:
            files: List of changed files

        Returns:
            Fallback commit message following Conventional Commits format
        """
        if not files:
            return "chore: update files"

        # Determine commit type based on file patterns
        commit_type = self._determine_commit_type_from_files(files)

        # Generate message based on number of files
        if len(files) == 1:
            filename = os.path.basename(files[0])
            return f"{commit_type}: update {filename}"
        elif len(files) <= 3:
            filenames = [os.path.basename(f) for f in files]
            return f"{commit_type}: update {', '.join(filenames)}"
        else:
            return f"{commit_type}: update {len(files)} files"

    def validate_conventional_format(self, message: str) -> bool:
        """
        Validate if message follows Conventional Commits format

        Args:
            message: Commit message to validate

        Returns:
            True if message follows Conventional Commits format
        """
        if not message or not message.strip():
            return False

        # Conventional Commits pattern: type(scope): description
        # Scope is optional, so we check for: type: description
        pattern = r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'

        return bool(re.match(pattern, message.strip(), re.IGNORECASE))

    def _should_use_ai(self, diff: str) -> bool:
        """
        Determine if AI should be used based on diff complexity

        Args:
            diff: Git diff content

        Returns:
            True if AI should be used
        """
        # Use AI for non-empty diffs that aren't too large
        return (
            diff and
            diff.strip() and
            len(diff) <= self.config.MAX_DIFF_SIZE and
            len(diff.split('\n')) > 3  # More than just a few lines
        )

    def _determine_commit_type_from_files(self, files: List[str]) -> str:
        """
        Determine commit type based on file patterns

        Args:
            files: List of changed files

        Returns:
            Appropriate commit type prefix
        """
        if not files:
            return 'chore'

        # Count file types with higher weights for specific patterns
        type_scores = {prefix: 0 for prefix in self.CONVENTIONAL_PREFIXES.keys()}

        for file_path in files:
            filename = os.path.basename(file_path).lower()
            file_ext = os.path.splitext(filename)[1].lower()
            full_path_lower = file_path.lower()

            # Check for documentation files (highest priority)
            if any(doc_pattern in filename for doc_pattern in ['readme', 'doc', 'changelog']) or file_ext == '.md':
                type_scores['docs'] += 3

            # Check for test files (high priority)
            elif any(test_pattern in filename for test_pattern in ['test', 'spec']) or \
                 any(test_pattern in full_path_lower for test_pattern in ['test_', '_test', '.test']):
                type_scores['test'] += 3

            # Check for configuration files
            elif any(config_pattern in filename for config_pattern in ['config', 'settings']) or \
                 file_ext in ['.json', '.yml', '.yaml', '.toml', '.ini', '.cfg']:
                type_scores['chore'] += 2

            # Check for source code files (could be feat, fix, or refactor)
            elif file_ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.cs']:
                # Default to feat for new functionality, but this is just a guess
                type_scores['feat'] += 1

            # Default to chore for other files
            else:
                type_scores['chore'] += 1

        # Return the type with highest score
        return max(type_scores.items(), key=lambda x: x[1])[0]

    def _fix_conventional_format(self, message: str, files: List[str]) -> Optional[str]:
        """
        Try to fix a message to follow Conventional Commits format

        Args:
            message: Original message to fix
            files: List of changed files for context

        Returns:
            Fixed message or None if cannot be fixed
        """
        if not message or not message.strip():
            return None

        message = message.strip()

        # If message already has a conventional prefix, just clean it up
        for prefix in self.CONVENTIONAL_PREFIXES.keys():
            if message.lower().startswith(f"{prefix}:") or message.lower().startswith(f"{prefix}("):
                # Clean up the message
                if len(message) > 72:
                    message = message[:69] + "..."
                return message

        # Get file-based type first
        file_based_type = self._determine_commit_type_from_files(files)

        # Try to add appropriate prefix based on content, but prioritize specific keywords
        message_lower = message.lower()

        # Check for specific, non-generic keywords first
        specific_matches = []
        generic_matches = []

        for prefix, keywords in self.CONVENTIONAL_PREFIXES.items():
            for keyword in keywords:
                if keyword in message_lower:
                    # Generic keywords that could apply to many contexts
                    if keyword in ['update', 'modify', 'change']:
                        generic_matches.append(prefix)
                    else:
                        specific_matches.append(prefix)
                    break

        # If we have specific matches, use the first one
        if specific_matches:
            return f"{specific_matches[0]}: {message}"

        # If we only have generic matches, prefer file-based determination
        # unless the file-based type is also generic (chore)
        if generic_matches and file_based_type == 'chore':
            return f"{generic_matches[0]}: {message}"

        # Use file-based determination
        return f"{file_based_type}: {message}"
