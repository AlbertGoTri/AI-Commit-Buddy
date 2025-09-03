#!/usr/bin/env python3
"""
End-to-end workflow tests for CommitBuddy
Tests the complete integration with real-like scenarios
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
import tempfile
import subprocess

# Add the scripts directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from commit_buddy import CommitBuddy


class TestE2EWorkflow(unittest.TestCase):
    """End-to-end workflow tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.commit_buddy = CommitBuddy()
    
    @patch('subprocess.run')
    @patch('commit_buddy.MessageGenerator')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_complete_successful_workflow_with_api(self, mock_print, mock_input, mock_msg_gen_class, mock_subprocess):
        """Test complete workflow with API success"""
        # Mock subprocess calls for Git operations
        mock_subprocess.side_effect = [
            # is_git_repository call
            Mock(returncode=0, stdout="", stderr=""),
            # get_staged_diff call
            Mock(returncode=0, stdout="diff --git a/test.py b/test.py\nindex 1234567..abcdefg 100644\n--- a/test.py\n+++ b/test.py\n@@ -1,3 +1,4 @@\n def hello():\n     print('hello')\n+    print('world')\n", stderr=""),
            # get_changed_files call
            Mock(returncode=0, stdout="test.py\n", stderr=""),
            # commit_with_message call
            Mock(returncode=0, stdout="[main abc1234] feat: add world greeting\n 1 file changed, 1 insertion(+)\n", stderr="")
        ]
        
        # Mock message generator
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = "feat: add world greeting"
        mock_msg_gen_class.return_value = mock_msg_gen
        
        # Mock user input (confirm the message)
        mock_input.return_value = "y"
        
        # Execute the workflow
        result = self.commit_buddy.handle_from_diff()
        
        # Verify result
        self.assertEqual(result, 0)
        
        # Verify Git operations were called correctly
        expected_calls = [
            call(['git', 'rev-parse', '--git-dir'], capture_output=True, text=True, timeout=5),
            call(['git', 'diff', '--staged'], capture_output=True, text=True, timeout=10),
            call(['git', 'diff', '--staged', '--name-only'], capture_output=True, text=True, timeout=10),
            call(['git', 'commit', '-m', 'feat: add world greeting'], capture_output=True, text=True, timeout=15)
        ]
        mock_subprocess.assert_has_calls(expected_calls)
        
        # Verify message generation was called
        mock_msg_gen.generate_message.assert_called_once()
        
        # Verify user was prompted and success was shown
        self.assertTrue(any("Mensaje de commit propuesto" in str(call) for call in mock_print.call_args_list))
        self.assertTrue(any("Commit creado exitosamente" in str(call) for call in mock_print.call_args_list))
    
    @patch('subprocess.run')
    @patch('commit_buddy.MessageGenerator')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_complete_workflow_with_fallback(self, mock_print, mock_input, mock_msg_gen_class, mock_subprocess):
        """Test complete workflow when API fails and fallback is used"""
        # Mock subprocess calls for Git operations
        mock_subprocess.side_effect = [
            # is_git_repository call
            Mock(returncode=0, stdout="", stderr=""),
            # get_staged_diff call
            Mock(returncode=0, stdout="diff --git a/config.json b/config.json\nindex 1234567..abcdefg 100644\n--- a/config.json\n+++ b/config.json\n@@ -1,3 +1,4 @@\n {\n   \"setting\": \"value\"\n+  \"new_setting\": \"new_value\"\n }\n", stderr=""),
            # get_changed_files call
            Mock(returncode=0, stdout="config.json\n", stderr=""),
            # commit_with_message call
            Mock(returncode=0, stdout="[main def5678] chore: update config.json\n 1 file changed, 1 insertion(+)\n", stderr="")
        ]
        
        # Mock message generator with API failure
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.side_effect = Exception("API Error")
        mock_msg_gen.generate_fallback_message.return_value = "chore: update config.json"
        mock_msg_gen_class.return_value = mock_msg_gen
        
        # Mock user input (confirm the fallback message)
        mock_input.return_value = "y"
        
        # Execute the workflow
        result = self.commit_buddy.handle_from_diff()
        
        # Verify result
        self.assertEqual(result, 0)
        
        # Verify fallback was used
        mock_msg_gen.generate_message.assert_called_once()
        mock_msg_gen.generate_fallback_message.assert_called_once_with(["config.json"])
        
        # Verify commit was made with fallback message
        commit_call = call(['git', 'commit', '-m', 'chore: update config.json'], capture_output=True, text=True, timeout=15)
        self.assertIn(commit_call, mock_subprocess.call_args_list)
        
        # Verify warning was shown about API error
        self.assertTrue(any("Error generando mensaje" in str(call) for call in mock_print.call_args_list))
    
    @patch('subprocess.run')
    @patch('commit_buddy.MessageGenerator')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_workflow_with_message_editing(self, mock_print, mock_input, mock_msg_gen_class, mock_subprocess):
        """Test workflow when user edits the commit message"""
        # Mock subprocess calls for Git operations
        mock_subprocess.side_effect = [
            # is_git_repository call
            Mock(returncode=0, stdout="", stderr=""),
            # get_staged_diff call
            Mock(returncode=0, stdout="diff --git a/feature.py b/feature.py\nindex 1234567..abcdefg 100644\n--- a/feature.py\n+++ b/feature.py\n@@ -1,3 +1,6 @@\n def new_feature():\n-    pass\n+    print('implementing feature')\n+    return True\n", stderr=""),
            # get_changed_files call
            Mock(returncode=0, stdout="feature.py\n", stderr=""),
            # commit_with_message call
            Mock(returncode=0, stdout="[main ghi9012] feat: implement awesome new feature\n 1 file changed, 3 insertions(+), 1 deletion(-)\n", stderr="")
        ]
        
        # Mock message generator
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = "feat: implement new feature"
        mock_msg_gen_class.return_value = mock_msg_gen
        
        # Mock user input: first 'e' for edit, then 'y' for confirm, then the edited message
        mock_input.side_effect = [
            "e",  # Choose to edit
            "feat: implement awesome new feature",  # Edited message
            "",   # End editing
            "y"   # Confirm edited message
        ]
        
        # Execute the workflow
        result = self.commit_buddy.handle_from_diff()
        
        # Verify result
        self.assertEqual(result, 0)
        
        # Verify commit was made with edited message
        commit_call = call(['git', 'commit', '-m', 'feat: implement awesome new feature'], capture_output=True, text=True, timeout=15)
        self.assertIn(commit_call, mock_subprocess.call_args_list)
        
        # Verify editing interface was shown
        self.assertTrue(any("Editando mensaje de commit" in str(call) for call in mock_print.call_args_list))
    
    @patch('subprocess.run')
    @patch('builtins.print')
    def test_workflow_error_scenarios(self, mock_print, mock_subprocess):
        """Test various error scenarios"""
        # Test 1: Not a Git repository
        mock_subprocess.return_value = Mock(returncode=1, stdout="", stderr="fatal: not a git repository")
        
        result = self.commit_buddy.handle_from_diff()
        self.assertEqual(result, 1)
        
        # Test 2: No staged changes
        mock_subprocess.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # is_git_repository
            Mock(returncode=0, stdout="", stderr="")   # get_staged_diff (empty)
        ]
        
        result = self.commit_buddy.handle_from_diff()
        self.assertEqual(result, 0)
        
        # Verify appropriate messages were shown
        self.assertTrue(any("No hay cambios staged" in str(call) for call in mock_print.call_args_list))
    
    @patch('subprocess.run')
    @patch('commit_buddy.MessageGenerator')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_workflow_commit_failure(self, mock_print, mock_input, mock_msg_gen_class, mock_subprocess):
        """Test workflow when git commit fails"""
        # Mock subprocess calls with commit failure
        mock_subprocess.side_effect = [
            # is_git_repository call
            Mock(returncode=0, stdout="", stderr=""),
            # get_staged_diff call
            Mock(returncode=0, stdout="diff --git a/test.py b/test.py\n+new line", stderr=""),
            # get_changed_files call
            Mock(returncode=0, stdout="test.py\n", stderr=""),
            # commit_with_message call (fails)
            Mock(returncode=1, stdout="", stderr="error: pathspec 'test.py' did not match any files")
        ]
        
        # Mock message generator
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = "feat: add new line"
        mock_msg_gen_class.return_value = mock_msg_gen
        
        # Mock user input (confirm the message)
        mock_input.return_value = "y"
        
        # Execute the workflow
        result = self.commit_buddy.handle_from_diff()
        
        # Verify result is error
        self.assertEqual(result, 1)
        
        # Verify error message was shown
        self.assertTrue(any("Error ejecutando git commit" in str(call) for call in mock_print.call_args_list))


class TestCLIIntegration(unittest.TestCase):
    """Test CLI integration and argument handling"""
    
    def test_cli_main_entry_point(self):
        """Test that main entry point works correctly"""
        commit_buddy = CommitBuddy()
        
        # Test help functionality
        with patch('sys.stdout') as mock_stdout:
            result = commit_buddy.main([])
            self.assertEqual(result, 0)
    
    def test_cli_argument_validation(self):
        """Test CLI argument validation"""
        commit_buddy = CommitBuddy()
        
        # Test with --from-diff argument
        with patch.object(commit_buddy, 'handle_from_diff', return_value=0) as mock_handle:
            result = commit_buddy.main(['--from-diff'])
            self.assertEqual(result, 0)
            mock_handle.assert_called_once()


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)