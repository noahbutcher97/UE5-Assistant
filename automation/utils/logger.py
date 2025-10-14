"""
Logging utility for automation operations.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


class AutomationLogger:
    """Centralized logging for automation operations."""
    
    def __init__(self, log_dir: Path = None, log_level: str = "INFO"):
        """Initialize automation logger."""
        self.log_dir = log_dir or Path.cwd() / "automation" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("automation")
        self.logger.setLevel(getattr(logging, log_level))
        
        log_file = self.log_dir / f"automation_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
