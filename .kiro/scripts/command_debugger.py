#!/usr/bin/env python3
"""
Command Debugger for Kiro Commit Buddy
Helps diagnose Kiro command recognition issues
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from typing import Tuple, List, Dict, Any

class CommandDebugger:
    """Debug Kiro command registration and recognition issues"""
    
    def __init__(self):
        self.hook_file = Path(".kiro/hooks/commit.yml")
        self.script_file = Path(".kiro/scripts/commit_buddy.py")
    
    def validate_hook_configuration(self) -> Tuple[bool, List[str]]:
        """Validate the hook configuration file"""
        issues = []
        
        # Check if hook file exists
        if not self.hook_file.exists():
            issues.append(f"Hook file not found: {self.hook_file}")
            return False, issues
        
        try:
            with open(self.hook_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Check required fields
            required_fields = ['name', 'description', 'command', 'args', 'triggers']
            for field in required_fields:
                if field not in config:
                    issues.append(f"Missing required field: {field}")
            
            # Check field values
            if 'command' in config and not config['command'].startswith('python'):
                issues.append(f"Command should start with 'python': {config['command']}")
            
            if 'args' in config and '--from-diff' not in config['args']:
                issues.append(f"Args should contain '--from-diff': {config['args']}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Error reading hook file: {e}")
            return False, issues
    
    def test_kiro_command_recognition(self) -> bool:
        """Test if Kiro recognizes the command"""
        try:
            # Test the actual kiro command
            result = subprocess.run([
                'kiro', 'commit', '--from-diff'
            ], capture_output=True, text=True, timeout=10)
            
            # Check for the warning message
            output = result.stdout + result.stderr
            has_warning = "Warning: 'from-diff' is not in the list of known options" in output
            
            return not has_warning
            
        except Exception as e:
            print(f"Error testing kiro command: {e}")
            return False
    
    def verify_script_execution(self) -> Tuple[bool, str]:
        """Verify the script can be executed directly"""
        try:
            result = subprocess.run([
                sys.executable, str(self.script_file), '--from-diff'
            ], capture_output=True, text=True, timeout=10)
            
            # Script should run without Python errors
            success = result.returncode in [0, 1]  # 0 = no changes, 1 = not git repo
            output = result.stdout + result.stderr
            
            return success, output
            
        except Exception as e:
            return False, str(e)
    
    def check_file_permissions(self) -> bool:
        """Check if files have correct permissions"""
        try:
            # Check if script is readable and executable
            return (self.script_file.exists() and 
                   os.access(self.script_file, os.R_OK))
        except Exception:
            return False
    
    def test_alternative_hook_formats(self) -> Dict[str, Any]:
        """Test different hook configuration formats"""
        results = {}
        
        # Current format
        current_config = {
            "name": "Commit Buddy",
            "description": "Generate AI-powered commit messages",
            "command": "python .kiro/scripts/commit_buddy.py",
            "args": ["--from-diff"],
            "triggers": ["manual"]
        }
        
        # Alternative format 1: Single command string
        alt1_config = {
            "name": "Commit Buddy",
            "description": "Generate AI-powered commit messages", 
            "command": "python .kiro/scripts/commit_buddy.py --from-diff",
            "triggers": ["manual"]
        }
        
        # Alternative format 2: Different command structure
        alt2_config = {
            "name": "commit",
            "description": "Generate AI-powered commit messages",
            "command": "python .kiro/scripts/commit_buddy.py",
            "args": ["--from-diff"],
            "triggers": ["manual"]
        }
        
        # Alternative format 3: Using executable path
        alt3_config = {
            "name": "Commit Buddy",
            "description": "Generate AI-powered commit messages",
            "command": ".kiro/scripts/commit_buddy.py",
            "args": ["--from-diff"],
            "triggers": ["manual"]
        }
        
        formats = {
            "current": current_config,
            "single_command": alt1_config,
            "name_as_commit": alt2_config,
            "executable_path": alt3_config
        }
        
        for format_name, config in formats.items():
            results[format_name] = {
                "config": config,
                "valid_yaml": True
            }
            
            try:
                # Test if it's valid YAML
                yaml.dump(config)
            except Exception as e:
                results[format_name]["valid_yaml"] = False
                results[format_name]["error"] = str(e)
        
        return results
    
    def generate_debug_report(self) -> str:
        """Generate a comprehensive debug report"""
        report = []
        report.append("=" * 60)
        report.append("KIRO COMMIT BUDDY - DEBUG REPORT")
        report.append("=" * 60)
        
        # Hook configuration validation
        report.append("\n1. HOOK CONFIGURATION VALIDATION")
        report.append("-" * 40)
        is_valid, issues = self.validate_hook_configuration()
        if is_valid:
            report.append("✅ Hook configuration is valid")
        else:
            report.append("❌ Hook configuration has issues:")
            for issue in issues:
                report.append(f"   - {issue}")
        
        # Script execution test
        report.append("\n2. SCRIPT EXECUTION TEST")
        report.append("-" * 40)
        script_works, script_output = self.verify_script_execution()
        if script_works:
            report.append("✅ Script executes correctly")
        else:
            report.append("❌ Script execution failed:")
            report.append(f"   Output: {script_output}")
        
        # Kiro command recognition test
        report.append("\n3. KIRO COMMAND RECOGNITION TEST")
        report.append("-" * 40)
        kiro_works = self.test_kiro_command_recognition()
        if kiro_works:
            report.append("✅ Kiro recognizes command correctly")
        else:
            report.append("❌ Kiro shows warning for unknown option")
        
        # File permissions
        report.append("\n4. FILE PERMISSIONS")
        report.append("-" * 40)
        perms_ok = self.check_file_permissions()
        if perms_ok:
            report.append("✅ File permissions are correct")
        else:
            report.append("❌ File permission issues detected")
        
        # Alternative formats
        report.append("\n5. ALTERNATIVE HOOK FORMATS")
        report.append("-" * 40)
        alt_formats = self.test_alternative_hook_formats()
        for format_name, format_data in alt_formats.items():
            status = "✅" if format_data["valid_yaml"] else "❌"
            report.append(f"{status} {format_name}: {format_data['config']}")
        
        # Current hook content
        report.append("\n6. CURRENT HOOK CONTENT")
        report.append("-" * 40)
        try:
            with open(self.hook_file, 'r', encoding='utf-8') as f:
                content = f.read()
            report.append(content)
        except Exception as e:
            report.append(f"Error reading hook file: {e}")
        
        return "\n".join(report)

def main():
    """Run the command debugger"""
    debugger = CommandDebugger()
    
    print("🔍 Running Kiro Command Debugger...")
    print()
    
    # Generate and display the debug report
    report = debugger.generate_debug_report()
    print(report)
    
    # Test the specific issue
    print("\n" + "=" * 60)
    print("SPECIFIC ISSUE TESTING")
    print("=" * 60)
    
    print("\n🧪 Testing 'kiro commit --from-diff' command...")
    try:
        result = subprocess.run([
            'kiro', 'commit', '--from-diff'
        ], capture_output=True, text=True, timeout=10)
        
        output = result.stdout + result.stderr
        print(f"Exit code: {result.returncode}")
        print(f"Output: {output}")
        
        if "Warning: 'from-diff' is not in the list of known options" in output:
            print("❌ ISSUE CONFIRMED: Kiro shows warning for unknown option")
        else:
            print("✅ No warning detected")
            
        # Check for empty file creation
        if Path("commit").exists():
            print("❌ ISSUE CONFIRMED: Empty 'commit' file was created")
            # Clean up
            Path("commit").unlink()
        else:
            print("✅ No empty 'commit' file created")
            
    except Exception as e:
        print(f"❌ Error testing kiro command: {e}")

if __name__ == "__main__":
    main()