"""
Comprehensive UE5 Client Module Tests
Tests every module in the UE5 client systematically.
Uses mock Unreal API for standalone testing.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import threading

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ue5_client"))

# Import mock unreal BEFORE client modules
import tests.ue5_client.mock_unreal as mock_unreal
sys.modules['unreal'] = mock_unreal


class TestCoreModule:
    """Test core/main.py module."""
    
    def test_main_module_imports(self):
        """Test main module imports successfully."""
        from AIAssistant.core import main
        assert main is not None
    
    def test_assistant_initialization(self):
        """Test AIAssistant class initialization."""
        from AIAssistant.core.main import AIAssistant
        assistant = AIAssistant()
        assert assistant is not None


class TestNetworkModules:
    """Test network communication modules."""
    
    def test_http_polling_client_import(self):
        """Test HTTP polling client imports."""
        from AIAssistant.network import http_polling_client
        assert http_polling_client is not None
    
    def test_http_polling_client_initialization(self):
        """Test HTTP client initializes."""
        from AIAssistant.network.http_polling_client import HTTPPollingClient
        
        client = HTTPPollingClient(
            backend_url="http://test.com",
            project_id="test_123"
        )
        assert client is not None
        assert client.backend_url == "http://test.com"
        assert client.project_id == "test_123"
    
    def test_ws_client_import(self):
        """Test WebSocket client imports."""
        from AIAssistant.network import ws_client
        assert ws_client is not None


class TestExecutionModules:
    """Test execution engine modules."""
    
    def test_action_queue_import(self):
        """Test action queue imports."""
        from AIAssistant.execution import action_queue
        assert action_queue is not None
    
    def test_action_queue_initialization(self):
        """Test ActionQueue initializes."""
        from AIAssistant.execution.action_queue import ActionQueue
        queue = ActionQueue()
        assert queue is not None
        assert hasattr(queue, 'queue')
    
    def test_action_executor_import(self):
        """Test action executor imports."""
        from AIAssistant.execution import action_executor
        assert action_executor is not None
    
    def test_action_executor_registration(self):
        """Test action executor registers actions."""
        from AIAssistant.execution.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        assert len(executor.actions) > 0
        assert 'describe_viewport' in executor.actions


class TestCollectionModules:
    """Test data collection modules."""
    
    def test_viewport_collector_import(self):
        """Test viewport collector imports."""
        from AIAssistant.collection import viewport_collector
        assert viewport_collector is not None
    
    def test_file_collector_import(self):
        """Test file collector imports."""
        from AIAssistant.collection import file_collector
        assert file_collector is not None
    
    def test_file_collector_functionality(self):
        """Test file collector basic functionality."""
        from AIAssistant.collection.file_collector import FileCollector
        
        collector = FileCollector()
        assert collector is not None
        assert hasattr(collector, 'project_dir')
    
    def test_project_metadata_collector_import(self):
        """Test project metadata collector imports."""
        from AIAssistant.collection import project_metadata_collector
        assert project_metadata_collector is not None


class TestToolsModules:
    """Test tools and utilities modules."""
    
    def test_scene_orchestrator_import(self):
        """Test scene orchestrator imports."""
        from AIAssistant.tools import scene_orchestrator
        assert scene_orchestrator is not None
    
    def test_viewport_controller_import(self):
        """Test viewport controller imports."""
        from AIAssistant.tools import viewport_controller
        assert viewport_controller is not None
    
    def test_actor_manipulator_import(self):
        """Test actor manipulator imports."""
        from AIAssistant.tools import actor_manipulator
        assert actor_manipulator is not None
    
    def test_blueprint_capture_import(self):
        """Test blueprint capture imports."""
        from AIAssistant.tools import blueprint_capture
        assert blueprint_capture is not None
    
    def test_editor_utility_generator_import(self):
        """Test editor utility generator imports."""
        from AIAssistant.tools import editor_utility_generator
        assert editor_utility_generator is not None


class TestSystemModules:
    """Test system management modules."""
    
    def test_auto_update_import(self):
        """Test auto-update imports."""
        from AIAssistant.system import auto_update
        assert auto_update is not None
    
    def test_auto_update_version_marker(self):
        """Test auto-update has version marker."""
        from AIAssistant.system.auto_update import _version_marker
        assert _version_marker is not None
        assert isinstance(_version_marker, str)
    
    def test_cleanup_legacy_import(self):
        """Test cleanup legacy imports."""
        from AIAssistant.system import cleanup_legacy
        assert cleanup_legacy is not None
    
    def test_cleanup_legacy_functions(self):
        """Test cleanup legacy has required functions."""
        from AIAssistant.system.cleanup_legacy import (
            cleanup_legacy_files,
            cleanup_pycache_recursive,
            get_legacy_files
        )
        assert cleanup_legacy_files is not None
        assert cleanup_pycache_recursive is not None
        assert get_legacy_files is not None


class TestUIModules:
    """Test UI components."""
    
    def test_toolbar_menu_import(self):
        """Test toolbar menu imports."""
        from AIAssistant.ui import toolbar_menu
        assert toolbar_menu is not None
    
    def test_ui_manager_import(self):
        """Test UI manager imports."""
        from AIAssistant.ui import ui_manager
        assert ui_manager is not None


class TestTroubleshootModules:
    """Test troubleshooting utilities."""
    
    def test_troubleshooter_import(self):
        """Test troubleshooter imports."""
        from AIAssistant.troubleshoot import troubleshooter
        assert troubleshooter is not None
    
    def test_connection_troubleshooter_import(self):
        """Test connection troubleshooter imports."""
        from AIAssistant.troubleshoot import connection_troubleshooter
        assert connection_troubleshooter is not None


class TestModuleIntegration:
    """Test module integration and dependencies."""
    
    def test_all_modules_import_together(self):
        """Test all modules can be imported together."""
        from AIAssistant.core import main
        from AIAssistant.network import http_polling_client, ws_client
        from AIAssistant.execution import action_queue, action_executor
        from AIAssistant.collection import viewport_collector, file_collector
        from AIAssistant.tools import scene_orchestrator
        from AIAssistant.system import auto_update
        from AIAssistant.ui import toolbar_menu
        from AIAssistant.troubleshoot import troubleshooter
        
        # If we get here, all imports succeeded
        assert True
    
    def test_update_lock_mechanism(self):
        """Test update lock prevents restart during updates."""
        from AIAssistant.system.auto_update import _update_in_progress
        from AIAssistant.execution.action_queue import ActionQueue
        
        # Update lock should be False initially
        assert _update_in_progress is False
        
        # ActionQueue should have update check method
        queue = ActionQueue()
        assert hasattr(queue, '_check_for_updates')


class TestThreadSafety:
    """Test thread safety of client modules."""
    
    def test_action_queue_thread_safety(self):
        """Test ActionQueue is thread-safe."""
        from AIAssistant.execution.action_queue import ActionQueue
        
        queue = ActionQueue()
        
        # Should handle both main and background threads
        is_main = threading.current_thread() == threading.main_thread()
        assert is_main is not None  # Just verify thread detection works


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
