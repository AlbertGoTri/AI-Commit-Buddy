"""
Unit tests for MessageGenerator class
Tests AI-powered and fallback message generation functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add the scripts directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from message_generator import MessageGenerator
from config import Config
from groq_client import GroqAPIError


class TestMessageGenerator(unittest.TestCase):
    """Test cases for MessageGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = Mock(spec=Config)
        self.config.has_groq_api_key.return_value = True
        self.config.MAX_DIFF_SIZE = 8000
        
    def test_init_with_api_key(self):
        """Test MessageGenerator initialization with API key"""
        with patch('message_generator.GroqClient') as mock_groq:
            generator = MessageGenerator(self.config)
            
            self.config.has_groq_api_key.assert_called_once()
            mock_groq.assert_called_once_with(self.config)
            self.assertIsNotNone(generator.groq_client)
    
    def test_init_without_api_key(self):
        """Test MessageGenerator initialization without API key"""
        self.config.has_groq_api_key.return_value = False
        
        generator = MessageGenerator(self.config)
        
        self.assertIsNone(generator.groq_client)
    
    def test_init_with_groq_error(self):
        """Test MessageGenerator initialization when GroqClient raises error"""
        with patch('message_generator.GroqClient', side_effect=GroqAPIError("API error")):
            generator = MessageGenerator(self.config)
            
            self.assertIsNone(generator.groq_client)
    
    def test_validate_conventional_format_valid_messages(self):
        """Test validation of valid Conventional Commits messages"""
        generator = MessageGenerator(self.config)
        
        valid_messages = [
            "feat: add new user authentication",
            "fix: resolve login bug",
            "docs: update README with installation steps",
            "refactor: restructure user service",
            "test: add unit tests for auth module",
            "chore: update dependencies",
            "feat(auth): add OAuth integration",
            "fix(ui): correct button alignment",
            "FEAT: add new feature",  # Case insensitive
        ]
        
        for message in valid_messages:
            with self.subTest(message=message):
                self.assertTrue(generator.validate_conventional_format(message))
    
    def test_validate_conventional_format_invalid_messages(self):
        """Test validation of invalid Conventional Commits messages"""
        generator = MessageGenerator(self.config)
        
        invalid_messages = [
            "",
            "   ",
            "add new feature",  # No prefix
            "feature: add new feature",  # Wrong prefix
            "feat:",  # No description
            "feat: ",  # Empty description
            "feat add new feature",  # Missing colon
            None,
        ]
        
        for message in invalid_messages:
            with self.subTest(message=message):
                self.assertFalse(generator.validate_conventional_format(message))
    
    def test_generate_fallback_message_single_file(self):
        """Test fallback message generation for single file"""
        generator = MessageGenerator(self.config)
        
        files = ["src/main.py"]
        message = generator.generate_fallback_message(files)
        
        self.assertEqual(message, "feat: update main.py")
    
    def test_generate_fallback_message_multiple_files(self):
        """Test fallback message generation for multiple files"""
        generator = MessageGenerator(self.config)
        
        files = ["src/main.py", "src/utils.py", "tests/test_main.py"]
        message = generator.generate_fallback_message(files)
        
        self.assertEqual(message, "test: update main.py, utils.py, test_main.py")
    
    def test_generate_fallback_message_many_files(self):
        """Test fallback message generation for many files"""
        generator = MessageGenerator(self.config)
        
        files = [f"file{i}.py" for i in range(5)]
        message = generator.generate_fallback_message(files)
        
        self.assertEqual(message, "feat: update 5 files")
    
    def test_generate_fallback_message_empty_files(self):
        """Test fallback message generation for empty file list"""
        generator = MessageGenerator(self.config)
        
        files = []
        message = generator.generate_fallback_message(files)
        
        self.assertEqual(message, "chore: update files")
    
    def test_determine_commit_type_from_files_docs(self):
        """Test commit type determination for documentation files"""
        generator = MessageGenerator(self.config)
        
        files = ["README.md", "docs/api.md"]
        commit_type = generator._determine_commit_type_from_files(files)
        
        self.assertEqual(commit_type, "docs")
    
    def test_determine_commit_type_from_files_tests(self):
        """Test commit type determination for test files"""
        generator = MessageGenerator(self.config)
        
        files = ["test_main.py", "src/utils_test.js"]
        commit_type = generator._determine_commit_type_from_files(files)
        
        self.assertEqual(commit_type, "test")
    
    def test_determine_commit_type_from_files_config(self):
        """Test commit type determination for configuration files"""
        generator = MessageGenerator(self.config)
        
        files = ["config.json", "settings.yml"]
        commit_type = generator._determine_commit_type_from_files(files)
        
        self.assertEqual(commit_type, "chore")
    
    def test_determine_commit_type_from_files_source_code(self):
        """Test commit type determination for source code files"""
        generator = MessageGenerator(self.config)
        
        files = ["main.py", "utils.js"]
        commit_type = generator._determine_commit_type_from_files(files)
        
        self.assertEqual(commit_type, "feat")
    
    def test_should_use_ai_valid_diff(self):
        """Test AI usage decision for valid diff"""
        generator = MessageGenerator(self.config)
        
        diff = "--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,4 @@\n def func():\n+    print('hello')\n     pass"
        
        self.assertTrue(generator._should_use_ai(diff))
    
    def test_should_use_ai_empty_diff(self):
        """Test AI usage decision for empty diff"""
        generator = MessageGenerator(self.config)
        
        self.assertFalse(generator._should_use_ai(""))
        self.assertFalse(generator._should_use_ai("   "))
        self.assertFalse(generator._should_use_ai(None))
    
    def test_should_use_ai_large_diff(self):
        """Test AI usage decision for large diff"""
        generator = MessageGenerator(self.config)
        
        large_diff = "x" * (self.config.MAX_DIFF_SIZE + 1)
        
        self.assertFalse(generator._should_use_ai(large_diff))
    
    def test_should_use_ai_small_diff(self):
        """Test AI usage decision for very small diff"""
        generator = MessageGenerator(self.config)
        
        small_diff = "line1\nline2"  # Only 2 lines
        
        self.assertFalse(generator._should_use_ai(small_diff))
    
    def test_fix_conventional_format_with_prefix(self):
        """Test fixing message that already has conventional prefix"""
        generator = MessageGenerator(self.config)
        
        message = "feat: add new authentication system"
        files = ["auth.py"]
        
        fixed = generator._fix_conventional_format(message, files)
        
        self.assertEqual(fixed, "feat: add new authentication system")
    
    def test_fix_conventional_format_with_keywords(self):
        """Test fixing message based on content keywords"""
        generator = MessageGenerator(self.config)
        
        message = "implement new user registration"
        files = ["user.py"]
        
        fixed = generator._fix_conventional_format(message, files)
        
        self.assertEqual(fixed, "feat: implement new user registration")
    
    def test_fix_conventional_format_fix_keywords(self):
        """Test fixing message with fix keywords"""
        generator = MessageGenerator(self.config)
        
        message = "fix login bug in authentication"
        files = ["auth.py"]
        
        fixed = generator._fix_conventional_format(message, files)
        
        self.assertEqual(fixed, "fix: fix login bug in authentication")
    
    def test_fix_conventional_format_fallback_to_files(self):
        """Test fixing message by falling back to file-based determination"""
        generator = MessageGenerator(self.config)
        
        message = "update user interface"
        files = ["README.md"]
        
        fixed = generator._fix_conventional_format(message, files)
        
        self.assertEqual(fixed, "docs: update user interface")
    
    def test_fix_conventional_format_empty_message(self):
        """Test fixing empty message"""
        generator = MessageGenerator(self.config)
        
        self.assertIsNone(generator._fix_conventional_format("", ["file.py"]))
        self.assertIsNone(generator._fix_conventional_format("   ", ["file.py"]))
        self.assertIsNone(generator._fix_conventional_format(None, ["file.py"]))
    
    def test_generate_message_with_ai_success(self):
        """Test message generation with successful AI call"""
        mock_groq_client = Mock()
        mock_groq_client.is_api_available.return_value = True
        mock_groq_client.generate_commit_message.return_value = "feat: add new feature"
        
        generator = MessageGenerator(self.config)
        generator.groq_client = mock_groq_client
        
        diff = "--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,4 @@\n def func():\n+    print('hello')\n     pass"
        files = ["file.py"]
        
        message = generator.generate_message(diff, files)
        
        self.assertEqual(message, "feat: add new feature")
        mock_groq_client.generate_commit_message.assert_called_once_with(diff)
    
    def test_generate_message_with_ai_invalid_format(self):
        """Test message generation when AI returns invalid format"""
        mock_groq_client = Mock()
        mock_groq_client.is_api_available.return_value = True
        mock_groq_client.generate_commit_message.return_value = "add new feature"  # Invalid format
        
        generator = MessageGenerator(self.config)
        generator.groq_client = mock_groq_client
        
        diff = "--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,4 @@\n def func():\n+    print('hello')\n     pass"
        files = ["file.py"]
        
        message = generator.generate_message(diff, files)
        
        # Should fix the format
        self.assertEqual(message, "feat: add new feature")
    
    def test_generate_message_with_ai_error(self):
        """Test message generation when AI call fails"""
        mock_groq_client = Mock()
        mock_groq_client.is_api_available.return_value = True
        mock_groq_client.generate_commit_message.side_effect = GroqAPIError("API error")
        
        generator = MessageGenerator(self.config)
        generator.groq_client = mock_groq_client
        
        diff = "--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,4 @@\n def func():\n+    print('hello')\n     pass"
        files = ["file.py"]
        
        message = generator.generate_message(diff, files)
        
        # Should fall back to local generation
        self.assertEqual(message, "feat: update file.py")
    
    def test_generate_message_api_unavailable(self):
        """Test message generation when API is unavailable"""
        mock_groq_client = Mock()
        mock_groq_client.is_api_available.return_value = False
        
        generator = MessageGenerator(self.config)
        generator.groq_client = mock_groq_client
        
        diff = "--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,4 @@\n def func():\n+    print('hello')\n     pass"
        files = ["file.py"]
        
        message = generator.generate_message(diff, files)
        
        # Should fall back to local generation
        self.assertEqual(message, "feat: update file.py")
        mock_groq_client.generate_commit_message.assert_not_called()
    
    def test_generate_message_no_groq_client(self):
        """Test message generation without Groq client"""
        generator = MessageGenerator(self.config)
        generator.groq_client = None
        
        diff = "--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,4 @@\n def func():\n+    print('hello')\n     pass"
        files = ["file.py"]
        
        message = generator.generate_message(diff, files)
        
        # Should use fallback generation
        self.assertEqual(message, "feat: update file.py")
    
    def test_generate_message_small_diff(self):
        """Test message generation with diff too small for AI"""
        mock_groq_client = Mock()
        
        generator = MessageGenerator(self.config)
        generator.groq_client = mock_groq_client
        
        small_diff = "line1\nline2"  # Too small for AI
        files = ["file.py"]
        
        message = generator.generate_message(small_diff, files)
        
        # Should use fallback generation without calling AI
        self.assertEqual(message, "feat: update file.py")
        mock_groq_client.generate_commit_message.assert_not_called()


if __name__ == '__main__':
    unittest.main()