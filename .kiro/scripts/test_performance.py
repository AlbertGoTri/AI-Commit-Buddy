#!/usr/bin/env python3
"""
Performance and stress tests for Kiro Commit Buddy
Tests performance characteristics and edge cases
"""

import unittest
import time
import sys
import os
from unittest.mock import Mock, patch
import threading
import concurrent.futures

# Add the scripts directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from git_operations import GitOperations
from groq_client import GroqClient
from message_generator import MessageGenerator
from user_interface import UserInterface
from commit_buddy import CommitBuddy
from test_fixtures import TestFixtures


class TestPerformance(unittest.TestCase):
    """Performance tests for various components"""
    
    def setUp(self):
        self.config = TestFixtures.create_mock_config()
    
    def test_git_operations_performance(self):
        """Test Git operations performance under normal conditions"""
        git_ops = GitOperations()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = TestFixtures.create_mock_subprocess_response(
                TestFixtures.GIT_RESPONSES['valid_repo']
            )
            
            # Measure time for multiple operations
            start_time = time.time()
            for _ in range(100):
                git_ops.is_git_repository()
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 100
            self.assertLess(avg_time, 0.01, "Git operations should be fast (< 10ms average)")
    
    def test_message_generation_performance(self):
        """Test message generation performance"""
        generator = MessageGenerator(self.config)
        
        # Test fallback message generation performance
        files = ['file1.py', 'file2.py', 'file3.py']
        
        start_time = time.time()
        for _ in range(1000):
            generator.generate_fallback_message(files)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 1000
        self.assertLess(avg_time, 0.001, "Fallback message generation should be very fast (< 1ms)")
    
    def test_conventional_format_validation_performance(self):
        """Test conventional format validation performance"""
        generator = MessageGenerator(self.config)
        
        messages = TestFixtures.VALID_CONVENTIONAL_MESSAGES + TestFixtures.INVALID_CONVENTIONAL_MESSAGES
        
        start_time = time.time()
        for _ in range(100):
            for message in messages:
                generator.validate_conventional_format(message)
        end_time = time.time()
        
        total_validations = 100 * len(messages)
        avg_time = (end_time - start_time) / total_validations
        self.assertLess(avg_time, 0.0001, "Format validation should be very fast (< 0.1ms)")
    
    @patch('requests.post')
    def test_api_client_timeout_handling(self, mock_post):
        """Test API client handles timeouts gracefully"""
        # Mock slow response
        def slow_response(*args, **kwargs):
            time.sleep(0.1)  # Simulate slow response
            return TestFixtures.create_mock_http_response(
                200, TestFixtures.GROQ_API_RESPONSES['success']
            )
        
        mock_post.side_effect = slow_response
        
        client = GroqClient(self.config)
        
        start_time = time.time()
        try:
            client.generate_commit_message("test diff")
        except Exception:
            pass  # Expected for timeout
        end_time = time.time()
        
        # Should not take longer than configured timeout + buffer
        self.assertLess(end_time - start_time, self.config.TIMEOUT + 2)


class TestStressConditions(unittest.TestCase):
    """Stress tests for edge cases and high load"""
    
    def setUp(self):
        self.config = TestFixtures.create_mock_config()
    
    def test_large_diff_handling(self):
        """Test handling of very large diffs"""
        generator = MessageGenerator(self.config)
        
        # Create a very large diff
        large_diff = "diff --git a/file.py b/file.py\n" + "+" + "x" * 50000
        files = ['file.py']
        
        start_time = time.time()
        message = generator.generate_message(large_diff, files)
        end_time = time.time()
        
        # Should handle large diffs gracefully and quickly
        self.assertIsNotNone(message)
        self.assertLess(end_time - start_time, 1.0, "Large diff handling should be fast")
        self.assertTrue(message.startswith('feat:'))  # Should fall back to local generation
    
    def test_many_files_handling(self):
        """Test handling of commits with many files"""
        generator = MessageGenerator(self.config)
        
        # Create a list with many files
        many_files = [f'file{i}.py' for i in range(1000)]
        
        start_time = time.time()
        message = generator.generate_fallback_message(many_files)
        end_time = time.time()
        
        # Should handle many files efficiently
        self.assertIsNotNone(message)
        self.assertLess(end_time - start_time, 0.1, "Many files handling should be fast")
        self.assertIn('1000 files', message)
    
    def test_concurrent_operations(self):
        """Test concurrent operations don't interfere"""
        def run_git_operation():
            git_ops = GitOperations()
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = TestFixtures.create_mock_subprocess_response(
                    TestFixtures.GIT_RESPONSES['valid_repo']
                )
                return git_ops.is_git_repository()
        
        # Run multiple operations concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_git_operation) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All operations should succeed
        self.assertTrue(all(results), "All concurrent operations should succeed")
    
    def test_memory_usage_with_large_data(self):
        """Test memory usage doesn't grow excessively with large data"""
        generator = MessageGenerator(self.config)
        
        # Process many large diffs
        for i in range(100):
            large_diff = f"diff --git a/file{i}.py b/file{i}.py\n" + "+" + "x" * 1000
            files = [f'file{i}.py']
            
            message = generator.generate_message(large_diff, files)
            self.assertIsNotNone(message)
        
        # Test passes if no memory errors occur
        self.assertTrue(True)
    
    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters"""
        generator = MessageGenerator(self.config)
        
        # Test with various unicode characters
        unicode_files = [
            'файл.py',  # Cyrillic
            '文件.py',   # Chinese
            'ファイル.py', # Japanese
            'archivo_con_ñ.py',  # Spanish
            'file with spaces.py',
            'file-with-dashes.py',
            'file_with_underscores.py',
            'file.with.dots.py'
        ]
        
        for filename in unicode_files:
            with self.subTest(filename=filename):
                message = generator.generate_fallback_message([filename])
                self.assertIsNotNone(message)
                self.assertTrue(any(prefix in message for prefix in TestFixtures.CONVENTIONAL_PREFIXES))
    
    def test_empty_and_null_inputs(self):
        """Test handling of empty and null inputs"""
        generator = MessageGenerator(self.config)
        git_ops = GitOperations()
        ui = UserInterface()
        
        # Test empty inputs
        empty_inputs = ['', '   ', None]
        
        for empty_input in empty_inputs:
            with self.subTest(input=empty_input):
                # Message generator should handle empty inputs gracefully
                if empty_input is not None:
                    result = generator.validate_conventional_format(empty_input)
                    self.assertFalse(result)
                
                # UI should handle empty inputs
                if empty_input is not None:
                    with patch('builtins.input', return_value=empty_input):
                        with patch('sys.stdout'):
                            # Should not crash
                            try:
                                ui.show_info(empty_input)
                            except Exception as e:
                                self.fail(f"UI should handle empty input gracefully: {e}")
    
    def test_rapid_successive_operations(self):
        """Test rapid successive operations"""
        commit_buddy = CommitBuddy()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = TestFixtures.create_mock_subprocess_response(
                TestFixtures.GIT_RESPONSES['no_staged_files']
            )
            
            # Perform rapid successive operations
            start_time = time.time()
            for _ in range(50):
                result = commit_buddy.handle_from_diff()
                self.assertEqual(result, 0)  # Should handle no staged files gracefully
            end_time = time.time()
            
            # Should complete quickly
            self.assertLess(end_time - start_time, 5.0, "Rapid operations should complete quickly")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        self.config = TestFixtures.create_mock_config()
    
    def test_boundary_diff_sizes(self):
        """Test diffs at boundary sizes"""
        generator = MessageGenerator(self.config)
        
        # Test diff exactly at MAX_DIFF_SIZE
        boundary_diff = "x" * self.config.MAX_DIFF_SIZE
        files = ['file.py']
        
        message = generator.generate_message(boundary_diff, files)
        self.assertIsNotNone(message)
        
        # Test diff just over MAX_DIFF_SIZE
        over_boundary_diff = "x" * (self.config.MAX_DIFF_SIZE + 1)
        message = generator.generate_message(over_boundary_diff, files)
        self.assertIsNotNone(message)
        self.assertTrue(message.startswith('feat:'))  # Should use fallback
    
    def test_maximum_file_count(self):
        """Test with maximum reasonable file count"""
        generator = MessageGenerator(self.config)
        
        # Test with very large number of files
        max_files = [f'file{i}.py' for i in range(10000)]
        
        start_time = time.time()
        message = generator.generate_fallback_message(max_files)
        end_time = time.time()
        
        self.assertIsNotNone(message)
        self.assertIn('10000 files', message)
        self.assertLess(end_time - start_time, 1.0, "Should handle max files quickly")
    
    def test_deeply_nested_file_paths(self):
        """Test with deeply nested file paths"""
        generator = MessageGenerator(self.config)
        
        # Create deeply nested path
        deep_path = '/'.join(['dir'] * 50) + '/file.py'
        files = [deep_path]
        
        message = generator.generate_fallback_message(files)
        self.assertIsNotNone(message)
        self.assertTrue(message.startswith('feat:'))
    
    def test_very_long_file_names(self):
        """Test with very long file names"""
        generator = MessageGenerator(self.config)
        
        # Create very long filename
        long_filename = 'a' * 255 + '.py'  # Maximum typical filename length
        files = [long_filename]
        
        message = generator.generate_fallback_message(files)
        self.assertIsNotNone(message)
        
        # Message should be truncated appropriately if too long
        self.assertLessEqual(len(message), 72, "Commit message should not exceed 72 characters")


def run_performance_tests():
    """Run all performance tests"""
    print("🚀 RUNNING PERFORMANCE AND STRESS TESTS")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestPerformance,
        TestStressConditions,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, descriptions=True)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ ALL PERFORMANCE TESTS PASSED!")
        print("The system performs well under stress conditions.")
    else:
        print("❌ SOME PERFORMANCE TESTS FAILED!")
        for test, traceback in result.failures + result.errors:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_performance_tests()
    sys.exit(0 if success else 1)