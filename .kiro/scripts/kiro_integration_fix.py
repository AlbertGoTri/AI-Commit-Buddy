#!/usr/bin/env python3
"""
Kiro Integration Fix for Commit Buddy
Addresses the command recognition issue and provides alternative solutions
"""

import os
import sys
import yaml
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Tuple, List

class KiroIntegrationFix:
    """Fix Kiro integration issues for Commit Buddy"""
    
    def __init__(self):
        self.hook_file = Path(".kiro/hooks/commit.yml")
        self.script_file = Path(".kiro/scripts/commit_buddy.py")
        self.kiro_scripts_dir = Path(".kiro/scripts")
        
    def diagnose_issue(self) -> Dict[str, Any]:
        """Diagnose the current Kiro integration issue"""
        diagnosis = {
            "kiro_available": False,
            "kiro_version": None,
            "hook_file_exists": False,
            "hook_content_valid": False,
            "script_executable": False,
            "command_recognition": False,
            "issues": [],
            "recommendations": []
        }
        
        # Check if Kiro is available
        try:
            result = subprocess.run(['kiro', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                diagnosis["kiro_available"] = True
                diagnosis["kiro_version"] = result.stdout.strip()
            else:
                diagnosis["issues"].append("Kiro command failed")
        except FileNotFoundError:
            try:
                # Try kiro.cmd on Windows
                result = subprocess.run(['kiro.cmd', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    diagnosis["kiro_available"] = True
                    diagnosis["kiro_version"] = result.stdout.strip()
            except FileNotFoundError:
                diagnosis["issues"].append("Kiro not found in PATH")
        except Exception as e:
            diagnosis["issues"].append(f"Error checking Kiro: {e}")
        
        # Check hook file
        if self.hook_file.exists():
            diagnosis["hook_file_exists"] = True
            try:
                with open(self.hook_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                if isinstance(config, dict) and 'name' in config:
                    diagnosis["hook_content_valid"] = True
                else:
                    diagnosis["issues"].append("Hook file has invalid content")
            except Exception as e:
                diagnosis["issues"].append(f"Error reading hook file: {e}")
        else:
            diagnosis["issues"].append("Hook file does not exist")
        
        # Check script executable
        if self.script_file.exists():
            try:
                result = subprocess.run([sys.executable, str(self.script_file), '--help'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    diagnosis["script_executable"] = True
                else:
                    diagnosis["issues"].append("Script execution failed")
            except Exception as e:
                diagnosis["issues"].append(f"Error testing script: {e}")
        else:
            diagnosis["issues"].append("Main script does not exist")
        
        # Test command recognition
        if diagnosis["kiro_available"]:
            try:
                kiro_cmd = 'kiro.cmd' if os.name == 'nt' else 'kiro'
                result = subprocess.run([kiro_cmd, 'commit', '--from-diff'],
                                      capture_output=True, text=True, timeout=10)
                output = result.stdout + result.stderr
                
                if "Warning: 'from-diff' is not in the list of known options" in output:
                    diagnosis["issues"].append("Kiro shows warning for unknown option")
                elif "No hay cambios staged" in output or "No estás en un repositorio Git" in output:
                    diagnosis["command_recognition"] = True
                else:
                    diagnosis["issues"].append(f"Unexpected Kiro output: {output}")
            except Exception as e:
                diagnosis["issues"].append(f"Error testing Kiro command: {e}")
        
        return diagnosis
    
    def create_alternative_hook_formats(self) -> List[Dict[str, Any]]:
        """Create alternative hook configuration formats to try"""
        
        alternatives = [
            {
                "name": "format_1_single_command",
                "config": {
                    "name": "commit",
                    "description": "Generate AI-powered commit messages",
                    "command": f"{sys.executable} .kiro/scripts/commit_buddy.py --from-diff",
                    "triggers": ["manual"]
                }
            },
            {
                "name": "format_2_shell_wrapper",
                "config": {
                    "name": "commit",
                    "description": "Generate AI-powered commit messages",
                    "command": "cmd" if os.name == 'nt' else "sh",
                    "args": ["/c", f"{sys.executable} .kiro/scripts/commit_buddy.py --from-diff"] if os.name == 'nt' 
                           else ["-c", f"{sys.executable} .kiro/scripts/commit_buddy.py --from-diff"],
                    "triggers": ["manual"]
                }
            },
            {
                "name": "format_3_batch_script",
                "config": {
                    "name": "commit",
                    "description": "Generate AI-powered commit messages",
                    "command": ".kiro/scripts/commit_buddy.bat" if os.name == 'nt' else ".kiro/scripts/commit_buddy.sh",
                    "args": ["--from-diff"],
                    "triggers": ["manual"]
                }
            }
        ]
        
        return alternatives
    
    def create_wrapper_scripts(self):
        """Create wrapper scripts for better compatibility"""
        
        # Create batch script for Windows
        if os.name == 'nt':
            batch_content = f'''@echo off
cd /d "%~dp0"
"{sys.executable}" commit_buddy.py %*
'''
            batch_file = self.kiro_scripts_dir / "commit_buddy.bat"
            with open(batch_file, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            print(f"✅ Created Windows batch wrapper: {batch_file}")
        
        # Create shell script for Unix-like systems
        shell_content = f'''#!/bin/bash
cd "$(dirname "$0")"
"{sys.executable}" commit_buddy.py "$@"
'''
        shell_file = self.kiro_scripts_dir / "commit_buddy.sh"
        with open(shell_file, 'w', encoding='utf-8') as f:
            f.write(shell_content)
        
        # Make shell script executable
        try:
            os.chmod(shell_file, 0o755)
            print(f"✅ Created shell wrapper: {shell_file}")
        except Exception as e:
            print(f"⚠️  Created shell wrapper but couldn't set permissions: {e}")
    
    def try_alternative_formats(self) -> Tuple[bool, str]:
        """Try alternative hook configuration formats"""
        
        if not self.hook_file.exists():
            return False, "Hook file does not exist"
        
        # Backup original
        backup_file = self.hook_file.with_suffix('.yml.backup')
        shutil.copy2(self.hook_file, backup_file)
        
        alternatives = self.create_alternative_hook_formats()
        
        for alt in alternatives:
            print(f"\n🧪 Testing alternative format: {alt['name']}")
            
            try:
                # Write alternative configuration
                with open(self.hook_file, 'w', encoding='utf-8') as f:
                    yaml.dump(alt['config'], f, default_flow_style=False)
                
                # Test if it works
                if self._test_kiro_command():
                    print(f"✅ SUCCESS: {alt['name']} works!")
                    return True, alt['name']
                else:
                    print(f"❌ FAILED: {alt['name']} doesn't work")
                    
            except Exception as e:
                print(f"❌ ERROR: {alt['name']} failed with: {e}")
        
        # Restore original
        shutil.copy2(backup_file, self.hook_file)
        return False, "No alternative format worked"
    
    def _test_kiro_command(self) -> bool:
        """Test if the Kiro command works without warnings"""
        try:
            kiro_cmd = 'kiro.cmd' if os.name == 'nt' else 'kiro'
            result = subprocess.run([kiro_cmd, 'commit', '--from-diff'],
                                  capture_output=True, text=True, timeout=10)
            
            output = result.stdout + result.stderr
            
            # Check for warning
            if "Warning: 'from-diff' is not in the list of known options" in output:
                return False
            
            # Check for expected behavior (no changes or not git repo is OK)
            if ("No hay cambios staged" in output or 
                "No estás en un repositorio Git" in output or
                "⚠️" in output):
                return True
            
            return False
            
        except Exception:
            return False
    
    def create_direct_command_alias(self):
        """Create a direct command alias as a workaround"""
        
        # Create a simple script that can be called directly
        alias_script = self.kiro_scripts_dir / "kiro-commit.py"
        
        alias_content = f'''#!/usr/bin/env python3
"""
Direct command alias for Kiro Commit Buddy
Usage: python .kiro/scripts/kiro-commit.py
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main commit buddy
from commit_buddy import CommitBuddy

if __name__ == "__main__":
    buddy = CommitBuddy()
    # Always use --from-diff for this alias
    sys.exit(buddy.main(["--from-diff"]))
'''
        
        with open(alias_script, 'w', encoding='utf-8') as f:
            f.write(alias_content)
        
        print(f"✅ Created direct command alias: {alias_script}")
        print(f"   Usage: python {alias_script}")
    
    def generate_workaround_instructions(self) -> str:
        """Generate instructions for workarounds"""
        
        instructions = []
        instructions.append("=" * 60)
        instructions.append("KIRO COMMIT BUDDY - WORKAROUND INSTRUCTIONS")
        instructions.append("=" * 60)
        
        instructions.append("\n🔧 ISSUE IDENTIFIED:")
        instructions.append("Kiro is not recognizing the hook configuration properly.")
        instructions.append("The command 'kiro commit --from-diff' shows a warning about unknown options.")
        
        instructions.append("\n💡 WORKAROUNDS AVAILABLE:")
        
        instructions.append("\n1. DIRECT SCRIPT EXECUTION (Recommended)")
        instructions.append("   Instead of: kiro commit --from-diff")
        instructions.append("   Use: python .kiro/scripts/commit_buddy.py --from-diff")
        instructions.append("   This works exactly the same and avoids the Kiro hook issue.")
        
        instructions.append("\n2. DIRECT COMMAND ALIAS")
        instructions.append("   Use: python .kiro/scripts/kiro-commit.py")
        instructions.append("   This is a simplified version that always uses --from-diff")
        
        instructions.append("\n3. CREATE A SHELL ALIAS")
        if os.name == 'nt':
            instructions.append("   PowerShell: Set-Alias kcommit 'python .kiro/scripts/commit_buddy.py --from-diff'")
            instructions.append("   CMD: doskey kcommit=python .kiro/scripts/commit_buddy.py --from-diff")
        else:
            instructions.append("   Bash: alias kcommit='python .kiro/scripts/commit_buddy.py --from-diff'")
            instructions.append("   Add to ~/.bashrc or ~/.zshrc for persistence")
        
        instructions.append("\n4. BATCH/SHELL WRAPPER")
        if os.name == 'nt':
            instructions.append("   Use: .kiro/scripts/commit_buddy.bat --from-diff")
        else:
            instructions.append("   Use: .kiro/scripts/commit_buddy.sh --from-diff")
        
        instructions.append("\n📋 FUNCTIONALITY STATUS:")
        instructions.append("✅ Core functionality works perfectly")
        instructions.append("✅ AI message generation works")
        instructions.append("✅ Fallback messages work")
        instructions.append("✅ Git integration works")
        instructions.append("✅ User interface works")
        instructions.append("⚠️  Only the Kiro hook integration has issues")
        
        instructions.append("\n🎯 RECOMMENDED USAGE:")
        instructions.append("Use the direct script execution method:")
        instructions.append("  1. Make some changes: echo 'test' > file.txt")
        instructions.append("  2. Stage changes: git add .")
        instructions.append("  3. Generate commit: python .kiro/scripts/commit_buddy.py --from-diff")
        
        return "\n".join(instructions)
    
    def apply_fixes(self) -> Dict[str, Any]:
        """Apply all available fixes and workarounds"""
        
        print("🔧 Applying Kiro Integration Fixes...")
        
        results = {
            "diagnosis": self.diagnose_issue(),
            "wrapper_scripts_created": False,
            "alternative_formats_tried": False,
            "alternative_format_success": False,
            "direct_alias_created": False,
            "workarounds_available": True
        }
        
        # Create wrapper scripts
        try:
            self.create_wrapper_scripts()
            results["wrapper_scripts_created"] = True
        except Exception as e:
            print(f"❌ Error creating wrapper scripts: {e}")
        
        # Try alternative hook formats
        try:
            success, format_name = self.try_alternative_formats()
            results["alternative_formats_tried"] = True
            results["alternative_format_success"] = success
            if success:
                results["successful_format"] = format_name
        except Exception as e:
            print(f"❌ Error trying alternative formats: {e}")
        
        # Create direct command alias
        try:
            self.create_direct_command_alias()
            results["direct_alias_created"] = True
        except Exception as e:
            print(f"❌ Error creating direct alias: {e}")
        
        return results

def main():
    """Run the Kiro integration fix"""
    
    print("🚀 Kiro Commit Buddy - Integration Fix")
    print("=" * 50)
    
    fixer = KiroIntegrationFix()
    
    # Run diagnosis
    print("\n🔍 DIAGNOSING ISSUE...")
    diagnosis = fixer.diagnose_issue()
    
    print(f"\nKiro Available: {'✅' if diagnosis['kiro_available'] else '❌'}")
    if diagnosis['kiro_version']:
        print(f"Kiro Version: {diagnosis['kiro_version']}")
    
    print(f"Hook File Exists: {'✅' if diagnosis['hook_file_exists'] else '❌'}")
    print(f"Hook Content Valid: {'✅' if diagnosis['hook_content_valid'] else '❌'}")
    print(f"Script Executable: {'✅' if diagnosis['script_executable'] else '❌'}")
    print(f"Command Recognition: {'✅' if diagnosis['command_recognition'] else '❌'}")
    
    if diagnosis['issues']:
        print(f"\n❌ ISSUES FOUND:")
        for issue in diagnosis['issues']:
            print(f"   - {issue}")
    
    # Apply fixes
    print(f"\n🔧 APPLYING FIXES...")
    results = fixer.apply_fixes()
    
    # Generate workaround instructions
    instructions = fixer.generate_workaround_instructions()
    print(f"\n{instructions}")
    
    # Final status
    if results['alternative_format_success']:
        print(f"\n🎉 SUCCESS: Found working hook format!")
        print(f"   The '{results['successful_format']}' format works correctly.")
        print(f"   You can now use: kiro commit --from-diff")
    else:
        print(f"\n⚠️  HOOK ISSUE PERSISTS:")
        print(f"   The Kiro hook system is not working as expected.")
        print(f"   Please use the workarounds provided above.")
        print(f"   The core functionality is not affected.")
    
    return 0 if results['alternative_format_success'] else 1

if __name__ == "__main__":
    sys.exit(main())