#!/usr/bin/env python3
"""
Test fixtures and test data for Kiro Commit Buddy tests
Provides consistent test data across all test modules
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock


class TestFixtures:
    """Test fixtures and data for consistent testing"""
    
    # Sample Git diffs for testing
    SAMPLE_DIFFS = {
        'python_feature': """diff --git a/src/auth.py b/src/auth.py
index 1234567..abcdefg 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -1,5 +1,8 @@
 def authenticate_user(username, password):
+    if not username or not password:
+        raise ValueError("Username and password required")
+    
     # Authenticate user logic
     return True
 
 def logout_user(user_id):
     # Logout logic
     pass""",
        
        'bug_fix': """diff --git a/src/utils.py b/src/utils.py
index 2345678..bcdefgh 100644
--- a/src/utils.py
+++ b/src/utils.py
@@ -10,7 +10,7 @@ def calculate_total(items):
     total = 0
     for item in items:
-        total += item.price
+        total += item.price if item.price else 0
     return total""",
        
        'documentation': """diff --git a/README.md b/README.md
index 3456789..cdefghi 100644
--- a/README.md
+++ b/README.md
@@ -1,4 +1,8 @@
 # Project Title
 
+## Installation
+
+Run `pip install -r requirements.txt` to install dependencies.
+
 ## Usage
 
 This is how you use the project.""",
        
        'test_file': """diff --git a/tests/test_auth.py b/tests/test_auth.py
index 4567890..defghij 100644
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -5,6 +5,12 @@ from src.auth import authenticate_user
 class TestAuth(unittest.TestCase):
     
+    def test_authenticate_user_empty_credentials(self):
+        with self.assertRaises(ValueError):
+            authenticate_user("", "")
+    
     def test_authenticate_user_valid(self):
         result = authenticate_user("user", "pass")
         self.assertTrue(result)""",
        
        'config_change': """diff --git a/config.json b/config.json
index 5678901..efghijk 100644
--- a/config.json
+++ b/config.json
@@ -1,5 +1,6 @@
 {
   "database_url": "localhost:5432",
-  "debug": false
+  "debug": false,
+  "timeout": 30
 }""",
        
        'refactor': """diff --git a/src/service.py b/src/service.py
index 6789012..fghijkl 100644
--- a/src/service.py
+++ b/src/service.py
@@ -1,10 +1,15 @@
-def process_data(data):
-    # Old implementation
-    result = []
-    for item in data:
-        result.append(item.upper())
-    return result
+class DataProcessor:
+    def __init__(self):
+        self.processed_count = 0
+    
+    def process_data(self, data):
+        # New implementation with class structure
+        result = []
+        for item in data:
+            result.append(item.upper())
+            self.processed_count += 1
+        return result""",
        
        'large_diff': "x" * 10000,  # Exceeds MAX_DIFF_SIZE
        
        'small_diff': "line1\nline2",  # Too small for AI
    }
    
    # Sample file lists for testing
    SAMPLE_FILE_LISTS = {
        'single_python': ['main.py'],
        'multiple_python': ['main.py', 'utils.py', 'config.py'],
        'mixed_files': ['main.py', 'README.md', 'test_main.py'],
        'docs_only': ['README.md', 'docs/api.md', 'CHANGELOG.md'],
        'tests_only': ['test_main.py', 'tests/test_utils.py', 'spec/auth_spec.py'],
        'config_only': ['config.json', 'settings.yml', '.env'],
        'many_files': [f'file{i}.py' for i in range(10)],
        'empty_list': [],
    }
    
    # Expected commit messages for different scenarios
    EXPECTED_MESSAGES = {
        'python_feature': 'feat: add user authentication validation',
        'bug_fix': 'fix: handle null price in calculate_total',
        'documentation': 'docs: add installation instructions',
        'test_file': 'test: add empty credentials validation test',
        'config_change': 'chore: add timeout configuration',
        'refactor': 'refactor: convert data processing to class structure',
    }
    
    # Conventional commit prefixes
    CONVENTIONAL_PREFIXES = ['feat', 'fix', 'docs', 'refactor', 'test', 'chore']
    
    # Valid conventional commit messages
    VALID_CONVENTIONAL_MESSAGES = [
        'feat: add new user authentication',
        'fix: resolve login bug',
        'docs: update README with installation steps',
        'refactor: restructure user service',
        'test: add unit tests for auth module',
        'chore: update dependencies',
        'feat(auth): add OAuth integration',
        'fix(ui): correct button alignment',
        'FEAT: add new feature',  # Case insensitive
    ]
    
    # Invalid conventional commit messages
    INVALID_CONVENTIONAL_MESSAGES = [
        '',
        '   ',
        'add new feature',  # No prefix
        'feature: add new feature',  # Wrong prefix
        'feat:',  # No description
        'feat: ',  # Empty description
        'feat add new feature',  # Missing colon
        None,
    ]
    
    # API response samples
    GROQ_API_RESPONSES = {
        'success': {
            'choices': [
                {
                    'message': {
                        'content': 'feat: add user authentication system'
                    }
                }
            ]
        },
        'multiline': {
            'choices': [
                {
                    'message': {
                        'content': 'feat: add feature\n\nThis is a detailed description'
                    }
                }
            ]
        },
        'quoted': {
            'choices': [
                {
                    'message': {
                        'content': '"feat: add quoted feature"'
                    }
                }
            ]
        },
        'long_message': {
            'choices': [
                {
                    'message': {
                        'content': 'feat: ' + 'x' * 100  # Very long message
                    }
                }
            ]
        },
        'empty_choices': {
            'choices': []
        },
        'empty_content': {
            'choices': [
                {
                    'message': {
                        'content': ''
                    }
                }
            ]
        },
        'invalid_structure': {
            'invalid': 'response'
        }
    }
    
    # Git command responses
    GIT_RESPONSES = {
        'valid_repo': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
        'invalid_repo': {
            'returncode': 128,
            'stdout': '',
            'stderr': 'fatal: not a git repository'
        },
        'staged_files': {
            'returncode': 0,
            'stdout': 'file1.py\nfile2.js\nREADME.md\n',
            'stderr': ''
        },
        'no_staged_files': {
            'returncode': 0,
            'stdout': '',
            'stderr': ''
        },
        'commit_success': {
            'returncode': 0,
            'stdout': '[main abc1234] feat: add new feature\n 1 file changed, 1 insertion(+)\n',
            'stderr': ''
        },
        'commit_failure': {
            'returncode': 1,
            'stdout': '',
            'stderr': 'error: pathspec did not match any files'
        }
    }
    
    @staticmethod
    def create_mock_config(has_api_key=True, api_key="gsk_test-api-key-1234567890abcdef"):
        """Create a mock configuration object"""
        config = Mock()
        config.GROQ_MODEL = "llama3-70b-8192"
        config.GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
        config.MAX_DIFF_SIZE = 8000
        config.TIMEOUT = 10
        config.MAX_TOKENS = 150
        config.TEMPERATURE = 0.3
        config.has_groq_api_key.return_value = has_api_key
        config.get_groq_api_key.return_value = api_key if has_api_key else None
        config.validate_api_key_format.return_value = (True, "") if has_api_key else (False, "No API key")
        config.get_api_headers.return_value = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if has_api_key else {}
        config.get_commit_prompt_template.return_value = "Test prompt: {diff}"
        return config
    
    @staticmethod
    def create_mock_subprocess_response(response_data):
        """Create a mock subprocess response"""
        mock_response = Mock()
        mock_response.returncode = response_data.get('returncode', 0)
        mock_response.stdout = response_data.get('stdout', '')
        mock_response.stderr = response_data.get('stderr', '')
        return mock_response
    
    @staticmethod
    def create_mock_http_response(status_code=200, json_data=None):
        """Create a mock HTTP response"""
        mock_response = Mock()
        mock_response.status_code = status_code
        if json_data:
            mock_response.json.return_value = json_data
        else:
            mock_response.json.side_effect = Exception("No JSON data")
        return mock_response
    
    @staticmethod
    def create_temp_git_repo():
        """Create a temporary Git repository for testing"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Initialize git repo
        os.system(f'cd {repo_path} && git init')
        os.system(f'cd {repo_path} && git config user.email "test@example.com"')
        os.system(f'cd {repo_path} && git config user.name "Test User"')
        
        return repo_path
    
    @staticmethod
    def cleanup_temp_repo(repo_path):
        """Clean up temporary Git repository"""
        import shutil
        shutil.rmtree(repo_path, ignore_errors=True)


class TestScenarios:
    """Common test scenarios for end-to-end testing"""
    
    @staticmethod
    def successful_workflow_scenario():
        """Complete successful workflow scenario"""
        return {
            'git_responses': [
                TestFixtures.GIT_RESPONSES['valid_repo'],  # is_git_repository
                TestFixtures.create_mock_subprocess_response({
                    'returncode': 0,
                    'stdout': TestFixtures.SAMPLE_DIFFS['python_feature'],
                    'stderr': ''
                }),  # get_staged_diff
                TestFixtures.GIT_RESPONSES['staged_files'],  # get_changed_files
                TestFixtures.GIT_RESPONSES['commit_success']  # commit_with_message
            ],
            'api_response': TestFixtures.GROQ_API_RESPONSES['success'],
            'user_inputs': ['y'],  # Confirm message
            'expected_message': 'feat: add user authentication system',
            'expected_exit_code': 0
        }
    
    @staticmethod
    def fallback_workflow_scenario():
        """Workflow with API failure and fallback scenario"""
        return {
            'git_responses': [
                TestFixtures.GIT_RESPONSES['valid_repo'],  # is_git_repository
                TestFixtures.create_mock_subprocess_response({
                    'returncode': 0,
                    'stdout': TestFixtures.SAMPLE_DIFFS['config_change'],
                    'stderr': ''
                }),  # get_staged_diff
                TestFixtures.create_mock_subprocess_response({
                    'returncode': 0,
                    'stdout': 'config.json\n',
                    'stderr': ''
                }),  # get_changed_files
                TestFixtures.GIT_RESPONSES['commit_success']  # commit_with_message
            ],
            'api_error': Exception("API Error"),
            'user_inputs': ['y'],  # Confirm fallback message
            'expected_message': 'chore: update config.json',
            'expected_exit_code': 0
        }
    
    @staticmethod
    def no_staged_changes_scenario():
        """Scenario with no staged changes"""
        return {
            'git_responses': [
                TestFixtures.GIT_RESPONSES['valid_repo'],  # is_git_repository
                TestFixtures.GIT_RESPONSES['no_staged_files']  # get_staged_diff
            ],
            'user_inputs': [],
            'expected_exit_code': 0
        }
    
    @staticmethod
    def invalid_git_repo_scenario():
        """Scenario with invalid Git repository"""
        return {
            'git_responses': [
                TestFixtures.GIT_RESPONSES['invalid_repo']  # is_git_repository
            ],
            'user_inputs': [],
            'expected_exit_code': 1
        }


if __name__ == '__main__':
    # Test the fixtures
    print("Testing fixtures...")
    
    # Test mock config
    config = TestFixtures.create_mock_config()
    assert config.has_groq_api_key() == True
    assert config.get_groq_api_key() == "test-api-key"
    print("✓ Mock config works")
    
    # Test mock responses
    response = TestFixtures.create_mock_subprocess_response(TestFixtures.GIT_RESPONSES['valid_repo'])
    assert response.returncode == 0
    print("✓ Mock subprocess response works")
    
    # Test scenarios
    scenario = TestScenarios.successful_workflow_scenario()
    assert len(scenario['git_responses']) == 4
    assert scenario['expected_exit_code'] == 0
    print("✓ Test scenarios work")
    
    print("All fixtures are working correctly!")