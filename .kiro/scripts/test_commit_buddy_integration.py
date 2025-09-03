#!/usr/bin/env python3
"""
Integration tests for CommitBuddy main CLI handler
Tests the complete workflow orchestration
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from io import StringIO

# Add the scripts directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from commit_buddy import CommitBuddy
from config import Config
from git_operations import GitOperations
from message_generator import MessageGenerator
from user_interface import UserInterface


class TestCommitBuddyIntegration(unittest.TestCase):
    """Integration tests for CommitBuddy main workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.commit_buddy = CommitBuddy()
        
        # Mock all external dependencies
        self.git_ops_mock = Mock(spec=GitOperations)
        self.ui_mock = Mock(spec=UserInterface)
        self.config_mock = Mock(spec=Config)
        self.message_gen_mock = Mock(spec=MessageGenerator)
        
        # Replace instances with mocks
        self.commit_buddy.git_ops = self.git_ops_mock
        self.commit_buddy.ui = self.ui_mock
        self.commit_buddy.config = self.config_mock
    
    def test_main_with_from_diff_argument(self):
        """Test main method with --from-diff argument"""
        with patch.object(self.commit_buddy, 'handle_from_diff', return_value=0) as mock_handle:
            result = self.commit_buddy.main(['--from-diff'])
            
            self.assertEqual(result, 0)
            mock_handle.assert_called_once()
    
    def test_main_without_arguments_shows_help(self):
        """Test main method without arguments shows help"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = self.commit_buddy.main([])
            
            self.assertEqual(result, 0)
            output = mock_stdout.getvalue()
            self.assertIn('usage:', output.lower())
            self.assertIn('--from-diff', output)
    
    def test_handle_from_diff_not_git_repository(self):
        """Test handle_from_diff when not in Git repository"""
        self.git_ops_mock.is_git_repository.return_value = False
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 1)
        self.git_ops_mock.is_git_repository.assert_called_once()
        self.ui_mock.show_error.assert_called_once_with("No estás en un repositorio Git")
    
    def test_handle_from_diff_no_staged_changes(self):
        """Test handle_from_diff when no staged changes"""
        self.git_ops_mock.is_git_repository.return_value = True
        self.git_ops_mock.get_staged_diff.return_value = ""
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 0)
        self.git_ops_mock.is_git_repository.assert_called_once()
        self.git_ops_mock.get_staged_diff.assert_called_once()
        self.ui_mock.show_info.assert_called_once_with("No hay cambios staged para commit. Usa 'git add' primero.")
    
    def test_handle_from_diff_empty_staged_changes(self):
        """Test handle_from_diff when staged changes are only whitespace"""
        self.git_ops_mock.is_git_repository.return_value = True
        self.git_ops_mock.get_staged_diff.return_value = "   \n  \t  \n"
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 0)
        self.ui_mock.show_info.assert_called_once_with("No hay cambios staged para commit. Usa 'git add' primero.")
    
    @patch('commit_buddy.MessageGenerator')
    def test_handle_from_diff_successful_flow_with_confirmation(self, mock_msg_gen_class):
        """Test complete successful flow with user confirmation"""
        # Setup mocks
        self.git_ops_mock.is_git_repository.return_value = True
        self.git_ops_mock.get_staged_diff.return_value = "diff --git a/file.py b/file.py\n+new line"
        self.git_ops_mock.get_changed_files.return_value = ["file.py"]
        self.git_ops_mock.commit_with_message.return_value = True
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = "feat: add new functionality"
        mock_msg_gen_class.return_value = mock_msg_gen
        
        self.ui_mock.show_proposed_message.return_value = 'y'
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 0)
        
        # Verify the complete flow
        self.git_ops_mock.is_git_repository.assert_called_once()
        self.git_ops_mock.get_staged_diff.assert_called_once()
        self.git_ops_mock.get_changed_files.assert_called_once()
        self.ui_mock.show_diff_summary.assert_called_once_with(["file.py"])
        mock_msg_gen.generate_message.assert_called_once()
        self.ui_mock.show_proposed_message.assert_called_once_with("feat: add new functionality")
        self.ui_mock.show_info.assert_called_once_with("Ejecutando commit...")
        self.git_ops_mock.commit_with_message.assert_called_once_with("feat: add new functionality")
        self.ui_mock.show_success.assert_called_once()
    
    @patch('commit_buddy.MessageGenerator')
    def test_handle_from_diff_user_cancels(self, mock_msg_gen_class):
        """Test flow when user cancels the commit"""
        # Setup mocks
        self.git_ops_mock.is_git_repository.return_value = True
        self.git_ops_mock.get_staged_diff.return_value = "diff --git a/file.py b/file.py\n+new line"
        self.git_ops_mock.get_changed_files.return_value = ["file.py"]
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = "feat: add new functionality"
        mock_msg_gen_class.return_value = mock_msg_gen
        
        self.ui_mock.show_proposed_message.return_value = 'n'
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 0)
        self.ui_mock.show_info.assert_called_with("Commit cancelado")
        self.git_ops_mock.commit_with_message.assert_not_called()
    
    @patch('commit_buddy.MessageGenerator')
    def test_handle_from_diff_user_edits_message(self, mock_msg_gen_class):
        """Test flow when user edits the commit message"""
        # Setup mocks
        self.git_ops_mock.is_git_repository.return_value = True
        self.git_ops_mock.get_staged_diff.return_value = "diff --git a/file.py b/file.py\n+new line"
        self.git_ops_mock.get_changed_files.return_value = ["file.py"]
        self.git_ops_mock.commit_with_message.return_value = True
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = "feat: add new functionality"
        mock_msg_gen_class.return_value = mock_msg_gen
        
        # First call returns 'e' for edit, second call returns 'y' for confirm
        self.ui_mock.show_proposed_message.side_effect = ['e', 'y']
        self.ui_mock.allow_message_editing.return_value = "feat: add custom functionality"
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 0)
        
        # Verify editing flow
        self.assertEqual(self.ui_mock.show_proposed_message.call_count, 2)
        self.ui_mock.allow_message_editing.assert_called_once_with("feat: add new functionality")
        self.git_ops_mock.commit_with_message.assert_called_once_with("feat: add custom functionality")
    
    @patch('commit_buddy.MessageGenerator')
    def test_handle_from_diff_user_cancels_editing(self, mock_msg_gen_class):
        """Test flow when user cancels during message editing"""
        # Setup mocks
        self.git_ops_mock.is_git_repository.return_value = True
        self.git_ops_mock.get_staged_diff.return_value = "diff --git a/file.py b/file.py\n+new line"
        self.git_ops_mock.get_changed_files.return_value = ["file.py"]
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = "feat: add new functionality"
        mock_msg_gen_class.return_value = mock_msg_gen
        
        self.ui_mock.show_proposed_message.return_value = 'e'
        self.ui_mock.allow_message_editing.return_value = None  # User cancelled editing
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 0)
        self.ui_mock.show_info.assert_called_with("Commit cancelado")
        self.git_ops_mock.commit_with_message.assert_not_called()
    
    @patch('commit_buddy.MessageGenerator')
    def test_handle_from_diff_commit_fails(self, mock_msg_gen_class):
        """Test flow when git commit fails"""
        # Setup mocks
        self.git_ops_mock.is_git_repository.return_value = True
        self.git_ops_mock.get_staged_diff.return_value = "diff --git a/file.py b/file.py\n+new line"
        self.git_ops_mock.get_changed_files.return_value = ["file.py"]
        self.git_ops_mock.commit_with_message.return_value = False  # Commit fails
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = "feat: add new functionality"
        mock_msg_gen_class.return_value = mock_msg_gen
        
        self.ui_mock.show_proposed_message.return_value = 'y'
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 1)
        self.ui_mock.show_error.assert_called_with("Error ejecutando git commit. Verifica que los cambios estén staged correctamente.")
    
    @patch('commit_buddy.MessageGenerator')
    def test_handle_from_diff_message_generation_error_uses_fallback(self, mock_msg_gen_class):
        """Test flow when message generation fails and fallback is used"""
        # Setup mocks
        self.git_ops_mock.is_git_repository.return_value = True
        self.git_ops_mock.get_staged_diff.return_value = "diff --git a/file.py b/file.py\n+new line"
        self.git_ops_mock.get_changed_files.return_value = ["file.py"]
        self.git_ops_mock.commit_with_message.return_value = True
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.side_effect = Exception("API Error")
        mock_msg_gen.generate_fallback_message.return_value = "chore: update file.py"
        mock_msg_gen_class.return_value = mock_msg_gen
        
        self.ui_mock.show_proposed_message.return_value = 'y'
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 0)
        
        # Verify fallback was used
        mock_msg_gen.generate_message.assert_called_once()
        mock_msg_gen.generate_fallback_message.assert_called_once_with(["file.py"])
        self.ui_mock.show_warning.assert_called_once()
        self.git_ops_mock.commit_with_message.assert_called_once_with("chore: update file.py")
    
    def test_handle_from_diff_no_changed_files_warning(self):
        """Test flow when get_changed_files returns empty list"""
        self.git_ops_mock.is_git_repository.return_value = True
        self.git_ops_mock.get_staged_diff.return_value = "diff --git a/file.py b/file.py\n+new line"
        self.git_ops_mock.get_changed_files.return_value = []  # No files returned
        
        with patch('commit_buddy.MessageGenerator') as mock_msg_gen_class:
            mock_msg_gen = Mock()
            mock_msg_gen.generate_message.return_value = "chore: update files"
            mock_msg_gen_class.return_value = mock_msg_gen
            
            self.ui_mock.show_proposed_message.return_value = 'n'
            
            result = self.commit_buddy.handle_from_diff()
            
            self.assertEqual(result, 0)
            self.ui_mock.show_warning.assert_called_once_with("No se pudieron obtener los archivos modificados")
            self.ui_mock.show_diff_summary.assert_called_once_with([])
    
    def test_handle_from_diff_keyboard_interrupt(self):
        """Test flow when user presses Ctrl+C"""
        self.git_ops_mock.is_git_repository.return_value = True
        self.git_ops_mock.get_staged_diff.side_effect = KeyboardInterrupt()
        
        with patch('builtins.print') as mock_print:
            result = self.commit_buddy.handle_from_diff()
            
            self.assertEqual(result, 0)
            mock_print.assert_called_once()  # New line after Ctrl+C
            self.ui_mock.show_info.assert_called_once_with("Operación cancelada por el usuario")
    
    def test_handle_from_diff_unexpected_error(self):
        """Test flow when unexpected error occurs"""
        self.git_ops_mock.is_git_repository.side_effect = Exception("Unexpected error")
        
        result = self.commit_buddy.handle_from_diff()
        
        self.assertEqual(result, 1)
        self.ui_mock.show_error.assert_called_once_with("Error inesperado: Unexpected error")


class TestCommitBuddyArgumentParsing(unittest.TestCase):
    """Test argument parsing functionality"""
    
    def setUp(self):
        self.commit_buddy = CommitBuddy()
    
    def test_argument_parsing_from_diff(self):
        """Test parsing --from-diff argument"""
        with patch.object(self.commit_buddy, 'handle_from_diff', return_value=0) as mock_handle:
            result = self.commit_buddy.main(['--from-diff'])
            
            self.assertEqual(result, 0)
            mock_handle.assert_called_once()
    
    def test_argument_parsing_help(self):
        """Test help argument shows usage"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as cm:
                self.commit_buddy.main(['--help'])
            
            self.assertEqual(cm.exception.code, 0)
            output = mock_stdout.getvalue()
            self.assertIn('AI-powered commit message generator', output)
            self.assertIn('--from-diff', output)
    
    def test_argument_parsing_invalid_argument(self):
        """Test invalid argument shows error"""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit) as cm:
                self.commit_buddy.main(['--invalid'])
            
            self.assertEqual(cm.exception.code, 2)
            output = mock_stderr.getvalue()
            self.assertIn('unrecognized arguments', output)


if __name__ == '__main__':
    unittest.main()