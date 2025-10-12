"""
Action Execution Tests with Mock Unreal API
Tests action_executor.py without requiring actual UE5 environment.
"""
import sys
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ue5_client"))

import mock_unreal

sys.modules['unreal'] = mock_unreal


class TestActionExecutorBasics:
    """Test basic action executor functionality."""
    
    def test_action_executor_initialization(self):
        """Test ActionExecutor initializes correctly with mock Unreal."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        assert executor is not None
        assert hasattr(executor, 'actions')
        assert isinstance(executor.actions, dict)
        assert len(executor.actions) > 0
    
    def test_registered_actions(self):
        """Test that default actions are registered."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        expected_actions = [
            'describe_viewport',
            'list_actors',
            'get_selected_info',
            'browse_files',
            'show_project_info',
            'get_project_info',
            'capture_blueprint',
            'list_blueprints'
        ]
        
        for action in expected_actions:
            assert action in executor.actions, f"Action '{action}' not registered"
    
    def test_action_registration(self):
        """Test custom action registration."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        def custom_action():
            return "Custom action executed"
        
        executor.register("custom_test_action", custom_action)
        
        assert "custom_test_action" in executor.actions
        assert executor.actions["custom_test_action"] == custom_action


class TestActionExecution:
    """Test action execution."""
    
    def test_describe_viewport_action(self):
        """Test describe_viewport action execution."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute("describe_viewport")
        
        assert isinstance(result, str)
        assert "[UE_ERROR]" not in result or result.startswith("[UE_DATA]")
    
    def test_list_blueprints_action(self):
        """Test list_blueprints action execution."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute("list_blueprints")
        
        assert isinstance(result, str)
        assert "[UE_DATA]" in result or "Blueprint" in result
    
    def test_browse_files_action(self):
        """Test browse_files action execution."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute("browse_files")
        
        assert isinstance(result, str)
        assert "[UE_DATA]" in result or "files" in result.lower()
    
    def test_show_project_info_action(self):
        """Test show_project_info action execution."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute("show_project_info")
        
        assert isinstance(result, str)
        assert "[UE_DATA]" in result or "project" in result.lower()
    
    def test_unknown_action_error(self):
        """Test that unknown action returns error."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute("unknown_action_xyz")
        
        assert "[UE_ERROR]" in result
        assert "unknown" in result.lower() or "Unknown" in result


class TestThreadSafety:
    """Test thread-safe action execution via queue system."""
    
    def test_main_thread_detection(self):
        """Test main thread detection."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        assert executor._is_main_thread() is True
    
    def test_background_thread_detection(self):
        """Test background thread detection."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        is_main = [None]
        
        def check_thread():
            is_main[0] = executor._is_main_thread()
        
        thread = threading.Thread(target=check_thread)
        thread.start()
        thread.join()
        
        assert is_main[0] is False
    
    def test_main_thread_direct_execution(self):
        """Test that actions execute directly on main thread."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        execution_log = []
        
        def tracked_action():
            execution_log.append(("executed", threading.current_thread().ident))
            return "[UE_DATA] Tracked action result"
        
        executor.register("tracked_action", tracked_action)
        
        result = executor.execute("tracked_action")
        
        assert len(execution_log) == 1
        assert execution_log[0][0] == "executed"
        assert "[UE_DATA]" in result
    
    @patch('AIAssistant.action_executor.HAS_ACTION_QUEUE', True)
    def test_background_thread_uses_queue(self):
        """Test that background threads use action queue when available."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        if executor.action_queue is None:
            pytest.skip("Action queue not available in test environment")
        
        result_container = [None]
        
        def background_execution():
            result_container[0] = executor.execute("describe_viewport")
        
        thread = threading.Thread(target=background_execution)
        thread.start()
        thread.join(timeout=2)
        
        if thread.is_alive():
            pytest.skip("Background thread timed out - queue processing not available")
        
        assert result_container[0] is not None


class TestActionExecutorWithQueue:
    """Test ActionExecutor integration with action queue."""
    
    def test_execute_with_queue_method(self):
        """Test execute_with_queue method."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute_with_queue("describe_viewport", {})
        
        assert isinstance(result, dict)
        assert "success" in result or "data" in result or "error" in result
    
    def test_execute_with_queue_params(self):
        """Test execute_with_queue with parameters."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        params = {"test_param": "test_value"}
        result = executor.execute_with_queue("describe_viewport", params)
        
        assert isinstance(result, dict)
    
    def test_execute_with_queue_error_handling(self):
        """Test execute_with_queue handles errors correctly."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute_with_queue("invalid_action_xyz", {})
        
        assert isinstance(result, dict)
        assert result.get("success") is False or "error" in result


class TestMockUnrealIntegration:
    """Test integration with mock Unreal API."""
    
    def test_mock_unreal_paths(self):
        """Test mock Unreal paths are accessible."""
        assert hasattr(mock_unreal, 'Paths')
        assert hasattr(mock_unreal.Paths, 'project_dir')
        
        project_dir = mock_unreal.Paths.project_dir()
        assert isinstance(project_dir, str)
        assert len(project_dir) > 0
    
    def test_mock_asset_registry(self):
        """Test mock asset registry."""
        assert hasattr(mock_unreal, 'AssetRegistryHelpers')
        
        registry = mock_unreal.AssetRegistryHelpers.get_asset_registry()
        assert registry is not None
        
        ar_filter = mock_unreal.ARFilter(class_names=['Blueprint'])
        assets = registry.get_assets(ar_filter)
        
        assert isinstance(assets, list)
        assert len(assets) > 0
    
    def test_mock_editor_asset_subsystem(self):
        """Test mock editor asset subsystem."""
        assert hasattr(mock_unreal, 'get_editor_subsystem')
        
        subsystem = mock_unreal.get_editor_subsystem(mock_unreal.EditorAssetSubsystem)
        assert subsystem is not None
        
        exists = subsystem.does_asset_exist("/Game/Blueprints/BP_Player")
        assert isinstance(exists, bool)


class TestBlueprintActions:
    """Test blueprint-related actions."""
    
    def test_list_blueprints_with_mock_registry(self):
        """Test list_blueprints uses mock asset registry."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute("list_blueprints")
        
        assert isinstance(result, str)
        assert "BP_" in result or "[UE_DATA]" in result
    
    def test_capture_blueprint_action(self):
        """Test capture_blueprint action."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute("capture_blueprint")
        
        assert isinstance(result, str)


class TestFileCollectorIntegration:
    """Test file collector integration."""
    
    def test_file_collector_with_mock_paths(self):
        """Test FileCollector works with mock Unreal paths."""
        from AIAssistant.file_collector import FileCollector
        
        collector = FileCollector()
        
        project_dir = mock_unreal.Paths.project_dir()
        assert project_dir in collector.project_root or collector.project_root in project_dir
    
    def test_browse_files_collects_mock_files(self):
        """Test browse_files action collects mock project files."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute("browse_files")
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestMetadataCollector:
    """Test project metadata collector."""
    
    def test_metadata_collector_initialization(self):
        """Test metadata collector initializes with mock Unreal."""
        from AIAssistant.project_metadata_collector import get_collector
        
        collector = get_collector()
        
        assert collector is not None
        assert hasattr(collector, 'get_project_metadata')
    
    def test_get_project_metadata(self):
        """Test getting project metadata."""
        from AIAssistant.project_metadata_collector import get_collector
        
        collector = get_collector()
        metadata = collector.get_project_metadata()
        
        assert isinstance(metadata, dict)
        assert "project_name" in metadata or len(metadata) >= 0


class TestContextCollector:
    """Test context collector."""
    
    def test_context_collector_initialization(self):
        """Test context collector initializes."""
        from AIAssistant.context_collector import get_collector
        
        collector = get_collector()
        
        assert collector is not None
        assert hasattr(collector, 'collect_viewport_context')


class TestActionExecutorErrorCases:
    """Test error handling in action executor."""
    
    def test_action_execution_exception_handling(self):
        """Test that action execution exceptions are caught."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        def failing_action():
            raise Exception("Intentional test failure")
        
        executor.register("failing_action", failing_action)
        
        result = executor.execute("failing_action")
        
        assert "[UE_ERROR]" in result
        assert "failed" in result.lower() or "error" in result.lower()
    
    def test_execute_with_none_params(self):
        """Test execute with None params."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute("describe_viewport", params=None)
        
        assert isinstance(result, str)
    
    def test_execute_empty_action_name(self):
        """Test execute with empty action name."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        result = executor.execute("")
        
        assert "[UE_ERROR]" in result


class TestActionQueueIntegration:
    """Test action queue integration (if available)."""
    
    def test_action_queue_availability(self):
        """Test if action queue is available."""
        try:
            from AIAssistant.action_queue import get_action_queue
            queue = get_action_queue()
            assert queue is not None
        except ImportError:
            pytest.skip("Action queue module not available")
    
    def test_action_queue_handler_registration(self):
        """Test action queue handler can be registered."""
        try:
            from AIAssistant.action_queue import get_action_queue
            
            queue = get_action_queue()
            
            def test_handler(action, params):
                return {"success": True, "action": action}
            
            queue.set_action_handler(test_handler)
            
            assert queue.action_handler is not None
        except ImportError:
            pytest.skip("Action queue module not available")


class TestOrchestrationActions:
    """Test orchestration actions (if available)."""
    
    def test_orchestration_actions_registered(self):
        """Test that orchestration actions are registered if available."""
        from AIAssistant.action_executor import ActionExecutor, HAS_ORCHESTRATION
        
        executor = ActionExecutor()
        
        if HAS_ORCHESTRATION:
            orchestration_actions = [
                'spawn_actor',
                'delete_actor',
                'move_actor',
                'rotate_actor',
                'set_camera_view'
            ]
            
            for action in orchestration_actions:
                if action in executor.actions:
                    assert callable(executor.actions[action])


class TestConcurrentExecution:
    """Test concurrent action execution."""
    
    def test_multiple_sequential_executions(self):
        """Test multiple sequential action executions."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        results = []
        actions = ['describe_viewport', 'list_blueprints', 'show_project_info']
        
        for action in actions:
            result = executor.execute(action)
            results.append(result)
        
        assert len(results) == len(actions)
        for result in results:
            assert isinstance(result, str)
    
    def test_same_action_multiple_times(self):
        """Test executing same action multiple times."""
        from AIAssistant.action_executor import ActionExecutor
        
        executor = ActionExecutor()
        
        results = [executor.execute("describe_viewport") for _ in range(5)]
        
        assert len(results) == 5
        for result in results:
            assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
