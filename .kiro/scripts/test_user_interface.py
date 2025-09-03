"""
Unit tests for UserInterface class
Tests all user interaction and display functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import io
from user_interface import UserInterface


class TestUserInterface(unittest.TestCase):
    """Test cases for UserInterface class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ui = UserInterface()
    
    def test_init_colors_disabled_when_not_tty(self):
        """Test that colors are disabled when not in a TTY"""
        with patch('sys.stdout.isatty', return_value=False):
            ui = UserInterface()
            self.assertFalse(ui.colors_enabled)
    
    def test_init_colors_enabled_when_tty_and_colorama_available(self):
        """Test that colors are enabled when in TTY and colorama is available"""
        with patch('sys.stdout.isatty', return_value=True):
            with patch('user_interface.COLORS_AVAILABLE', True):
                ui = UserInterface()
                self.assertTrue(ui.colors_enabled)
    
    def test_colorize_with_colors_enabled(self):
        """Test colorize method when colors are enabled"""
        self.ui.colors_enabled = True
        with patch('user_interface.COLORS_AVAILABLE', True):
            with patch('user_interface.Fore') as mock_fore:
                with patch('user_interface.Style') as mock_style:
                    mock_fore.RED = '\033[31m'
                    mock_style.BRIGHT = '\033[1m'
                    mock_style.RESET_ALL = '\033[0m'
                    
                    result = self.ui._colorize("test", mock_fore.RED, mock_style.BRIGHT)
                    expected = f"{mock_style.BRIGHT}{mock_fore.RED}test{mock_style.RESET_ALL}"
                    self.assertEqual(result, expected)
    
    def test_colorize_with_colors_disabled(self):
        """Test colorize method when colors are disabled"""
        self.ui.colors_enabled = False
        result = self.ui._colorize("test", "color", "style")
        self.assertEqual(result, "test")
    
    @patch('builtins.input', return_value='y')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_proposed_message_accept(self, mock_stdout, mock_input):
        """Test show_proposed_message with user accepting"""
        result = self.ui.show_proposed_message("feat: add new feature")
        self.assertEqual(result, 'y')
        output = mock_stdout.getvalue()
        self.assertIn("Mensaje de commit propuesto", output)
        self.assertIn("feat: add new feature", output)
    
    @patch('builtins.input', return_value='n')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_proposed_message_reject(self, mock_stdout, mock_input):
        """Test show_proposed_message with user rejecting"""
        result = self.ui.show_proposed_message("feat: add new feature")
        self.assertEqual(result, 'n')
    
    @patch('builtins.input', return_value='e')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_proposed_message_edit(self, mock_stdout, mock_input):
        """Test show_proposed_message with user choosing to edit"""
        result = self.ui.show_proposed_message("feat: add new feature")
        self.assertEqual(result, 'e')
    
    @patch('builtins.input', return_value='')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_proposed_message_default_accept(self, mock_stdout, mock_input):
        """Test show_proposed_message with empty input (default accept)"""
        result = self.ui.show_proposed_message("feat: add new feature")
        self.assertEqual(result, 'y')
    
    @patch('builtins.input', side_effect=['invalid', 'y'])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_proposed_message_invalid_then_valid(self, mock_stdout, mock_input):
        """Test show_proposed_message with invalid input then valid"""
        result = self.ui.show_proposed_message("feat: add new feature")
        self.assertEqual(result, 'y')
        output = mock_stdout.getvalue()
        self.assertIn("Por favor ingresa", output)
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_proposed_message_keyboard_interrupt(self, mock_stdout, mock_input):
        """Test show_proposed_message with keyboard interrupt"""
        result = self.ui.show_proposed_message("feat: add new feature")
        self.assertEqual(result, 'n')
    
    @patch('builtins.input', side_effect=['fix: updated functionality', ''])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_allow_message_editing_success(self, mock_stdout, mock_input):
        """Test allow_message_editing with successful edit"""
        result = self.ui.allow_message_editing("feat: original message")
        self.assertEqual(result, "fix: updated functionality")
        output = mock_stdout.getvalue()
        self.assertIn("Editando mensaje de commit", output)
        self.assertIn("feat: original message", output)
    
    @patch('builtins.input', side_effect=['', ''])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_allow_message_editing_empty_message(self, mock_stdout, mock_input):
        """Test allow_message_editing with empty message returns original"""
        original = "feat: original message"
        result = self.ui.allow_message_editing(original)
        self.assertEqual(result, original)
        output = mock_stdout.getvalue()
        self.assertIn("Mensaje vacío, usando mensaje original", output)
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_allow_message_editing_cancelled(self, mock_stdout, mock_input):
        """Test allow_message_editing with cancellation"""
        result = self.ui.allow_message_editing("feat: original message")
        self.assertIsNone(result)
        output = mock_stdout.getvalue()
        self.assertIn("Edición cancelada", output)
    
    @patch('builtins.input', side_effect=['line 1', 'line 2', ''])
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_allow_message_editing_multiline(self, mock_stdout, mock_input):
        """Test allow_message_editing with multiline input"""
        result = self.ui.allow_message_editing("original")
        self.assertEqual(result, "line 1\nline 2")
    
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_show_error(self, mock_stderr):
        """Test show_error displays error message"""
        self.ui.show_error("Test error message")
        output = mock_stderr.getvalue()
        self.assertIn("Test error message", output)
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_success(self, mock_stdout):
        """Test show_success displays success message"""
        self.ui.show_success("Test success message")
        output = mock_stdout.getvalue()
        self.assertIn("Test success message", output)
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_info(self, mock_stdout):
        """Test show_info displays info message"""
        self.ui.show_info("Test info message")
        output = mock_stdout.getvalue()
        self.assertIn("Test info message", output)
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_warning(self, mock_stdout):
        """Test show_warning displays warning message"""
        self.ui.show_warning("Test warning message")
        output = mock_stdout.getvalue()
        self.assertIn("Test warning message", output)
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_diff_summary_with_files(self, mock_stdout):
        """Test show_diff_summary displays file list"""
        files = ["file1.py", "file2.js", "file3.md"]
        self.ui.show_diff_summary(files, additions=10, deletions=5)
        output = mock_stdout.getvalue()
        self.assertIn("Archivos modificados", output)
        self.assertIn("file1.py", output)
        self.assertIn("file2.js", output)
        self.assertIn("file3.md", output)
        self.assertIn("+10", output)
        self.assertIn("-5", output)
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_diff_summary_many_files(self, mock_stdout):
        """Test show_diff_summary with many files shows truncation"""
        files = [f"file{i}.py" for i in range(10)]
        self.ui.show_diff_summary(files)
        output = mock_stdout.getvalue()
        self.assertIn("archivos más", output)
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_diff_summary_empty_files(self, mock_stdout):
        """Test show_diff_summary with empty file list"""
        self.ui.show_diff_summary([])
        output = mock_stdout.getvalue()
        self.assertEqual(output, "")
    
    @patch('builtins.input', return_value='y')
    def test_confirm_action_yes(self, mock_input):
        """Test confirm_action with yes response"""
        result = self.ui.confirm_action("Continue?")
        self.assertTrue(result)
    
    @patch('builtins.input', return_value='n')
    def test_confirm_action_no(self, mock_input):
        """Test confirm_action with no response"""
        result = self.ui.confirm_action("Continue?")
        self.assertFalse(result)
    
    @patch('builtins.input', return_value='')
    def test_confirm_action_default_true(self, mock_input):
        """Test confirm_action with empty input and default True"""
        result = self.ui.confirm_action("Continue?", default=True)
        self.assertTrue(result)
    
    @patch('builtins.input', return_value='')
    def test_confirm_action_default_false(self, mock_input):
        """Test confirm_action with empty input and default False"""
        result = self.ui.confirm_action("Continue?", default=False)
        self.assertFalse(result)
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    def test_confirm_action_keyboard_interrupt(self, mock_input):
        """Test confirm_action with keyboard interrupt"""
        result = self.ui.confirm_action("Continue?")
        self.assertFalse(result)
    
    def test_show_error_without_colors(self):
        """Test show_error when colors are disabled"""
        self.ui.colors_enabled = False
        with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            self.ui.show_error("Test error")
            output = mock_stderr.getvalue()
            self.assertIn("ERROR:", output)
            self.assertIn("Test error", output)
    
    def test_show_success_without_colors(self):
        """Test show_success when colors are disabled"""
        self.ui.colors_enabled = False
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            self.ui.show_success("Test success")
            output = mock_stdout.getvalue()
            self.assertIn("SUCCESS:", output)
            self.assertIn("Test success", output)


if __name__ == '__main__':
    unittest.main()