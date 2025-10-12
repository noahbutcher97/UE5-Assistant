"""
Comprehensive Backend API Tests for UE5 AI Assistant
Tests all API endpoints without requiring UE5 access.
"""
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main import app

client = TestClient(app)


class TestHTTPPollingEndpoints:
    """Test HTTP polling endpoints for UE5 client fallback."""
    
    def test_register_http_client(self):
        """Test UE5 client registration via HTTP polling."""
        response = client.post("/api/ue5/register_http", json={
            "project_id": "test_project_123",
            "project_name": "Test UE5 Project"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Registered via HTTP polling" in data["message"]
    
    def test_register_http_client_missing_project_id(self):
        """Test registration fails without project_id."""
        response = client.post("/api/ue5/register_http", json={
            "project_name": "Test Project"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "project_id required" in data["error"]
    
    def test_poll_for_commands_registered(self):
        """Test polling for commands after registration."""
        project_id = "test_poll_123"
        
        client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Poll Test"
        })
        
        response = client.post("/api/ue5/poll", json={
            "project_id": project_id
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "commands" in data
        assert data["registered"] is True
        assert isinstance(data["commands"], list)
    
    def test_poll_auto_registration(self):
        """Test that polling auto-registers unregistered clients."""
        response = client.post("/api/ue5/poll", json={
            "project_id": "auto_register_test",
            "project_name": "Auto Registered Project"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["registered"] is True
    
    def test_poll_missing_project_id(self):
        """Test polling without project_id returns not registered."""
        response = client.post("/api/ue5/poll", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert data["commands"] == []
        assert data["registered"] is False
    
    def test_heartbeat_registered_client(self):
        """Test heartbeat for registered client."""
        project_id = "heartbeat_test_123"
        
        client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Heartbeat Test"
        })
        
        response = client.post("/api/ue5/heartbeat", json={
            "project_id": project_id
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["status"] == "alive"
    
    def test_heartbeat_unregistered_client(self):
        """Test heartbeat for unregistered client fails."""
        response = client.post("/api/ue5/heartbeat", json={
            "project_id": "unregistered_client"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
    
    def test_ue5_response_submission(self):
        """Test UE5 client submitting action response."""
        project_id = "response_test_123"
        
        client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Response Test"
        })
        
        response = client.post("/api/ue5/response", json={
            "project_id": project_id,
            "response": {
                "request_id": "req_12345",
                "success": True,
                "data": "Action completed successfully"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestCommandRoutingEndpoints:
    """Test command routing between dashboard and UE5."""
    
    @pytest.mark.asyncio
    async def test_send_command_to_ue5_not_connected(self):
        """Test sending command to non-connected UE5 client."""
        response = client.post("/send_command_to_ue5", json={
            "project_id": "nonexistent_project",
            "command": {
                "type": "execute_action",
                "action": "describe_viewport"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not connected" in data["error"].lower()
    
    def test_send_command_missing_data(self):
        """Test sending command with missing required fields."""
        response = client.post("/send_command_to_ue5", json={
            "project_id": "test_project"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "command" in data["error"].lower()


class TestAutoUpdateEndpoint:
    """Test auto-update trigger endpoint."""
    
    @pytest.mark.asyncio
    async def test_trigger_auto_update(self):
        """Test auto-update trigger endpoint."""
        response = client.post("/api/trigger_auto_update")
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "clients_notified" in data


class TestProjectRegistrationEndpoints:
    """Test project registration and management."""
    
    def test_register_project(self):
        """Test registering a new project (UE5 client format)."""
        response = client.post("/api/register_project", json={
            "project_id": "test_project_456",
            "project_data": {
                "name": "My UE5 Project",
                "path": "D:/Projects/MyGame",
                "version": "5.6",
                "metadata": {
                    "blueprints_count": 10,
                    "modules_count": 3
                }
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project_id"] == "test_project_456"
    
    def test_list_projects(self):
        """Test listing all registered projects."""
        response = client.get("/api/projects")
        
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)
    
    def test_get_active_project(self):
        """Test getting the active project."""
        response = client.get("/api/active_project")
        
        assert response.status_code == 200
        data = response.json()
        assert "project" in data or data.get("project") is None
    
    def test_set_active_project(self):
        """Test setting active project."""
        project_id = "test_active_456"
        
        # Register with UE5 client format
        client.post("/api/register_project", json={
            "project_id": project_id,
            "project_data": {
                "name": "Active Test Project",
                "path": "/path/to/project"
            }
        })
        
        response = client.post("/api/set_active_project", json={
            "project_id": project_id
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_set_active_nonexistent_project(self):
        """Test setting non-existent project as active fails."""
        response = client.post("/api/set_active_project", json={
            "project_id": "nonexistent_project_999"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["error"].lower()


class TestExecuteCommandEndpoint:
    """Test the /execute_command endpoint."""
    
    @patch('app.services.openai_client.openai.chat.completions.create')
    def test_execute_command_basic(self, mock_openai):
        """Test basic command execution without UE requests."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a basic response from the AI."
        mock_openai.return_value = mock_response
        
        response = client.post("/execute_command", json={
            "user_message": "Hello, can you help me with Unreal Engine?"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
    
    @patch('app.services.openai_client.openai.chat.completions.create')
    def test_execute_command_with_ue_request_token(self, mock_openai):
        """Test command execution with [UE_REQUEST] token."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "[UE_REQUEST] describe_viewport"
        mock_openai.return_value = mock_response
        
        response = client.post("/execute_command", json={
            "user_message": "Describe my viewport"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data


class TestDescribeViewportEndpoint:
    """Test viewport description endpoint."""
    
    @patch('app.services.openai_client.openai.chat.completions.create')
    def test_describe_viewport_success(self, mock_openai):
        """Test successful viewport description."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "The viewport shows a 3D scene with a character standing on terrain."
        mock_openai.return_value = mock_response
        
        response = client.post("/describe_viewport", json={
            "actors": [
                {
                    "name": "BP_Player",
                    "class": "ThirdPersonCharacter",
                    "location": [0, 0, 100]
                }
            ],
            "camera": {
                "location": [0, -500, 200],
                "rotation": [0, 0, 0]
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "description" in data
        assert isinstance(data["description"], str)
    
    @patch('app.services.openai_client.openai.chat.completions.create')
    def test_describe_viewport_with_filtering(self, mock_openai):
        """Test viewport description with data filtering."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Clean filtered description."
        mock_openai.return_value = mock_response
        
        response = client.post("/describe_viewport", json={
            "actors": [
                {
                    "name": "SM_MERGED_Actor",
                    "class": "StaticMeshActor",
                    "location": [0, 0, 0]
                },
                {
                    "name": "BP_GameMode",
                    "class": "GameModeBase",
                    "location": [0, 0, 0]
                }
            ]
        })
        
        assert response.status_code == 200


class TestAnswerWithContextEndpoint:
    """Test context-aware answer endpoint."""
    
    @patch('app.services.openai_client.openai.chat.completions.create')
    def test_answer_with_context(self, mock_openai):
        """Test answering with project context."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Based on your project context, I recommend..."
        mock_openai.return_value = mock_response
        
        response = client.post("/answer_with_context", json={
            "question": "How should I optimize my blueprints?",
            "context": {
                "project_name": "ActionGame",
                "blueprints_count": 50,
                "technologies": ["UE5.6", "Blueprints"]
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)


class TestErrorHandling:
    """Test error handling across endpoints."""
    
    def test_invalid_json_payload(self):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/ue5/register_http",
            content=b"invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        response = client.post("/api/project/register", json={
            "name": "Incomplete Project"
        })
        
        assert response.status_code in [400, 422]
    
    @patch('app.services.openai_client.openai.chat.completions.create')
    def test_openai_api_failure(self, mock_openai):
        """Test handling of OpenAI API failures."""
        mock_openai.side_effect = Exception("API Error")
        
        response = client.post("/describe_viewport", json={
            "actors": []
        })
        
        assert response.status_code in [200, 500]


class TestDataPersistence:
    """Test data persistence and state management."""
    
    def test_conversation_history_persistence(self):
        """Test that conversation history persists."""
        response1 = client.get("/api/conversations")
        assert response1.status_code == 200
        
        initial_count = len(response1.json().get("conversations", []))
        
        response2 = client.get("/api/conversations")
        assert response2.status_code == 200
        
        current_count = len(response2.json().get("conversations", []))
        assert current_count >= initial_count
    
    def test_project_registry_persistence(self):
        """Test project registry persists between requests."""
        project_id = "persist_test_789"
        
        client.post("/api/project/register", json={
            "project_id": project_id,
            "name": "Persistent Project",
            "path": "/path"
        })
        
        response = client.get("/api/project/list")
        projects = response.json()["projects"]
        
        project_ids = [p["project_id"] for p in projects]
        assert project_id in project_ids


class TestConfigurationEndpoints:
    """Test configuration management endpoints."""
    
    def test_get_config(self):
        """Test getting current configuration."""
        response = client.get("/api/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "model" in data
        assert "response_style" in data
    
    def test_update_config(self):
        """Test updating configuration."""
        response = client.post("/api/config", json={
            "response_style": "concise"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("response_style") == "concise"


class TestUtilityGeneration:
    """Test editor utility widget generation."""
    
    def test_generate_utility_widget(self):
        """Test generating UE 5.6 utility widget."""
        response = client.post("/api/generate_utility", json={
            "name": "TestUtility",
            "description": "Test utility widget",
            "capabilities": ["spawn_actors", "query_project"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "script_content" in data
        assert "TestUtility" in data["script_content"]
    
    def test_generate_action_plan(self):
        """Test AI action plan generation."""
        with patch('openai.chat.completions.create') as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '[{"type": "spawn", "location": [0,0,0]}]'
            mock_openai.return_value = mock_response
            
            response = client.post("/api/generate_action_plan", json={
                "description": "Create a simple room with a chair"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "plan" in data or "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
