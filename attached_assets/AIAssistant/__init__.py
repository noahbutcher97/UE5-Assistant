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
from . import (
    action_executor,
    api_client,
    async_client,
    config,
    context_collector,
    main,
    ui_manager,
    utils,
)
from .action_executor import get_executor
from .config import get_config

# Main entry points for convenience
from .main import get_assistant, send_command

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
