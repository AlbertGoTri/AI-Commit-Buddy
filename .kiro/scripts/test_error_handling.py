"""
Comprehensive tests for error handling scenarios in Kiro Commit Buddy
Tests all error conditions specified in requirements 3.1, 3.2, 3.3, 4.2, 4.3
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import os
import sys

# Add the scripts directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from git_operations import GitOperations, GitOperationError
from groq_client import GroqClient, GroqAPIError
from message_generator import MessageGenerator
from config import Config
from commit_buddy import CommitBuddy
from user_interface import UserInterface


class TestGitErrorHandling(unittest.TestCase):
    """Test Git-related error handling scenarios"""
    
    def setUp(self):
        self.git_ops = GitOperations()
    
    @patch('subprocess.run')
    def test_validate_git_environment_git_not_installed(self, mock_run):
        """Test error handling when Git is not installed"""
        mock_run.side_effect = FileNotFoundError()
        
        is_valid, error_msg = self.git_ops.validate_git_environment()
        
        self.assertFalse(is_valid)
        self.assertIn("Git is not installed", error_msg)
    
    @patch('subprocess.run')
    def test_validate_git_environment_not_git_repo(self, mock_run):
        """Test error handling when not in a Git repository"""
        # First call succeeds (git --version), second call fails (git rev-parse)
        mock_run.side_effect = [
            Mock(returncode=0, stdout="git version 2.0.0"),  # git --version
            Mock(returncode=128, stderr="fatal: not a git repository")  # git rev-parse
        ]
        
        is_valid, error_msg = self.git_ops.validate_git_environment()
        
        self.assertFalse(is_valid)
        self.assertIn("You are not in a Git repository", error_msg)
    
    @patch('subprocess.run')
    def test_get_staged_diff_no_changes(self, mock_run):
        """Test handling when no staged changes exist"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        diff = self.git_ops.get_staged_diff()
        
        self.assertEqual(diff, "")
    
    @patch('subprocess.run')
    def test_get_staged_diff_git_error(self, mock_run):
        """Test error handling when git diff fails"""
        mock_run.return_value = Mock(returncode=1, stderr="fatal: git error")
        
        with self.assertRaises(GitOperationError) as context:
            self.git_ops.get_staged_diff()
        
        self.assertIn("Error getting diff", str(context.exception))
    
    @patch('subprocess.run')
    def test_commit_with_message_failure(self, mock_run):
        """Test error handling when git commit fails"""
        mock_run.return_value = Mock(returncode=1, stderr="fatal: commit failed")
        
        success, error_msg = self.git_ops.commit_with_message("test commit")
        
        self.assertFalse(success)
        self.assertIn("Error executing commit", error_msg)


class TestGroqAPIErrorHandling(unittest.TestCase):
    """Test Groq API error handling scenarios"""
    
    def setUp(self):
        from config import Config
        config = Config()
        config.GROQ_API_KEY = "gsk_test-api-key-1234567890abcdef"  # Valid format
        self.client = GroqClient(config)
    
    def test_missing_api_key(self):
        """Test error handling when API key is missing"""
        from config import Config
        config = Config()
        config.GROQ_API_KEY = ""
        
        with self.assertRaises(GroqAPIError) as context:
            client = GroqClient(config)
        
        self.assertIn("GROQ_API_KEY environment variable is not configured", str(context.exception))
    
    @patch('requests.post')
    def test_api_connection_timeout(self, mock_post):
        """Test error handling for API connection timeout"""
        mock_post.side_effect = Exception("Connection timeout")
        
        with self.assertRaises(GroqAPIError) as context:
            self.client.generate_commit_message("test diff")
        
        self.assertIn("Unexpected error", str(context.exception))
    
    @patch('requests.post')
    def test_api_invalid_response(self, mock_post):
        """Test error handling for invalid API response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "response"}
        mock_post.return_value = mock_response
        
        with self.assertRaises(GroqAPIError) as context:
            self.client.generate_commit_message("test diff")
        
        self.assertIn("No choices in API response", str(context.exception))
    
    @patch('requests.post')
    def test_api_http_error(self, mock_post):
        """Test error handling for HTTP errors"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        with self.assertRaises(GroqAPIError) as context:
            self.client.generate_commit_message("test diff")
        
        self.assertIn("Invalid API key", str(context.exception))
    
    @patch('requests.post')
    def test_is_api_available_connection_error(self, mock_post):
        """Test API availability check with connection error"""
        mock_post.side_effect = Exception("Connection error")
        
        is_available = self.client.is_api_available()
        
        self.assertFalse(is_available)


class TestMessageGeneratorErrorHandling(unittest.TestCase):
    """Test message generator error handling scenarios"""
    
    def setUp(self):
        from config import Config
        config = Config()
        self.generator = MessageGenerator(config)
    
    @patch.object(GroqClient, 'generate_commit_message')
    def test_fallback_when_api_fails(self, mock_generate):
        """Test fallback message generation when API fails"""
        mock_generate.side_effect = GroqAPIError("API failed")
        
        message = self.generator.generate_message("test diff", ["file1.py", "file2.py"])
        
        # Should generate fallback message - Python files default to 'feat'
        self.assertIn("feat:", message)
        self.assertIn("file1.py", message)
    
    def test_fallback_message_single_file(self):
        """Test fallback message for single file"""
        message = self.generator.generate_fallback_message(["main.py"])
        
        # Python files default to 'feat' type
        self.assertEqual(message, "feat: update main.py")
    
    def test_fallback_message_multiple_files(self):
        """Test fallback message for multiple files"""
        files = ["file1.py", "file2.py", "file3.py"]
        message = self.generator.generate_fallback_message(files)
        
        # Python files default to 'feat' type
        self.assertEqual(message, "feat: update file1.py, file2.py, file3.py")
    
    def test_fallback_message_many_files(self):
        """Test fallback message for many files"""
        files = [f"file{i}.py" for i in range(5)]
        message = self.generator.generate_fallback_message(files)
        
        # Python files default to 'feat' type
        self.assertEqual(message, "feat: update 5 files")


class TestCommitBuddyErrorHandling(unittest.TestCase):
    """Test main CommitBuddy error handling scenarios"""
    
    def setUp(self):
        self.commit_buddy = CommitBuddy()
    
    @patch.object(GitOperations, 'validate_git_environment')
    def test_handle_from_diff_invalid_git_env(self, mock_validate):
        """Test error handling for invalid Git environment"""
        mock_validate.return_value = (False, "You are not in a Git repository")
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 1)  # Error exit code
    
    @patch.object(GitOperations, 'validate_git_environment')
    @patch.object(GitOperations, 'get_staged_diff')
    def test_handle_from_diff_no_staged_changes(self, mock_diff, mock_validate):
        """Test handling when no staged changes exist"""
        mock_validate.return_value = (True, "")
        mock_diff.return_value = ""
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 0)  # Success exit code (no error, just no changes)
    
    @patch.object(GitOperations, 'validate_git_environment')
    @patch.object(GitOperations, 'check_staged_changes')
    @patch.object(GitOperations, 'get_staged_diff')
    @patch.object(MessageGenerator, 'generate_message')
    @patch.object(UserInterface, 'show_proposed_message')
    @patch.object(UserInterface, 'show_info')
    @patch.object(UserInterface, 'show_diff_summary')
    @patch.object(UserInterface, 'show_error')
    @patch.object(GitOperations, 'commit_with_message')
    def test_handle_from_diff_commit_failure(self, mock_commit, mock_error, mock_summary, 
                                           mock_info, mock_show, mock_generate, 
                                           mock_diff, mock_check, mock_validate):
        """Test error handling when git commit fails"""
        mock_validate.return_value = (True, "")
        mock_check.return_value = (True, "Changes found", ["test.py"])
        mock_diff.return_value = "test diff"
        mock_generate.return_value = "feat: add test feature"
        mock_show.return_value = 'y'  # User confirms
        mock_commit.return_value = (False, "Error executing commit")
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 1)  # Error exit code


class TestConfigErrorHandling(unittest.TestCase):
    """Test configuration error handling scenarios"""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_groq_api_key(self):
        """Test handling when GROQ_API_KEY is not set"""
        from config import Config
        config = Config()
        
        self.assertFalse(config.has_groq_api_key())
    
    @patch.dict(os.environ, {'GROQ_API_KEY': ''})
    def test_empty_groq_api_key(self):
        """Test handling when GROQ_API_KEY is empty"""
        from config import Config
        config = Config()
        
        self.assertFalse(config.has_groq_api_key())


class TestUserInterfaceErrorHandling(unittest.TestCase):
    """Test user interface error handling scenarios"""
    
    def setUp(self):
        self.ui = UserInterface()
    
    @patch('builtins.input')
    def test_show_proposed_message_invalid_input(self, mock_input):
        """Test handling of invalid user input"""
        # Simulate invalid input followed by valid input
        mock_input.side_effect = ['invalid', 'x', 'y']
        
        result = self.ui.show_proposed_message("test: commit message")
        
        self.assertTrue(result)  # Should eventually get valid input
    
    @patch('builtins.input')
    def test_allow_message_editing_empty_input(self, mock_input):
        """Test handling of empty input during message editing"""
        mock_input.return_value = ""
        
        result = self.ui.allow_message_editing("original message")
        
        self.assertEqual(result, "original message")  # Should return original if empty


if __name__ == '__main__':
    unittest.main()