"""
Unit tests for GitOperations class
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess
from git_operations import GitOperations


class TestGitOperations(unittest.TestCase):
    """Test cases for GitOperations class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.git_ops = GitOperations()
    
    @patch('subprocess.run')
    def test_is_git_repository_valid(self, mock_run):
        """Test is_git_repository returns True for valid Git repository"""
        # Mock successful git rev-parse command
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.git_ops.is_git_repository()
        
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            timeout=5
        )
    
    @patch('subprocess.run')
    def test_is_git_repository_invalid(self, mock_run):
        """Test is_git_repository returns False for invalid Git repository"""
        # Mock failed git rev-parse command
        mock_run.return_value = MagicMock(returncode=128)
        
        result = self.git_ops.is_git_repository()
        
        self.assertFalse(result)
        mock_run.assert_called_once_with(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            timeout=5
        )
    
    @patch('subprocess.run')
    def test_is_git_repository_timeout(self, mock_run):
        """Test is_git_repository handles timeout gracefully"""
        # Mock timeout exception
        mock_run.side_effect = subprocess.TimeoutExpired(['git', 'rev-parse', '--git-dir'], 5)
        
        result = self.git_ops.is_git_repository()
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_is_git_repository_file_not_found(self, mock_run):
        """Test is_git_repository handles missing git command"""
        # Mock FileNotFoundError (git not installed)
        mock_run.side_effect = FileNotFoundError()
        
        result = self.git_ops.is_git_repository()
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_get_staged_diff_with_changes(self, mock_run):
        """Test get_staged_diff returns diff when there are staged changes"""
        expected_diff = """diff --git a/file.py b/file.py
index 1234567..abcdefg 100644
--- a/file.py
+++ b/file.py
@@ -1,3 +1,4 @@
 def hello():
+    print("world")
     pass
"""
        mock_run.return_value = MagicMock(returncode=0, stdout=expected_diff)
        
        result = self.git_ops.get_staged_diff()
        
        self.assertEqual(result, expected_diff)
        mock_run.assert_called_once_with(
            ['git', 'diff', '--staged'],
            capture_output=True,
            text=True,
            timeout=10
        )
    
    @patch('subprocess.run')
    def test_get_staged_diff_no_changes(self, mock_run):
        """Test get_staged_diff returns empty string when no staged changes"""
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        
        result = self.git_ops.get_staged_diff()
        
        self.assertEqual(result, "")
    
    @patch('subprocess.run')
    def test_get_staged_diff_git_error(self, mock_run):
        """Test get_staged_diff handles git command errors"""
        mock_run.return_value = MagicMock(returncode=128)
        
        result = self.git_ops.get_staged_diff()
        
        self.assertEqual(result, "")
    
    @patch('subprocess.run')
    def test_get_staged_diff_timeout(self, mock_run):
        """Test get_staged_diff handles timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired(['git', 'diff', '--staged'], 10)
        
        result = self.git_ops.get_staged_diff()
        
        self.assertEqual(result, "")
    
    @patch('subprocess.run')
    def test_get_changed_files_with_files(self, mock_run):
        """Test get_changed_files returns list of changed files"""
        mock_run.return_value = MagicMock(
            returncode=0, 
            stdout="file1.py\nfile2.js\nREADME.md\n"
        )
        
        result = self.git_ops.get_changed_files()
        
        self.assertEqual(result, ["file1.py", "file2.js", "README.md"])
        mock_run.assert_called_once_with(
            ['git', 'diff', '--staged', '--name-only'],
            capture_output=True,
            text=True,
            timeout=10
        )
    
    @patch('subprocess.run')
    def test_get_changed_files_no_files(self, mock_run):
        """Test get_changed_files returns empty list when no files changed"""
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        
        result = self.git_ops.get_changed_files()
        
        self.assertEqual(result, [])
    
    @patch('subprocess.run')
    def test_get_changed_files_single_file(self, mock_run):
        """Test get_changed_files with single file"""
        mock_run.return_value = MagicMock(returncode=0, stdout="single_file.py\n")
        
        result = self.git_ops.get_changed_files()
        
        self.assertEqual(result, ["single_file.py"])
    
    @patch('subprocess.run')
    def test_get_changed_files_git_error(self, mock_run):
        """Test get_changed_files handles git command errors"""
        mock_run.return_value = MagicMock(returncode=128)
        
        result = self.git_ops.get_changed_files()
        
        self.assertEqual(result, [])
    
    @patch('subprocess.run')
    def test_get_changed_files_timeout(self, mock_run):
        """Test get_changed_files handles timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired(['git', 'diff', '--staged', '--name-only'], 10)
        
        result = self.git_ops.get_changed_files()
        
        self.assertEqual(result, [])
    
    @patch('subprocess.run')
    def test_commit_with_message_success(self, mock_run):
        """Test commit_with_message returns True on successful commit"""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.git_ops.commit_with_message("feat: add new feature")
        
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['git', 'commit', '-m', 'feat: add new feature'],
            capture_output=True,
            text=True,
            timeout=15
        )
    
    @patch('subprocess.run')
    def test_commit_with_message_failure(self, mock_run):
        """Test commit_with_message returns False on commit failure"""
        mock_run.return_value = MagicMock(returncode=1)
        
        result = self.git_ops.commit_with_message("invalid commit")
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_commit_with_message_timeout(self, mock_run):
        """Test commit_with_message handles timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired(['git', 'commit', '-m', 'test'], 15)
        
        result = self.git_ops.commit_with_message("test message")
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_commit_with_message_file_not_found(self, mock_run):
        """Test commit_with_message handles missing git command"""
        mock_run.side_effect = FileNotFoundError()
        
        result = self.git_ops.commit_with_message("test message")
        
        self.assertFalse(result)
    
    def test_commit_with_message_empty_message(self):
        """Test commit_with_message with empty message"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            result = self.git_ops.commit_with_message("")
            
            self.assertTrue(result)
            mock_run.assert_called_once_with(
                ['git', 'commit', '-m', ''],
                capture_output=True,
                text=True,
                timeout=15
            )


if __name__ == '__main__':
    unittest.main()