#!/usr/bin/env python3
"""
Hook Format Tester for Kiro Commit Buddy
Tests different hook configuration formats to find the correct one
"""

import os
import sys
import yaml
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List

class HookFormatTester:
    """Test different hook configuration formats"""
    
    def __init__(self):
        self.hook_file = Path(".kiro/hooks/commit.yml")
        self.backup_file = Path(".kiro/hooks/commit.yml.backup")
        self.original_config = None
        
    def backup_current_config(self):
        """Backup the current hook configuration"""
        if self.hook_file.exists():
            with open(self.hook_file, 'r', encoding='utf-8') as f:
                self.original_config = f.read()
            shutil.copy2(self.hook_file, self.backup_file)
            print(f"✅ Backed up current config to {self.backup_file}")
    
    def restore_config(self):
        """Restore the original configuration"""
        if self.original_config:
            with open(self.hook_file, 'w', encoding='utf-8') as f:
                f.write(self.original_config)
            print("✅ Restored original configuration")
    
    def test_hook_format(self, config: Dict[str, Any], format_name: str) -> bool:
        """Test a specific hook configuration format"""
        print(f"\n🧪 Testing format: {format_name}")
        print("-" * 40)
        
        try:
            # Write the test configuration
            with open(self.hook_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            print(f"📝 Configuration written:")
            for key, value in config.items():
                print(f"   {key}: {value}")
            
            # Test if the configuration is valid YAML
            with open(self.hook_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            print("✅ Valid YAML format")
            
            # Test if Kiro recognizes the command (if kiro is available)
            try:
                # First check if kiro is available
                result = subprocess.run(['kiro', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✅ Kiro is available")
                    
                    # Test the actual command
                    result = subprocess.run(['kiro', 'commit', '--from-diff'], 
                                          capture_output=True, text=True, timeout=10)
                    
                    output = result.stdout + result.stderr
                    
                    # Check for the warning
                    if "Warning: 'from-diff' is not in the list of known options" in output:
                        print("❌ Still shows warning for unknown option")
                        return False
                    elif "No hay cambios staged" in output or "No estás en un repositorio Git" in output:
                        print("✅ Command executed without warnings")
                        return True
                    else:
                        print(f"⚠️  Unexpected output: {output}")
                        return False
                else:
                    print("⚠️  Kiro not available for testing")
                    return None
                    
            except subprocess.TimeoutExpired:
                print("⚠️  Kiro command timed out")
                return None
            except FileNotFoundError:
                print("⚠️  Kiro not found in PATH")
                return None
            except Exception as e:
                print(f"⚠️  Error testing Kiro command: {e}")
                return None
                
        except Exception as e:
            print(f"❌ Error testing format: {e}")
            return False
    
    def get_test_formats(self) -> Dict[str, Dict[str, Any]]:
        """Get different hook configuration formats to test"""
        
        formats = {
            "original": {
                "name": "Commit Buddy",
                "description": "Generate AI-powered commit messages",
                "command": "python .kiro/scripts/commit_buddy.py",
                "args": ["--from-diff"],
                "triggers": ["manual"]
            },
            
            "single_command_string": {
                "name": "Commit Buddy", 
                "description": "Generate AI-powered commit messages",
                "command": "python .kiro/scripts/commit_buddy.py --from-diff",
                "triggers": ["manual"]
            },
            
            "name_as_commit": {
                "name": "commit",
                "description": "Generate AI-powered commit messages",
                "command": "python .kiro/scripts/commit_buddy.py",
                "args": ["--from-diff"],
                "triggers": ["manual"]
            },
            
            "executable_script": {
                "name": "Commit Buddy",
                "description": "Generate AI-powered commit messages", 
                "command": ".kiro/scripts/commit_buddy.py",
                "args": ["--from-diff"],
                "triggers": ["manual"]
            },
            
            "with_working_directory": {
                "name": "Commit Buddy",
                "description": "Generate AI-powered commit messages",
                "command": "python commit_buddy.py",
                "args": ["--from-diff"],
                "workingDirectory": ".kiro/scripts",
                "triggers": ["manual"]
            },
            
            "different_trigger": {
                "name": "Commit Buddy",
                "description": "Generate AI-powered commit messages",
                "command": "python .kiro/scripts/commit_buddy.py",
                "args": ["--from-diff"],
                "triggers": ["command"]
            },
            
            "with_env": {
                "name": "Commit Buddy",
                "description": "Generate AI-powered commit messages",
                "command": "python .kiro/scripts/commit_buddy.py",
                "args": ["--from-diff"],
                "triggers": ["manual"],
                "env": {
                    "PYTHONPATH": ".kiro/scripts"
                }
            },
            
            "absolute_python": {
                "name": "Commit Buddy",
                "description": "Generate AI-powered commit messages",
                "command": f"{sys.executable} .kiro/scripts/commit_buddy.py",
                "args": ["--from-diff"],
                "triggers": ["manual"]
            }
        }
        
        return formats
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run tests for all hook formats"""
        print("🚀 Starting Hook Format Tests")
        print("=" * 60)
        
        # Backup current configuration
        self.backup_current_config()
        
        formats = self.get_test_formats()
        results = {}
        
        try:
            for format_name, config in formats.items():
                result = self.test_hook_format(config, format_name)
                results[format_name] = result
                
                if result is True:
                    print(f"🎉 SUCCESS: {format_name} works!")
                elif result is False:
                    print(f"❌ FAILED: {format_name} doesn't work")
                else:
                    print(f"⚠️  UNKNOWN: {format_name} couldn't be tested")
        
        finally:
            # Always restore the original configuration
            self.restore_config()
        
        return results
    
    def generate_report(self, results: Dict[str, bool]) -> str:
        """Generate a summary report of the test results"""
        report = []
        report.append("=" * 60)
        report.append("HOOK FORMAT TEST REPORT")
        report.append("=" * 60)
        
        successful_formats = []
        failed_formats = []
        unknown_formats = []
        
        for format_name, result in results.items():
            if result is True:
                successful_formats.append(format_name)
            elif result is False:
                failed_formats.append(format_name)
            else:
                unknown_formats.append(format_name)
        
        if successful_formats:
            report.append("\n✅ SUCCESSFUL FORMATS:")
            for fmt in successful_formats:
                report.append(f"   - {fmt}")
        
        if failed_formats:
            report.append("\n❌ FAILED FORMATS:")
            for fmt in failed_formats:
                report.append(f"   - {fmt}")
        
        if unknown_formats:
            report.append("\n⚠️  UNTESTABLE FORMATS (Kiro not available):")
            for fmt in unknown_formats:
                report.append(f"   - {fmt}")
        
        report.append(f"\nSUMMARY: {len(successful_formats)} successful, {len(failed_formats)} failed, {len(unknown_formats)} untestable")
        
        if successful_formats:
            report.append(f"\n🎯 RECOMMENDATION: Use the '{successful_formats[0]}' format")
        elif not unknown_formats:
            report.append("\n💡 SUGGESTION: The issue may not be with the hook format")
            report.append("   Consider checking:")
            report.append("   - Kiro installation")
            report.append("   - Hook registration mechanism")
            report.append("   - Command parsing in Kiro")
        
        return "\n".join(report)

def main():
    """Run the hook format tester"""
    tester = HookFormatTester()
    
    print("🔍 Kiro Hook Format Tester")
    print("This tool will test different hook configuration formats")
    print("to find the correct one for Kiro Commit Buddy\n")
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Generate and display report
    report = tester.generate_report(results)
    print("\n" + report)
    
    # Return appropriate exit code
    successful_count = sum(1 for result in results.values() if result is True)
    return 0 if successful_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())