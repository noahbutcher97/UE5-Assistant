"""
End-to-End Workflow Integration Tests
Tests complete user workflows from dashboard to UE5 execution.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import time

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main import app

client = TestClient(app)


class TestCompleteUserWorkflows:
    """Test complete user workflows end-to-end."""
    
    def setup_method(self):
        """Setup test environment for each test."""
        self.project_id = f"e2e_test_{int(time.time())}"
        self.project_name = "E2E Test Project"
        
        # Register test project
        client.post("/api/ue5/register_http", json={
            "project_id": self.project_id,
            "project_name": self.project_name
        })
        
        client.post("/api/register_project", json={
            "project_id": self.project_id,
            "project_data": {
                "name": self.project_name,
                "path": "D:/Projects/E2ETest"
            }
        })
        
        client.post("/api/set_active_project", json={
            "project_id": self.project_id
        })
    
    def test_workflow_describe_viewport(self):
        """Test: User clicks 'Describe Viewport' → Command sent → Response received."""
        # Step 1: User clicks button (sends command)
        send_response = client.post("/send_command_to_ue5", json={
            "project_id": self.project_id,
            "command": {
                "type": "execute_action",
                "action": "describe_viewport",
                "params": {}
            }
        })
        assert send_response.status_code == 200
        
        # Step 2: Client polls for command
        poll_response = client.post("/api/ue5/poll", json={
            "project_id": self.project_id
        })
        commands = poll_response.json()["commands"]
        assert len(commands) > 0
        assert commands[0]["action"] == "describe_viewport"
        
        # Step 3: Client sends response
        response_data = client.post("/api/ue5/response", json={
            "project_id": self.project_id,
            "response": {
                "request_id": commands[0].get("request_id", "test_req"),
                "success": True,
                "data": "Viewport contains 5 actors"
            }
        })
        assert response_data.json()["success"] is True
    
    @patch('app.routes.call_openai_chat')
    def test_workflow_ai_widget_generation(self, mock_openai):
        """Test: User generates widget → AI creates code → UE5 receives it."""
        mock_openai.return_value = """
        ```python
        import unreal
        
        class MyGeneratedWidget:
            def run(self):
                print("Widget running")
        ```
        """
        
        # Step 1: User submits widget request
        gen_response = client.post("/api/generate_utility", json={
            "widget_name": "E2ETestWidget",
            "description": "A test widget for E2E testing",
            "project_id": self.project_id
        })
        assert gen_response.status_code == 200
        
        # Step 2: Check if command was queued for UE5
        poll_response = client.post("/api/ue5/poll", json={
            "project_id": self.project_id
        })
        commands = poll_response.json()["commands"]
        
        # Should have write_utility_file command
        write_commands = [c for c in commands if c.get("action") == "write_utility_file"]
        assert len(write_commands) > 0
    
    @patch('app.routes.call_openai_chat')
    def test_workflow_ai_chat_with_context(self, mock_openai):
        """Test: User asks AI question → AI uses project context → Returns answer."""
        mock_openai.return_value = "Based on your project, you should..."
        
        # Step 1: User asks question
        chat_response = client.post("/answer_with_context", json={
            "query": "What should I build next?",
            "project_id": self.project_id
        })
        assert chat_response.status_code == 200
        
        # Verify AI was called with context
        assert mock_openai.called
    
    def test_workflow_project_switch(self):
        """Test: User switches project → New project becomes active → Commands route correctly."""
        # Create second project
        project_2 = f"e2e_test_2_{int(time.time())}"
        
        client.post("/api/register_project", json={
            "project_id": project_2,
            "project_data": {
                "name": "Second Project",
                "path": "D:/Projects/Project2"
            }
        })
        
        # Switch to second project
        switch_response = client.post("/api/set_active_project", json={
            "project_id": project_2
        })
        assert switch_response.json()["success"] is True
        
        # Verify active project changed
        active_response = client.get("/api/active_project")
        assert active_response.json()["project_id"] == project_2
    
    def test_workflow_auto_update(self):
        """Test: User triggers update → Command sent to UE5 → Update initiated."""
        # Trigger update
        update_response = client.post("/api/trigger_auto_update", json={
            "project_id": self.project_id
        })
        assert update_response.status_code == 200
        
        # Check if update command was queued
        poll_response = client.post("/api/ue5/poll", json={
            "project_id": self.project_id
        })
        commands = poll_response.json()["commands"]
        
        # Should have auto_update command
        update_commands = [c for c in commands if c.get("action") == "auto_update"]
        assert len(update_commands) > 0


class TestErrorRecoveryWorkflows:
    """Test error recovery and resilience workflows."""
    
    def test_recovery_from_disconnection(self):
        """Test: Client disconnects → Reconnects → Resumes normally."""
        project_id = "recovery_test"
        
        # Register
        client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Recovery Test"
        })
        
        # Send command
        client.post("/send_command_to_ue5", json={
            "project_id": project_id,
            "command": {"type": "test"}
        })
        
        # Simulate reconnect
        reconnect_response = client.post("/api/reconnect", json={
            "project_id": project_id
        })
        assert reconnect_response.status_code == 200
        
        # Should still be able to poll
        poll_response = client.post("/api/ue5/poll", json={
            "project_id": project_id
        })
        assert poll_response.status_code == 200
    
    def test_recovery_from_invalid_command(self):
        """Test: Invalid command sent → Error handled → System continues."""
        project_id = "invalid_cmd_test"
        
        client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Invalid Command Test"
        })
        
        # Send invalid command
        response = client.post("/send_command_to_ue5", json={
            "project_id": project_id,
            "command": {
                "type": "execute_action",
                "action": "nonexistent_action_xyz"
            }
        })
        
        # Should handle gracefully
        assert response.status_code in [200, 400]
        
        # System should still work
        poll_response = client.post("/api/ue5/poll", json={
            "project_id": project_id
        })
        assert poll_response.status_code == 200


class TestConcurrentUserWorkflows:
    """Test multiple users/projects operating concurrently."""
    
    def test_multiple_projects_simultaneously(self):
        """Test: Multiple projects connected → Commands route to correct project."""
        # Create multiple projects
        projects = []
        for i in range(3):
            project_id = f"concurrent_test_{i}_{int(time.time())}"
            projects.append(project_id)
            
            client.post("/api/ue5/register_http", json={
                "project_id": project_id,
                "project_name": f"Concurrent Project {i}"
            })
        
        # Send different commands to each
        for i, project_id in enumerate(projects):
            client.post("/send_command_to_ue5", json={
                "project_id": project_id,
                "command": {
                    "type": "execute_action",
                    "action": f"test_action_{i}"
                }
            })
        
        # Verify each gets only its command
        for i, project_id in enumerate(projects):
            poll_response = client.post("/api/ue5/poll", json={
                "project_id": project_id
            })
            commands = poll_response.json()["commands"]
            
            if len(commands) > 0:
                # Should have command for this project only
                assert commands[0]["action"] == f"test_action_{i}"


class TestDataPersistenceWorkflows:
    """Test data persistence across sessions."""
    
    def test_project_data_persists(self):
        """Test: Project registered → Data persists → Can be retrieved."""
        project_id = "persistence_test"
        
        # Register with metadata
        client.post("/api/register_project", json={
            "project_id": project_id,
            "project_data": {
                "name": "Persistence Test",
                "path": "D:/Projects/PersistenceTest",
                "custom_field": "custom_value"
            }
        })
        
        # Retrieve projects
        response = client.get("/api/projects")
        projects = response.json()
        
        assert project_id in projects
        project_data = projects[project_id]
        assert project_data.get("project_data", {}).get("custom_field") == "custom_value"
    
    def test_operation_history_persists(self):
        """Test: Operations executed → History maintained → Can be queried."""
        # Execute some operations
        client.post("/send_command_to_ue5", json={
            "project_id": "history_test",
            "command": {"type": "test"}
        })
        
        # Get operation history
        response = client.get("/api/operations")
        operations = response.json()
        
        assert isinstance(operations, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
