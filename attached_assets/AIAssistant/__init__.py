"""
UE5 AI Assistant - Modular Architecture
Author: Noah Butcher
Version: 2.0 (October 2025)

A modular AI assistant system for Unreal Engine 5.6+ that provides:
- Smart viewport and scene analysis
- Natural language command execution
- Async API communication
- Extensible action system
"""

__version__ = "2.0.0"
__author__ = "Noah Butcher"

# Core components will be imported here
from . import action_executor, api_client, config, context_collector, ui_manager, utils

__all__ = [
    "config",
    "utils",
    "api_client",
    "context_collector",
    "action_executor",
    "ui_manager",
]
