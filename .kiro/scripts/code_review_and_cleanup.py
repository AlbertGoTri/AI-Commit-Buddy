#!/usr/bin/env python3
"""
Code Review and Cleanup Script
Performs final code review and cleanup for Kiro Commit Buddy
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple

class CodeReviewAndCleanup:
    """Performs comprehensive code review and cleanup"""
    
    def __init__(self):
        self.issues = []
        self.suggestions = []
        self.script_dir = Path(__file__).parent
        
    def log_issue(self, file_path: str, issue_type: str, message: str, line_num: int = None):
        """Log a code issue"""
        location = f"{file_path}:{line_num}" if line_num else file_path
        self.issues.append({
            'location': location,
            'type': issue_type,
            'message': message
        })
    
    def log_suggestion(self, file_path: str, message: str):
        """Log a code suggestion"""
        self.suggestions.append({
            'file': file_path,
            'message': message
        })
    
    def check_python_syntax(self, file_path: Path) -> bool:
        """Check Python syntax validity"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True
        except SyntaxError as e:
            self.log_issue(str(file_path), "SYNTAX_ERROR", f"Syntax error: {e}", e.lineno)
            return False
        except Exception as e:
            self.log_issue(str(file_path), "PARSE_ERROR", f"Parse error: {e}")
            return False
    
    def check_imports(self, file_path: Path):
        """Check import statements for best practices"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            import_section_ended = False
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check for imports after code
                if line.startswith(('import ', 'from ')) and import_section_ended:
                    self.log_issue(str(file_path), "IMPORT_ORDER", 
                                 "Import statement after code", i)
                
                # Mark end of import section
                if line and not line.startswith(('import ', 'from ', '#', '"""', "'''")) and not import_section_ended:
                    import_section_ended = True
                
                # Check for unused imports (basic check)
                if line.startswith('import ') or line.startswith('from '):
                    # This is a simplified check - in production, use tools like flake8
                    pass
                    
        except Exception as e:
            self.log_issue(str(file_path), "IMPORT_CHECK_ERROR", f"Error checking imports: {e}")
    
    def check_docstrings(self, file_path: Path):
        """Check for proper docstrings"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        self.log_issue(str(file_path), "MISSING_DOCSTRING", 
                                     f"Missing docstring for {node.name}", node.lineno)
                        
        except Exception as e:
            self.log_issue(str(file_path), "DOCSTRING_CHECK_ERROR", f"Error checking docstrings: {e}")
    
    def check_error_handling(self, file_path: Path):
        """Check error handling patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for bare except clauses
            if re.search(r'except\s*:', content):
                self.log_issue(str(file_path), "BARE_EXCEPT", 
                             "Bare except clause found - should specify exception type")
            
            # Check for proper exception handling
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        self.log_issue(str(file_path), "BARE_EXCEPT", 
                                     "Bare except clause", node.lineno)
                        
        except Exception as e:
            self.log_issue(str(file_path), "ERROR_HANDLING_CHECK_ERROR", f"Error checking error handling: {e}")
    
    def check_code_complexity(self, file_path: Path):
        """Check for code complexity issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check line length
            for i, line in enumerate(lines, 1):
                if len(line) > 100:
                    self.log_issue(str(file_path), "LONG_LINE", 
                                 f"Line too long ({len(line)} chars)", i)
            
            # Check function complexity (simplified)
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Count nested levels
                    max_depth = self._calculate_nesting_depth(node)
                    if max_depth > 4:
                        self.log_issue(str(file_path), "HIGH_COMPLEXITY", 
                                     f"Function {node.name} has high nesting depth ({max_depth})", 
                                     node.lineno)
                        
        except Exception as e:
            self.log_issue(str(file_path), "COMPLEXITY_CHECK_ERROR", f"Error checking complexity: {e}")
    
    def _calculate_nesting_depth(self, node, depth=0):
        """Calculate maximum nesting depth of a node"""
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def check_security_issues(self, file_path: Path):
        """Check for potential security issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for hardcoded secrets (basic patterns)
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
            ]
            
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.log_issue(str(file_path), "POTENTIAL_SECRET", 
                                 "Potential hardcoded secret found")
            
            # Check for subprocess usage without shell=False
            if 'subprocess' in content and 'shell=True' in content:
                self.log_issue(str(file_path), "SHELL_INJECTION_RISK", 
                             "subprocess with shell=True may be vulnerable to injection")
                             
        except Exception as e:
            self.log_issue(str(file_path), "SECURITY_CHECK_ERROR", f"Error checking security: {e}")
    
    def review_file(self, file_path: Path):
        """Perform comprehensive review of a single file"""
        print(f"Reviewing {file_path.name}...")
        
        # Basic syntax check
        if not self.check_python_syntax(file_path):
            return  # Skip other checks if syntax is invalid
        
        # Import checks
        self.check_imports(file_path)
        
        # Docstring checks
        self.check_docstrings(file_path)
        
        # Error handling checks
        self.check_error_handling(file_path)
        
        # Complexity checks
        self.check_code_complexity(file_path)
        
        # Security checks
        self.check_security_issues(file_path)
    
    def cleanup_file(self, file_path: Path):
        """Perform automated cleanup on a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove trailing whitespace
            lines = content.split('\n')
            cleaned_lines = [line.rstrip() for line in lines]
            content = '\n'.join(cleaned_lines)
            
            # Ensure file ends with newline
            if content and not content.endswith('\n'):
                content += '\n'
            
            # Remove multiple consecutive blank lines
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_suggestion(str(file_path), "Cleaned up whitespace and formatting")
                
        except Exception as e:
            self.log_issue(str(file_path), "CLEANUP_ERROR", f"Error during cleanup: {e}")
    
    def review_all_files(self):
        """Review all Python files in the project"""
        print("🔍 Starting Code Review and Cleanup")
        print("=" * 50)
        
        # Get all Python files
        python_files = [
            self.script_dir / 'commit_buddy.py',
            self.script_dir / 'config.py',
            self.script_dir / 'git_operations.py',
            self.script_dir / 'groq_client.py',
            self.script_dir / 'message_generator.py',
            self.script_dir / 'user_interface.py',
        ]
        
        # Filter existing files
        existing_files = [f for f in python_files if f.exists()]
        
        # Review each file
        for file_path in existing_files:
            self.review_file(file_path)
            self.cleanup_file(file_path)
        
        # Generate report
        self.generate_review_report()
    
    def generate_review_report(self):
        """Generate code review report"""
        print("\n" + "=" * 50)
        print("📋 CODE REVIEW REPORT")
        print("=" * 50)
        
        # Summary
        total_issues = len(self.issues)
        total_suggestions = len(self.suggestions)
        
        print(f"Issues Found: {total_issues}")
        print(f"Improvements Made: {total_suggestions}")
        
        # Issues by type
        if self.issues:
            issue_types = {}
            for issue in self.issues:
                issue_type = issue['type']
                if issue_type not in issue_types:
                    issue_types[issue_type] = 0
                issue_types[issue_type] += 1
            
            print("\n📊 Issues by Type:")
            for issue_type, count in sorted(issue_types.items()):
                print(f"  {issue_type}: {count}")
            
            print("\n❌ Detailed Issues:")
            for issue in self.issues:
                print(f"  • {issue['location']}: {issue['message']} [{issue['type']}]")
        
        # Suggestions
        if self.suggestions:
            print("\n✅ Improvements Made:")
            for suggestion in self.suggestions:
                print(f"  • {suggestion['file']}: {suggestion['message']}")
        
        # Code quality assessment
        print("\n📈 Code Quality Assessment:")
        if total_issues == 0:
            print("  🎉 Excellent! No issues found.")
        elif total_issues <= 5:
            print("  ✅ Good! Minor issues found.")
        elif total_issues <= 15:
            print("  ⚠️  Fair. Some issues need attention.")
        else:
            print("  ❌ Poor. Many issues need to be addressed.")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if total_issues == 0:
            print("  • Code is ready for production")
            print("  • Consider adding more comprehensive tests")
            print("  • Monitor performance in production")
        else:
            print("  • Address critical issues first")
            print("  • Consider using automated linting tools (flake8, pylint)")
            print("  • Add more comprehensive error handling")
            print("  • Improve documentation where needed")


if __name__ == "__main__":
    reviewer = CodeReviewAndCleanup()
    reviewer.review_all_files()