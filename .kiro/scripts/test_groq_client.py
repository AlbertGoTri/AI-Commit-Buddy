"""
Unit tests for GroqClient class
Tests API key validation, API availability checking, and commit message generation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

from groq_client import GroqClient, GroqAPIError
from config import Config


class TestGroqClient(unittest.TestCase):
    """Test cases for GroqClient class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config with valid API key
        self.mock_config = Mock(spec=Config)
        self.mock_config.GROQ_MODEL = "llama3-70b-8192"
        self.mock_config.GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
        self.mock_config.MAX_DIFF_SIZE = 8000
        self.mock_config.TIMEOUT = 10
        self.mock_config.MAX_TOKENS = 150
        self.mock_config.TEMPERATURE = 0.3
        self.mock_config.has_groq_api_key.return_value = True
        self.mock_config.get_groq_api_key.return_value = "test-api-key"
        self.mock_config.get_api_headers.return_value = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json"
        }
        self.mock_config.get_commit_prompt_template.return_value = "Test prompt: {diff}"
    
    def test_init_with_valid_api_key(self):
        """Test GroqClient initialization with valid API key"""
        client = GroqClient(self.mock_config)
        self.assertEqual(client.config, self.mock_config)
        self.mock_config.has_groq_api_key.assert_called_once()
    
    def test_init_without_api_key(self):
        """Test GroqClient initialization without API key raises error"""
        self.mock_config.has_groq_api_key.return_value = False
        
        with self.assertRaises(GroqAPIError) as context:
            GroqClient(self.mock_config)
        
        self.assertIn("GROQ_API_KEY environment variable is not configured", str(context.exception))
    
    @patch('groq_client.requests.post')
    def test_is_api_available_success(self, mock_post):
        """Test API availability check with successful response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        client = GroqClient(self.mock_config)
        result = client.is_api_available()
        
        self.assertTrue(result)
        mock_post.assert_called_once()
        
        # Verify the test request parameters
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['timeout'], 10)
        self.assertIn('headers', call_args[1])
        self.assertIn('json', call_args[1])
    
    @patch('groq_client.requests.post')
    def test_is_api_available_with_error_codes(self, mock_post):
        """Test API availability check with various error codes that still indicate availability"""
        client = GroqClient(self.mock_config)
        
        # Test various status codes that indicate API is available but may have issues
        for status_code in [400, 401, 429, 500]:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_post.return_value = mock_response
            
            result = client.is_api_available()
            self.assertTrue(result, f"Should return True for status code {status_code}")
    
    @patch('groq_client.requests.post')
    def test_is_api_available_connection_error(self, mock_post):
        """Test API availability check with connection error"""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        client = GroqClient(self.mock_config)
        result = client.is_api_available()
        
        self.assertFalse(result)
    
    @patch('groq_client.requests.post')
    def test_is_api_available_timeout(self, mock_post):
        """Test API availability check with timeout"""
        mock_post.side_effect = Timeout("Request timed out")
        
        client = GroqClient(self.mock_config)
        result = client.is_api_available()
        
        self.assertFalse(result)
    
    @patch('groq_client.requests.post')
    def test_generate_commit_message_success(self, mock_post):
        """Test successful commit message generation"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "feat: add user authentication system"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = GroqClient(self.mock_config)
        result = client.generate_commit_message("diff content here")
        
        self.assertEqual(result, "feat: add user authentication system")
        mock_post.assert_called_once()
        
        # Verify request parameters
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['timeout'], 10)
        self.assertIn('json', call_args[1])
        
        # Verify payload structure
        payload = call_args[1]['json']
        self.assertEqual(payload['model'], "llama3-70b-8192")
        self.assertEqual(payload['max_tokens'], 150)
        self.assertEqual(payload['temperature'], 0.3)
        self.assertIn('messages', payload)
    
    @patch('groq_client.requests.post')
    def test_generate_commit_message_with_long_diff(self, mock_post):
        """Test commit message generation with diff that exceeds max size"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "fix: truncate long diffs"}}]
        }
        mock_post.return_value = mock_response
        
        client = GroqClient(self.mock_config)
        long_diff = "x" * 10000  # Exceeds MAX_DIFF_SIZE of 8000
        
        result = client.generate_commit_message(long_diff)
        
        self.assertEqual(result, "fix: truncate long diffs")
        
        # Verify that the diff was truncated in the request
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        message_content = payload['messages'][0]['content']
        self.assertIn("(truncated)", message_content)
    
    @patch('groq_client.requests.post')
    def test_generate_commit_message_api_errors(self, mock_post):
        """Test commit message generation with various API errors"""
        client = GroqClient(self.mock_config)
        
        # Test different error status codes
        error_cases = [
            (401, "invalid api key"),
            (429, "rate limit exceeded"),
            (500, "server error"),
            (404, "status 404")
        ]
        
        for status_code, expected_message in error_cases:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_post.return_value = mock_response
            
            with self.assertRaises(GroqAPIError) as context:
                client.generate_commit_message("test diff")
            
            self.assertIn(expected_message, str(context.exception).lower())
    
    @patch('groq_client.requests.post')
    def test_generate_commit_message_connection_error(self, mock_post):
        """Test commit message generation with connection error"""
        mock_post.side_effect = ConnectionError("Network error")
        
        client = GroqClient(self.mock_config)
        
        with self.assertRaises(GroqAPIError) as context:
            client.generate_commit_message("test diff")
        
        self.assertIn("Network error", str(context.exception))
    
    @patch('groq_client.requests.post')
    def test_generate_commit_message_timeout(self, mock_post):
        """Test commit message generation with timeout"""
        mock_post.side_effect = Timeout("Request timed out")
        
        client = GroqClient(self.mock_config)
        
        with self.assertRaises(GroqAPIError) as context:
            client.generate_commit_message("test diff")
        
        self.assertIn("Network error", str(context.exception))
    
    @patch('groq_client.requests.post')
    def test_generate_commit_message_invalid_json(self, mock_post):
        """Test commit message generation with invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response
        
        client = GroqClient(self.mock_config)
        
        with self.assertRaises(GroqAPIError) as context:
            client.generate_commit_message("test diff")
        
        self.assertIn("Invalid JSON response", str(context.exception))
    
    @patch('groq_client.requests.post')
    def test_generate_commit_message_empty_response(self, mock_post):
        """Test commit message generation with empty response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": []}
        mock_post.return_value = mock_response
        
        client = GroqClient(self.mock_config)
        
        with self.assertRaises(GroqAPIError) as context:
            client.generate_commit_message("test diff")
        
        self.assertIn("No choices in API response", str(context.exception))
    
    @patch('groq_client.requests.post')
    def test_generate_commit_message_empty_content(self, mock_post):
        """Test commit message generation with empty content"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": ""}}]
        }
        mock_post.return_value = mock_response
        
        client = GroqClient(self.mock_config)
        
        with self.assertRaises(GroqAPIError) as context:
            client.generate_commit_message("test diff")
        
        self.assertIn("Empty response from API", str(context.exception))
    
    @patch('groq_client.requests.post')
    def test_clean_commit_message_multiline(self, mock_post):
        """Test commit message cleaning with multiline response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "feat: add feature\n\nThis is a detailed description"}}]
        }
        mock_post.return_value = mock_response
        
        client = GroqClient(self.mock_config)
        result = client.generate_commit_message("test diff")
        
        # Should only return the first line
        self.assertEqual(result, "feat: add feature")
    
    @patch('groq_client.requests.post')
    def test_clean_commit_message_with_quotes(self, mock_post):
        """Test commit message cleaning with quoted response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '"feat: add quoted feature"'}}]
        }
        mock_post.return_value = mock_response
        
        client = GroqClient(self.mock_config)
        result = client.generate_commit_message("test diff")
        
        # Should remove quotes
        self.assertEqual(result, "feat: add quoted feature")
    
    @patch('groq_client.requests.post')
    def test_clean_commit_message_too_long(self, mock_post):
        """Test commit message cleaning with very long message"""
        long_message = "feat: " + "x" * 100  # Very long message
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": long_message}}]
        }
        mock_post.return_value = mock_response
        
        client = GroqClient(self.mock_config)
        result = client.generate_commit_message("test diff")
        
        # Should be truncated to 72 characters with ellipsis
        self.assertEqual(len(result), 72)
        self.assertTrue(result.endswith("..."))


if __name__ == '__main__':
    unittest.main()