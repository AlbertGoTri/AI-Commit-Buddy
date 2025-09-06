"""
Groq API client for Kiro Commit Buddy
Handles communication with Groq API for AI-powered commit message generation
"""

from typing import Optional, Dict, Any
import json
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from config import Config
from verbose_logger import get_logger

class GroqAPIError(Exception):
    """Custom exception for Groq API errors"""
    pass

class GroqClient:
    """Client for Groq API interactions"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        self.logger.debug("Initializing GroqClient", "GROQ")
        self._validate_api_key()

    def _validate_api_key(self) -> None:
        """Validate that API key is configured and has correct format"""
        self.logger.debug("Validating API key configuration", "GROQ")
        
        if not self.config.has_groq_api_key():
            self.logger.error("GROQ_API_KEY not configured", "GROQ")
            raise GroqAPIError(
                "GROQ_API_KEY environment variable is not configured.\n"
                "To configure it:\n"
                "  Windows: set GROQ_API_KEY=your_api_key\n"
                "  Linux/Mac: export GROQ_API_KEY=your_api_key\n"
                "Get your API key at: https://console.groq.com/keys"
            )

        # Validate API key format
        is_valid, error_msg = self.config.validate_api_key_format()
        if not is_valid:
            self.logger.error(f"API key format validation failed: {error_msg}", "GROQ")
            raise GroqAPIError(f"Invalid API key format: {error_msg}")
        
        self.logger.debug("API key validation successful", "GROQ")

    def is_api_available(self) -> bool:
        """Check if Groq API is available and accessible"""
        self.logger.debug("Checking API availability", "GROQ")
        
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

            self.logger.log_api_request(self.config.GROQ_ENDPOINT, headers, test_payload)

            response = requests.post(
                self.config.GROQ_ENDPOINT,
                headers=headers,
                json=test_payload,
                timeout=self.config.TIMEOUT
            )

            self.logger.debug(f"API availability check response: {response.status_code}", "GROQ")

            # Consider API available if we get any response (even errors like rate limiting)
            # as long as it's not a connection/network error
            # 401 means API is reachable but auth failed, which we'll handle in actual calls
            is_available = response.status_code in [200, 400, 401, 429, 500]
            self.logger.debug(f"API availability result: {is_available} (status: {response.status_code})", "GROQ")
            return is_available

        except (ConnectionError, Timeout, RequestException) as e:
            self.logger.error(f"API availability check failed - network error: {str(e)}", "GROQ")
            return False
        except Exception as e:
            self.logger.error(f"API availability check failed - unexpected error: {str(e)}", "GROQ")
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
        self.logger.debug(f"Generating commit message for diff ({len(diff)} chars)", "GROQ")
        
        try:
            # Truncate diff if it's too long
            original_length = len(diff)
            if len(diff) > self.config.MAX_DIFF_SIZE:
                diff = diff[:self.config.MAX_DIFF_SIZE] + "\n... (truncated)"
                self.logger.debug(f"Diff truncated from {original_length} to {len(diff)} chars", "GROQ")

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

            self.logger.log_api_request(self.config.GROQ_ENDPOINT, headers, payload)

            # Make the API request
            self.logger.debug("Sending request to Groq API", "GROQ")
            response = requests.post(
                self.config.GROQ_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=self.config.TIMEOUT
            )

            self.logger.debug(f"Received response with status: {response.status_code}", "GROQ")

            # Log response details
            try:
                response_data = response.json()
                self.logger.log_api_response(response.status_code, response.headers, response_data)
            except:
                self.logger.log_api_response(response.status_code, response.headers, response.text)

            # Handle different response status codes
            if response.status_code == 401:
                self.logger.error("API authentication failed", "GROQ")
                raise GroqAPIError("Invalid API key. Please check your GROQ_API_KEY.")
            elif response.status_code == 429:
                self.logger.warning("API rate limit exceeded", "GROQ")
                raise GroqAPIError("API rate limit exceeded. Please try again later.")
            elif response.status_code == 500:
                self.logger.error("API server error", "GROQ")
                raise GroqAPIError("Groq API server error. Please try again later.")
            elif response.status_code != 200:
                self.logger.error(f"API request failed with status {response.status_code}", "GROQ")
                raise GroqAPIError(f"API request failed with status {response.status_code}")

            # Parse the response
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON response: {str(e)}", "GROQ")
                raise GroqAPIError("Invalid JSON response from API")

            # Extract the commit message
            commit_message = self._extract_commit_message(response_data)
            self.logger.debug(f"Extracted commit message: {commit_message}", "GROQ")

            # Validate and clean the message
            cleaned_message = self._clean_commit_message(commit_message)
            self.logger.debug(f"Cleaned commit message: {cleaned_message}", "GROQ")
            
            self.logger.info(f"Successfully generated commit message: {cleaned_message}", "GROQ")
            return cleaned_message

        except (ConnectionError, Timeout) as e:
            self.logger.error(f"Network error: {str(e)}", "GROQ")
            raise GroqAPIError("Network error: Unable to connect to Groq API")
        except RequestException as e:
            self.logger.error(f"Request error: {str(e)}", "GROQ")
            raise GroqAPIError(f"Request error: {str(e)}")
        except Exception as e:
            if isinstance(e, GroqAPIError):
                raise
            self.logger.error(f"Unexpected error: {str(e)}", "GROQ")
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
        import re
        
        # Remove any extra whitespace and newlines
        message = message.strip()
        
        # If the message contains explanations, try to extract just the commit message
        lines = message.split('\n')
        
        # Look for lines that match conventional commit format
        conventional_pattern = r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'
        
        for line in lines:
            line = line.strip()
            # Remove quotes if present
            if (line.startswith('"') and line.endswith('"')) or \
               (line.startswith("'") and line.endswith("'")):
                line = line[1:-1].strip()
            
            # Remove backticks if present
            if line.startswith('`') and line.endswith('`'):
                line = line[1:-1].strip()
            
            # Check if this line matches conventional commit format
            if re.match(conventional_pattern, line, re.IGNORECASE):
                message = line
                break
        else:
            # If no conventional commit found, use the first non-empty line
            for line in lines:
                line = line.strip()
                if line and not line.lower().startswith(('analysis:', 'justification:', 'based on', 'the message')):
                    # Remove quotes and backticks
                    if (line.startswith('"') and line.endswith('"')) or \
                       (line.startswith("'") and line.endswith("'")):
                        line = line[1:-1].strip()
                    if line.startswith('`') and line.endswith('`'):
                        line = line[1:-1].strip()
                    message = line
                    break

        # Ensure the message is not empty after cleaning
        if not message:
            raise GroqAPIError("Empty commit message after cleaning")

        # Limit length to reasonable commit message size
        if len(message) > 72:
            message = message[:69] + "..."

        return message
