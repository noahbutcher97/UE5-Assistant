"""
Comprehensive Backend Routes Testing
Tests every route, handler, and endpoint in the backend API.
Organized by functional area for maintainability.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main import app

client = TestClient(app)


class TestHTTPPollingRoutes:
    """Test HTTP polling endpoints for UE5 client communication."""
    
    def test_register_http_success(self):
        """Test successful HTTP client registration."""
        response = client.post("/api/ue5/register_http", json={
            "project_id": "http_reg_test",
            "project_name": "HTTP Registration Test"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_register_http_missing_data(self):
        """Test registration with missing required data."""
        response = client.post("/api/ue5/register_http", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
    
    def test_poll_commands(self):
        """Test polling for commands."""
        project_id = "poll_test_route"
        
        # Register first
        client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Poll Test"
        })
        
        # Poll for commands
        response = client.post("/api/ue5/poll", json={
            "project_id": project_id
        })
        assert response.status_code == 200
        data = response.json()
        assert "commands" in data
        assert isinstance(data["commands"], list)
    
    def test_submit_response(self):
        """Test submitting command response."""
        response = client.post("/api/ue5/response", json={
            "project_id": "response_test",
            "response": {
                "request_id": "test_123",
                "success": True,
                "data": "Response data"
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_heartbeat(self):
        """Test heartbeat keep-alive."""
        project_id = "heartbeat_test_route"
        
        # Register
        client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Heartbeat Test"
        })
        
        # Send heartbeat
        response = client.post("/api/ue5/heartbeat", json={
            "project_id": project_id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestWebSocketRoutes:
    """Test WebSocket connection endpoints."""
    
    def test_ws_connect_endpoint_exists(self):
        """Test WebSocket connect endpoint exists."""
        # WebSocket endpoints can't be tested with TestClient easily
        # Just verify the route structure
        from main import app
        routes = [route.path for route in app.routes]
        assert "/ws/{project_id}" in routes or any("/ws" in r for r in routes)


class TestProjectManagementRoutes:
    """Test project registry and management endpoints."""
    
    def test_register_project(self):
        """Test project registration."""
        response = client.post("/api/register_project", json={
            "project_id": "proj_mgmt_test",
            "project_data": {
                "name": "Project Management Test",
                "path": "D:/Projects/TestProject",
                "engine_version": "5.6"
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_list_projects(self):
        """Test listing all projects."""
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_set_active_project(self):
        """Test setting active project."""
        # Register project first
        client.post("/api/register_project", json={
            "project_id": "active_test",
            "project_data": {"name": "Active Test"}
        })
        
        response = client.post("/api/set_active_project", json={
            "project_id": "active_test"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_active_project(self):
        """Test getting active project."""
        response = client.get("/api/active_project")
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data or "error" in data


class TestCommandRoutingRoutes:
    """Test command routing and execution endpoints."""
    
    def test_send_command_to_ue5(self):
        """Test sending command to UE5 client."""
        response = client.post("/send_command_to_ue5", json={
            "project_id": "cmd_route_test",
            "command": {
                "type": "execute_action",
                "action": "describe_viewport"
            }
        })
        assert response.status_code == 200
    
    @patch('app.routes.call_openai_chat')
    def test_execute_command_with_ai(self, mock_openai):
        """Test AI-powered command execution."""
        mock_openai.return_value = "AI response"
        
        response = client.post("/execute_command", json={
            "query": "What is in the viewport?"
        })
        assert response.status_code == 200


class TestAIIntegrationRoutes:
    """Test AI integration endpoints."""
    
    @patch('app.routes.call_openai_chat')
    def test_describe_viewport(self, mock_openai):
        """Test viewport description endpoint."""
        mock_openai.return_value = "The viewport shows..."
        
        response = client.post("/describe_viewport", json={
            "viewport_data": {
                "actors": [],
                "camera": {}
            }
        })
        assert response.status_code == 200
    
    @patch('app.routes.call_openai_chat')
    def test_answer_with_context(self, mock_openai):
        """Test context-aware AI responses."""
        mock_openai.return_value = "Based on the context..."
        
        response = client.post("/answer_with_context", json={
            "query": "What should I do next?",
            "project_id": "ai_context_test"
        })
        assert response.status_code == 200


class TestUtilityGenerationRoutes:
    """Test Editor Utility Widget generation endpoints."""
    
    @patch('app.routes.call_openai_chat')
    def test_generate_utility(self, mock_openai):
        """Test utility widget generation."""
        mock_openai.return_value = """
        ```python
        import unreal
        
        class GeneratedWidget:
            pass
        ```
        """
        
        response = client.post("/api/generate_utility", json={
            "widget_name": "TestUtility",
            "description": "Test description",
            "project_id": "util_gen_test"
        })
        assert response.status_code == 200
    
    @patch('app.routes.call_openai_chat')
    def test_generate_action_plan(self, mock_openai):
        """Test action plan generation."""
        mock_openai.return_value = "1. Step one\n2. Step two"
        
        response = client.post("/api/generate_action_plan", json={
            "goal": "Test goal",
            "context": "Test context"
        })
        assert response.status_code == 200


class TestAutoUpdateRoutes:
    """Test auto-update system endpoints."""
    
    def test_trigger_auto_update(self):
        """Test triggering auto-update."""
        response = client.post("/api/trigger_auto_update", json={
            "project_id": "update_trigger_test"
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "queued" in data or "message" in data
    
    def test_download_client_package(self):
        """Test downloading client package."""
        response = client.get("/api/download_client")
        assert response.status_code == 200
        
        # Should return ZIP or TAR.GZ
        content_type = response.headers.get("content-type", "")
        assert "application" in content_type or "octet-stream" in content_type


class TestConfigurationRoutes:
    """Test configuration and settings endpoints."""
    
    def test_get_config(self):
        """Test getting current configuration."""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_update_config(self):
        """Test updating configuration."""
        response = client.post("/api/config", json={
            "test_key": "test_value"
        })
        assert response.status_code == 200


class TestDiagnosticsRoutes:
    """Test diagnostics and troubleshooting endpoints."""
    
    def test_get_events(self):
        """Test getting event history."""
        response = client.get("/api/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_operations(self):
        """Test getting operation history."""
        response = client.get("/api/operations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_server_switch(self):
        """Test server switch command."""
        response = client.post("/api/server_switch", json={
            "project_id": "switch_route_test",
            "server_url": "http://test.com"
        })
        assert response.status_code == 200
    
    def test_reconnect(self):
        """Test reconnect command."""
        response = client.post("/api/reconnect", json={
            "project_id": "reconnect_route_test"
        })
        assert response.status_code == 200


class TestStaticFileRoutes:
    """Test static file serving routes."""
    
    def test_dashboard_page(self):
        """Test dashboard page loads."""
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "html" in response.headers.get("content-type", "").lower()
    
    def test_root_redirect(self):
        """Test root redirects to dashboard."""
        response = client.get("/", follow_redirects=False)
        # Should redirect or serve dashboard
        assert response.status_code in [200, 301, 302, 303, 307, 308]


class TestErrorHandling:
    """Test error handling across all routes."""
    
    def test_invalid_project_id(self):
        """Test handling of invalid project IDs."""
        response = client.post("/send_command_to_ue5", json={
            "project_id": "nonexistent_project_12345",
            "command": {"type": "test"}
        })
        # Should return error gracefully
        assert response.status_code in [200, 404, 400]
    
    def test_malformed_request(self):
        """Test handling of malformed requests."""
        response = client.post("/api/ue5/register_http", json={
            "invalid_field": "value"
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "error" in data
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        response = client.post("/api/generate_utility", json={})
        # Should return error about missing fields
        assert response.status_code in [200, 400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
