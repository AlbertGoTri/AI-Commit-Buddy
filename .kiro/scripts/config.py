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
                "Para configurarla:\n"
                "  Windows: set GROQ_API_KEY=tu_api_key\n"
                "  Linux/Mac: export GROQ_API_KEY=tu_api_key\n"
                "Obtén tu API key en: https://console.groq.com/keys"
            )
        return self.GROQ_API_KEY.strip()

    def validate_api_key_format(self) -> Tuple[bool, str]:
        """
        Validate API key format
        Returns: (is_valid, error_message)
        """
        if not self.has_groq_api_key():
            return False, "GROQ_API_KEY no está configurada"

        api_key = self.GROQ_API_KEY.strip()

        # Basic format validation
        if len(api_key) < 10:
            return False, "GROQ_API_KEY parece ser demasiado corta"

        if not api_key.startswith('gsk_'):
            return False, "GROQ_API_KEY debe comenzar con 'gsk_'"

        if ' ' in api_key:
            return False, "GROQ_API_KEY no debe contener espacios"

        return True, ""

    def get_api_headers(self) -> dict:
        """Get headers for Groq API requests"""
        return {
            "Authorization": f"Bearer {self.get_groq_api_key()}",
            "Content-Type": "application/json"
        }

    def get_commit_prompt_template(self) -> str:
        """Get the prompt template for commit message generation"""
        return """Analiza el siguiente git diff y genera un mensaje de commit siguiendo Conventional Commits.

Reglas:
- Usa prefijos: feat, fix, docs, refactor, test, chore
- Máximo 50 caracteres para el título
- Sé específico pero conciso
- En español

Diff:
{diff}

Responde solo con el mensaje de commit:"""
