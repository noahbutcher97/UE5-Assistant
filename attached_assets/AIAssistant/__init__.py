"""
UE5 AI Assistant - Modular Architecture
Author: Noah Butcher
Version: 2.0 (October 2025)

A modular AI assistant system for Unreal Engine 5.6+ that provides:
- Smart viewport and scene analysis
- Natural language command execution
- Async API communication
- Extensible action system

Quick Start:
    from AIAssistant import send_command
    response = send_command("what do I see?")
"""

__version__ = "2.0.0"
__author__ = "Noah Butcher"

# Core components
from . import config
from . import utils
from . import api_client
from . import async_client
from . import context_collector
from . import action_executor
from . import ui_manager
from . import main

# Main entry points for convenience
from .main import send_command, get_assistant
from .config import get_config
from .action_executor import get_executor

__all__ = [
    # Main functions
    "send_command",
    "get_assistant",
    "get_config",
    "get_executor",
    # Modules
    "config",
    "utils",
    "api_client",
    "async_client",
    "context_collector",
    "action_executor",
    "ui_manager",
    "main",
]
