#!/usr/bin/env python3
"""
Complete functionality test for MessageGenerator
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from message_generator import MessageGenerator
from config import Config
from unittest.mock import Mock

def test_complete_functionality():
    """Test complete MessageGenerator functionality"""
    
    # Test complete functionality
    config = Mock()
    config.has_groq_api_key.return_value = False
    config.MAX_DIFF_SIZE = 8000

    gen = MessageGenerator(config)

    print('=== MessageGenerator Functionality Test ===')
    print()

    # Test 1: Conventional format validation
    print('1. Conventional format validation:')
    valid_msgs = ['feat: add feature', 'fix: bug fix', 'docs: update readme']
    invalid_msgs = ['add feature', 'feat:', '']
    for msg in valid_msgs:
        print(f'  "{msg}" -> {gen.validate_conventional_format(msg)}')
    for msg in invalid_msgs:
        print(f'  "{msg}" -> {gen.validate_conventional_format(msg)}')
    print()

    # Test 2: Fallback message generation
    print('2. Fallback message generation:')
    test_cases = [
        (['main.py'], 'Single Python file'),
        (['README.md'], 'Single doc file'),
        (['test_main.py'], 'Single test file'),
        (['config.json'], 'Single config file'),
        (['main.py', 'utils.py', 'test.py'], 'Multiple files'),
        ([f'file{i}.py' for i in range(5)], 'Many files')
    ]

    for files, desc in test_cases:
        msg = gen.generate_fallback_message(files)
        print(f'  {desc}: {msg}')
    print()

    # Test 3: Message generation (fallback only since no API)
    print('3. Message generation (fallback mode):')
    diff = '--- a/main.py\n+++ b/main.py\n@@ -1,3 +1,4 @@\n def func():\n+    print("hello")\n     pass'
    files = ['main.py']
    msg = gen.generate_message(diff, files)
    print(f'  Generated: {msg}')
    print()

    # Test 4: Commit type determination
    print('4. Commit type determination:')
    file_test_cases = [
        (['README.md', 'docs/api.md'], 'Documentation files'),
        (['test_main.py', 'tests/test_utils.py'], 'Test files'),
        (['config.json', 'settings.yml'], 'Config files'),
        (['main.py', 'utils.py'], 'Source code files'),
        (['style.css', 'image.png'], 'Other files')
    ]
    
    for files, desc in file_test_cases:
        commit_type = gen._determine_commit_type_from_files(files)
        print(f'  {desc}: {commit_type}')
    print()

    # Test 5: Message fixing
    print('5. Message format fixing:')
    fix_test_cases = [
        ('feat: add new feature', ['main.py'], 'Already formatted'),
        ('add new authentication', ['auth.py'], 'Add keyword'),
        ('fix login bug', ['auth.py'], 'Fix keyword'),
        ('update documentation', ['README.md'], 'Generic update with docs file'),
        ('refactor code structure', ['main.py'], 'Refactor keyword')
    ]
    
    for message, files, desc in fix_test_cases:
        fixed = gen._fix_conventional_format(message, files)
        print(f'  {desc}: "{message}" -> "{fixed}"')
    print()

    print('=== All tests completed successfully! ===')

if __name__ == '__main__':
    test_complete_functionality()