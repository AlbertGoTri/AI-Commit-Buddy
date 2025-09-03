"""
Groq API client for Kiro Commit Buddy
Handles communication with Groq API for AI-powered commit message generation
"""

from typing import Optional, Dict, Any
import json
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from config import Config

class GroqAPIError(Exception):
    """Custom exception for Groq API errors"""
    pass

class GroqClient:
    """Client for Groq API interactions"""

    def __init__(self, config: Config):
        self.config = config
        self._validate_api_key()

    def _validate_api_key(self) -> None:
        """Validate that API key is configured and has correct format"""
        if not self.config.has_groq_api_key():
            raise GroqAPIError(
                "GROQ_API_KEY environment variable is not configured.\n"
                "Para configurarla:\n"
                "  Windows: set GROQ_API_KEY=tu_api_key\n"
                "  Linux/Mac: export GROQ_API_KEY=tu_api_key\n"
                "Obtén tu API key en: https://console.groq.com/keys"
            )

        # Validate API key format
        is_valid, error_msg = self.config.validate_api_key_format()
        if not is_valid:
            raise GroqAPIError(f"Formato de API key inválido: {error_msg}")

    def is_api_available(self) -> bool:
        """Check if Groq API is available and accessible"""
        try:
            # Make a simple test request to check API availability
            headers = self.config.get_api_headers()

            # Use a minimal test payload
            test_payload = {
                "model": self.config.GROQ_MODEL,
                "messages": [
                    {"role": "user", "content": "test"}
                ],
                "max_tokens": 1,
                "temperature": 0.1
            }

            response = requests.post(
                self.config.GROQ_ENDPOINT,
                headers=headers,
                json=test_payload,
                timeout=self.config.TIMEOUT
            )

            # Consider API available if we get any response (even errors like rate limiting)
            # as long as it's not a connection/network error
            return response.status_code in [200, 400, 401, 429, 500]

        except (ConnectionError, Timeout, RequestException):
            return False
        except Exception:
            return False

    def generate_commit_message(self, diff: str) -> str:
        """
        Generate commit message using Groq API

        Args:
            diff: Git diff content to analyze

        Returns:
            Generated commit message

        Raises:
            GroqAPIError: If API request fails or returns invalid response
        """
        try:
            # Truncate diff if it's too long
            if len(diff) > self.config.MAX_DIFF_SIZE:
                diff = diff[:self.config.MAX_DIFF_SIZE] + "\n... (truncated)"

            # Prepare the API request
            headers = self.config.get_api_headers()
            prompt = self.config.get_commit_prompt_template().format(diff=diff)

            payload = {
                "model": self.config.GROQ_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.config.MAX_TOKENS,
                "temperature": self.config.TEMPERATURE
            }

            # Make the API request
            response = requests.post(
                self.config.GROQ_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=self.config.TIMEOUT
            )

            # Handle different response status codes
            if response.status_code == 401:
                raise GroqAPIError("Invalid API key. Please check your GROQ_API_KEY.")
            elif response.status_code == 429:
                raise GroqAPIError("API rate limit exceeded. Please try again later.")
            elif response.status_code == 500:
                raise GroqAPIError("Groq API server error. Please try again later.")
            elif response.status_code != 200:
                raise GroqAPIError(f"API request failed with status {response.status_code}")

            # Parse the response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                raise GroqAPIError("Invalid JSON response from API")

            # Extract the commit message
            commit_message = self._extract_commit_message(response_data)

            # Validate and clean the message
            return self._clean_commit_message(commit_message)

        except (ConnectionError, Timeout):
            raise GroqAPIError("Network error: Unable to connect to Groq API")
        except RequestException as e:
            raise GroqAPIError(f"Request error: {str(e)}")
        except Exception as e:
            if isinstance(e, GroqAPIError):
                raise
            raise GroqAPIError(f"Unexpected error: {str(e)}")

    def _extract_commit_message(self, response_data: Dict[Any, Any]) -> str:
        """Extract commit message from API response"""
        try:
            choices = response_data.get("choices", [])
            if not choices:
                raise GroqAPIError("No choices in API response")

            message = choices[0].get("message", {})
            content = message.get("content", "")

            if not content or not content.strip():
                raise GroqAPIError("Empty response from API")

            return content.strip()

        except (KeyError, IndexError, TypeError) as e:
            raise GroqAPIError(f"Invalid API response format: {str(e)}")

    def _clean_commit_message(self, message: str) -> str:
        """Clean and validate the commit message"""
        # Remove any extra whitespace and newlines
        message = message.strip()

        # Take only the first line if there are multiple lines
        if '\n' in message:
            message = message.split('\n')[0].strip()

        # Remove quotes if the message is wrapped in them
        if (message.startswith('"') and message.endswith('"')) or \
           (message.startswith("'") and message.endswith("'")):
            message = message[1:-1].strip()

        # Ensure the message is not empty after cleaning
        if not message:
            raise GroqAPIError("Empty commit message after cleaning")

        # Limit length to reasonable commit message size
        if len(message) > 72:
            message = message[:69] + "..."

        return message
