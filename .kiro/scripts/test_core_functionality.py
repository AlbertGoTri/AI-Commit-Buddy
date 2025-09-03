#!/usr/bin/env python3
"""
Core functionality tests for Kiro Commit Buddy
Tests the essential features without complex mocking issues
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from pathlib import Path

# Add the scripts directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from message_generator import MessageGenerator
from user_interface import UserInterface
from git_operations import GitOperations
from test_fixtures import TestFixtures


class TestCoreMessageGeneration(unittest.TestCase):
    """Test core message generation functionality"""
    
    def test_fallback_message_generation(self):
        """Test fallback message generation works correctly"""
        config = TestFixtures.create_mock_config(has_api_key=False)
        
        # Create generator without API key to force fallback mode
        with patch('message_generator.GroqClient') as mock_groq_class:
            mock_groq_class.side_effect = Exception("No API key")
            generator = MessageGenerator(config)
            generator.groq_client = None  # Force fallback mode
            
            # Test single file
            message = generator.generate_fallback_message(['main.py'])
            self.assertTrue(message.startswith('feat:'))
            self.assertIn('main.py', message)
            
            # Test multiple files
            message = generator.generate_fallback_message(['file1.py', 'file2.py'])
            self.assertTrue(message.startswith('feat:'))
            self.assertIn('file1.py', message)
            
            # Test documentation files
            message = generator.generate_fallback_message(['README.md'])
            self.assertTrue(message.startswith('docs:'))
            
            # Test test files
            message = generator.generate_fallback_message(['test_main.py'])
            self.assertTrue(message.startswith('test:'))
            
            # Test config files
            message = generator.generate_fallback_message(['config.json'])
            self.assertTrue(message.startswith('chore:'))
    
    def test_conventional_format_validation(self):
        """Test conventional format validation"""
        config = TestFixtures.create_mock_config(has_api_key=False)
        
        with patch('message_generator.GroqClient') as mock_groq_class:
            mock_groq_class.side_effect = Exception("No API key")
            generator = MessageGenerator(config)
            generator.groq_client = None
            
            # Test valid messages
            valid_messages = [
                'feat: add new feature',
                'fix: resolve bug',
                'docs: update readme',
                'refactor: improve code',
                'test: add tests',
                'chore: update deps'
            ]
            
            for message in valid_messages:
                self.assertTrue(generator.validate_conventional_format(message), 
                              f"Should validate: {message}")
            
            # Test invalid messages
            invalid_messages = [
                'add new feature',  # No prefix
                'feat:',  # No description
                '',  # Empty
                None  # None
            ]
            
            for message in invalid_messages:
                self.assertFalse(generator.validate_conventional_format(message),
                               f"Should not validate: {message}")


class TestCoreUserInterface(unittest.TestCase):
    """Test core user interface functionality"""
    
    def test_message_display(self):
        """Test message display functionality"""
        ui = UserInterface()
        
        # Test that methods don't crash
        with patch('sys.stdout'):
            ui.show_info("Test info")
            ui.show_success("Test success")
            ui.show_warning("Test warning")
        
        with patch('sys.stderr'):
            ui.show_error("Test error")
        
        # Test diff summary
        with patch('sys.stdout'):
            ui.show_diff_summary(['file1.py', 'file2.py'])
            ui.show_diff_summary([])  # Empty list
    
    def test_user_confirmation(self):
        """Test user confirmation functionality"""
        ui = UserInterface()
        
        # Test confirmation with mocked input
        with patch('builtins.input', return_value='y'):
            result = ui.show_proposed_message("test: commit message")
            self.assertEqual(result, 'y')
        
        with patch('builtins.input', return_value='n'):
            result = ui.show_proposed_message("test: commit message")
            self.assertEqual(result, 'n')


class TestCoreGitOperations(unittest.TestCase):
    """Test core Git operations functionality"""
    
    def test_git_validation_methods(self):
        """Test Git validation methods"""
        git_ops = GitOperations()
        
        # Test with mocked successful git command
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            
            result = git_ops.is_git_repository()
            self.assertTrue(result)
        
        # Test with mocked failed git command
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=128, stdout="", stderr="not a git repository")
            
            result = git_ops.is_git_repository()
            self.assertFalse(result)
    
    def test_diff_operations(self):
        """Test diff operations"""
        git_ops = GitOperations()
        
        # Test with mocked diff output
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="diff content", stderr="")
            
            result = git_ops.get_staged_diff()
            self.assertEqual(result, "diff content")
        
        # Test with no diff
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            
            result = git_ops.get_staged_diff()
            self.assertEqual(result, "")


class TestCoreConfiguration(unittest.TestCase):
    """Test core configuration functionality"""
    
    def test_config_basic_properties(self):
        """Test basic configuration properties"""
        config = Config()
        
        # Test that basic properties exist and have expected values
        self.assertEqual(config.GROQ_MODEL, "llama3-70b-8192")
        self.assertEqual(config.MAX_DIFF_SIZE, 8000)
        self.assertEqual(config.TIMEOUT, 10)
        self.assertEqual(config.MAX_TOKENS, 150)
        self.assertEqual(config.TEMPERATURE, 0.3)
        
        # Test API key detection
        self.assertIsInstance(config.has_groq_api_key(), bool)
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_test_key_123'})
    def test_config_with_api_key(self):
        """Test configuration with API key set"""
        config = Config()
        
        self.assertTrue(config.has_groq_api_key())
        self.assertEqual(config.get_groq_api_key(), 'gsk_test_key_123')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_without_api_key(self):
        """Test configuration without API key"""
        config = Config()
        
        self.assertFalse(config.has_groq_api_key())


class TestRequirementsCompliance(unittest.TestCase):
    """Test that core requirements are met"""
    
    def test_requirement_1_cli_workflow_components(self):
        """Test that CLI workflow components exist"""
        # Test that main components can be imported and instantiated
        from commit_buddy import CommitBuddy
        
        commit_buddy = CommitBuddy()
        self.assertIsNotNone(commit_buddy)
        
        # Test that main method exists and handles arguments
        result = commit_buddy.main([])
        self.assertEqual(result, 0)  # Should show help and exit successfully
    
    def test_requirement_2_conventional_commits_support(self):
        """Test that conventional commits are supported"""
        config = TestFixtures.create_mock_config(has_api_key=False)
        
        with patch('message_generator.GroqClient') as mock_groq_class:
            mock_groq_class.side_effect = Exception("No API key")
            generator = MessageGenerator(config)
            generator.groq_client = None
            
            # Test that all required prefixes are supported
            required_prefixes = ['feat', 'fix', 'docs', 'refactor', 'test', 'chore']
            
            for prefix in required_prefixes:
                message = f"{prefix}: test message"
                self.assertTrue(generator.validate_conventional_format(message),
                              f"Should support {prefix} prefix")
    
    def test_requirement_3_fallback_mechanisms(self):
        """Test that fallback mechanisms work"""
        config = TestFixtures.create_mock_config(has_api_key=False)
        
        with patch('message_generator.GroqClient') as mock_groq_class:
            mock_groq_class.side_effect = Exception("No API key")
            generator = MessageGenerator(config)
            generator.groq_client = None
            
            # Test that fallback messages are generated
            files = ['main.py', 'utils.py']
            message = generator.generate_fallback_message(files)
            
            self.assertIsNotNone(message)
            self.assertTrue(any(prefix in message for prefix in ['feat', 'fix', 'docs', 'refactor', 'test', 'chore']))
            self.assertTrue(any(filename in message for filename in files))
    
    def test_requirement_4_api_key_handling(self):
        """Test that API key handling works"""
        # Test without API key
        config_no_key = Config()
        with patch.dict(os.environ, {}, clear=True):
            config_no_key = Config()
            self.assertFalse(config_no_key.has_groq_api_key())
        
        # Test with API key
        with patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_test_key'}):
            config_with_key = Config()
            self.assertTrue(config_with_key.has_groq_api_key())
    
    def test_requirement_5_kiro_integration_structure(self):
        """Test that Kiro integration structure exists"""
        # Test that the CLI can be invoked
        from commit_buddy import CommitBuddy
        
        commit_buddy = CommitBuddy()
        
        # Test --from-diff argument handling
        with patch.object(commit_buddy, 'handle_from_diff', return_value=0) as mock_handle:
            result = commit_buddy.main(['--from-diff'])
            self.assertEqual(result, 0)
            mock_handle.assert_called_once()
    
    def test_requirement_6_documentation_exists(self):
        """Test that documentation files exist"""
        # Check for key documentation files
        project_root = Path(__file__).parent.parent.parent
        
        readme_path = project_root / "README.md"
        self.assertTrue(readme_path.exists(), "README.md should exist")
        
        install_path = project_root / "INSTALLATION.md"
        self.assertTrue(install_path.exists(), "INSTALLATION.md should exist")
        
        trouble_path = project_root / "TROUBLESHOOTING.md"
        self.assertTrue(trouble_path.exists(), "TROUBLESHOOTING.md should exist")


def run_core_tests():
    """Run core functionality tests"""
    print("🚀 RUNNING CORE FUNCTIONALITY TESTS")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestCoreMessageGeneration,
        TestCoreUserInterface,
        TestCoreGitOperations,
        TestCoreConfiguration,
        TestRequirementsCompliance
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, descriptions=True)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("CORE FUNCTIONALITY TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
            print(f"  {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")
            print(f"  {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("\n✅ ALL CORE TESTS PASSED!")
        print("Core functionality is working correctly.")
    else:
        print("\n❌ SOME CORE TESTS FAILED!")
        print("Please review the failures above.")
    
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_core_tests()
    sys.exit(0 if success else 1)