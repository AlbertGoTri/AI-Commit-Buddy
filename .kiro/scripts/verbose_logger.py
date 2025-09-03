"""
Verbose logging system for Kiro Commit Buddy
Provides detailed logging to track API call flow and identify failure points
"""

import os
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

class VerboseLogger:
    """Centralized logging system with multiple output options"""

    def __init__(self, enabled: bool = False, log_file: Optional[str] = None):
        self.enabled = enabled
        self.log_file = log_file
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create logs directory if logging to file
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

    def enable(self):
        """Enable verbose logging"""
        self.enabled = True

    def disable(self):
        """Disable verbose logging"""
        self.enabled = False

    def log(self, message: str, level: str = "INFO", component: str = "MAIN"):
        """
        Log a message with timestamp and component info
        
        Args:
            message: The message to log
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            component: Component name (API, GIT, UI, etc.)
        """
        if not self.enabled:
            return

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
        log_entry = f"[{timestamp}] [{level:7}] [{component:8}] {message}"
        
        # Output to console
        print(log_entry)
        
        # Output to file if configured
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
            except Exception as e:
                print(f"[ERROR] Failed to write to log file: {e}")

    def debug(self, message: str, component: str = "DEBUG"):
        """Log debug message"""
        self.log(message, "DEBUG", component)

    def info(self, message: str, component: str = "INFO"):
        """Log info message"""
        self.log(message, "INFO", component)

    def warning(self, message: str, component: str = "WARNING"):
        """Log warning message"""
        self.log(message, "WARNING", component)

    def error(self, message: str, component: str = "ERROR"):
        """Log error message"""
        self.log(message, "ERROR", component)

    def log_api_request(self, endpoint: str, headers: Dict[str, Any], payload: Dict[str, Any]):
        """Log API request details"""
        if not self.enabled:
            return

        # Sanitize headers (hide API key)
        safe_headers = {k: (v[:20] + "..." if k == "Authorization" else v) for k, v in headers.items()}
        
        self.debug(f"API Request to: {endpoint}", "API")
        self.debug(f"Headers: {json.dumps(safe_headers, indent=2)}", "API")
        self.debug(f"Payload: {json.dumps(payload, indent=2)}", "API")

    def log_api_response(self, status_code: int, headers: Dict[str, Any], response_data: Any):
        """Log API response details"""
        if not self.enabled:
            return

        self.debug(f"API Response Status: {status_code}", "API")
        self.debug(f"Response Headers: {dict(headers)}", "API")
        
        if isinstance(response_data, dict):
            self.debug(f"Response Data: {json.dumps(response_data, indent=2)}", "API")
        else:
            self.debug(f"Response Data: {str(response_data)[:500]}...", "API")

    def log_git_operation(self, command: str, result: Any, error: Optional[str] = None):
        """Log Git operation details"""
        if not self.enabled:
            return

        self.debug(f"Git Command: {command}", "GIT")
        if error:
            self.error(f"Git Error: {error}", "GIT")
        else:
            self.debug(f"Git Result: {str(result)[:200]}...", "GIT")

    def log_message_generation(self, source: str, input_data: str, output_message: str):
        """Log message generation details"""
        if not self.enabled:
            return

        self.debug(f"Message Source: {source}", "MSG_GEN")
        self.debug(f"Input Length: {len(input_data)} chars", "MSG_GEN")
        self.debug(f"Generated Message: {output_message}", "MSG_GEN")

    def log_fallback_trigger(self, reason: str, context: Dict[str, Any]):
        """Log when fallback is triggered and why"""
        if not self.enabled:
            return

        self.warning(f"Fallback triggered: {reason}", "FALLBACK")
        self.debug(f"Fallback context: {json.dumps(context, indent=2)}", "FALLBACK")

    def log_user_interaction(self, action: str, details: str):
        """Log user interactions"""
        if not self.enabled:
            return

        self.info(f"User {action}: {details}", "UI")

    def create_session_summary(self) -> Dict[str, Any]:
        """Create a summary of the current session"""
        return {
            "session_id": self.session_id,
            "enabled": self.enabled,
            "log_file": self.log_file,
            "timestamp": datetime.now().isoformat()
        }

# Global logger instance
_global_logger = VerboseLogger()

def get_logger() -> VerboseLogger:
    """Get the global logger instance"""
    return _global_logger

def enable_verbose_logging(log_file: Optional[str] = None):
    """Enable verbose logging globally"""
    global _global_logger
    _global_logger.enabled = True
    if log_file:
        _global_logger.log_file = log_file

def disable_verbose_logging():
    """Disable verbose logging globally"""
    global _global_logger
    _global_logger.enabled = False

def is_verbose_enabled() -> bool:
    """Check if verbose logging is enabled"""
    return _global_logger.enabled

# Environment variable check
if os.getenv("KIRO_COMMIT_BUDDY_VERBOSE", "").lower() in ["1", "true", "yes"]:
    enable_verbose_logging()
    _global_logger.info("Verbose logging enabled via environment variable", "INIT")