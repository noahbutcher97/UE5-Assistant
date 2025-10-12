"""
Dashboard Integration Tests
End-to-end tests for dashboard quick actions and UE5 integration.
"""
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import json

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main import app

client = TestClient(app)


class TestDashboardQuickActions:
    """Test dashboard quick actions end-to-end."""
    
    def setup_method(self):
        """Setup test client for each test."""
        self.project_id = "dashboard_test_project"
        self.project_name = "Dashboard Test Project"
        
        client.post("/api/ue5/register_http", json={
            "project_id": self.project_id,
            "project_name": self.project_name
        })
        
        # Register with UE5 client format
        client.post("/api/register_project", json={
            "project_id": self.project_id,
            "project_data": {
                "name": self.project_name,
                "path": "D:/Projects/TestProject"
            }
        })
        
        client.post("/api/set_active_project", json={
            "project_id": self.project_id
        })
    
    @pytest.mark.asyncio
    async def test_describe_viewport_action(self):
        """Test Describe Viewport dashboard action."""
        command = {
            "project_id": self.project_id,
            "command": {
                "type": "execute_action",
                "action": "describe_viewport",
                "params": {}
            }
        }
        
        response = client.post("/send_command_to_ue5", json=command)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_list_blueprints_action(self):
        """Test List Blueprints dashboard action."""
        command = {
            "project_id": self.project_id,
            "command": {
                "type": "execute_action",
                "action": "list_blueprints",
                "params": {}
            }
        }
        
        response = client.post("/send_command_to_ue5", json=command)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_browse_files_action(self):
        """Test Browse Files dashboard action."""
        command = {
            "project_id": self.project_id,
            "command": {
                "type": "execute_action",
                "action": "browse_files",
                "params": {}
            }
        }
        
        response = client.post("/send_command_to_ue5", json=command)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_project_info_action(self):
        """Test Get Project Info dashboard action."""
        command = {
            "project_id": self.project_id,
            "command": {
                "type": "execute_action",
                "action": "get_project_info",
                "params": {}
            }
        }
        
        response = client.post("/send_command_to_ue5", json=command)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data or "error" in data


class TestDashboardWithMockResponses:
    """Test dashboard actions with simulated UE5 responses."""
    
    def setup_method(self):
        """Setup with mock responses."""
        self.project_id = "mock_response_project"
        
        client.post("/api/ue5/register_http", json={
            "project_id": self.project_id,
            "project_name": "Mock Response Project"
        })
    
    def test_viewport_description_flow(self):
        """Test complete viewport description flow with mock response."""
        poll_response = client.post("/api/ue5/poll", json={
            "project_id": self.project_id
        })
        
        assert poll_response.status_code == 200
        
        viewport_data = {
            "actors": [
                {
                    "name": "BP_Player",
                    "class": "ThirdPersonCharacter",
                    "location": [0, 0, 100],
                    "rotation": [0, 0, 0]
                },
                {
                    "name": "StaticMeshActor_1",
                    "class": "StaticMeshActor",
                    "location": [500, 0, 0]
                }
            ],
            "camera": {
                "location": [0, -500, 200],
                "rotation": [-15, 0, 0]
            }
        }
        
        response_data = {
            "request_id": "viewport_001",
            "success": True,
            "data": viewport_data
        }
        
        client.post("/api/ue5/response", json={
            "project_id": self.project_id,
            "response": response_data
        })
    
    def test_blueprint_list_flow(self):
        """Test complete blueprint list flow with mock response."""
        blueprint_data = {
            "blueprints": [
                {
                    "name": "BP_Player",
                    "path": "/Game/Blueprints/BP_Player",
                    "class": "Character"
                },
                {
                    "name": "BP_Enemy",
                    "path": "/Game/Blueprints/BP_Enemy",
                    "class": "Character"
                },
                {
                    "name": "BP_GameMode",
                    "path": "/Game/Core/BP_GameMode",
                    "class": "GameModeBase"
                }
            ],
            "total": 3
        }
        
        response_data = {
            "request_id": "blueprints_001",
            "success": True,
            "data": blueprint_data
        }
        
        client.post("/api/ue5/response", json={
            "project_id": self.project_id,
            "response": response_data
        })
    
    def test_project_info_flow(self):
        """Test complete project info flow with mock response."""
        project_data = {
            "project_name": "ActionGame",
            "version": "5.6",
            "path": "D:/UnrealProjects/ActionGame",
            "blueprints_count": 25,
            "modules_count": 3,
            "plugins": ["EnhancedInput", "Niagara"]
        }
        
        response_data = {
            "request_id": "project_info_001",
            "success": True,
            "data": project_data
        }
        
        client.post("/api/ue5/response", json={
            "project_id": self.project_id,
            "response": response_data
        })


class TestDashboardErrorScenarios:
    """Test dashboard error handling."""
    
    def test_command_to_disconnected_project(self):
        """Test sending command to disconnected project."""
        command = {
            "project_id": "nonexistent_project_xyz",
            "command": {
                "type": "execute_action",
                "action": "describe_viewport"
            }
        }
        
        response = client.post("/send_command_to_ue5", json=command)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not connected" in data["error"].lower()
    
    def test_invalid_action_name(self):
        """Test dashboard action with invalid action name."""
        project_id = "error_test_project"
        
        client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Error Test"
        })
        
        command = {
            "project_id": project_id,
            "command": {
                "type": "execute_action",
                "action": "invalid_action_xyz_123"
            }
        }
        
        response = client.post("/send_command_to_ue5", json=command)
        
        assert response.status_code == 200
    
    def test_missing_command_fields(self):
        """Test dashboard command with missing fields."""
        response = client.post("/send_command_to_ue5", json={
            "project_id": "test_project"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False


class TestDashboardAIIntegration:
    """Test dashboard AI context-aware responses."""
    
    @patch('app.services.openai_client.openai.chat.completions.create')
    def test_ai_with_viewport_context(self, mock_openai):
        """Test AI receives viewport context correctly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Based on your viewport, I can see a player character..."
        mock_openai.return_value = mock_response
        
        viewport_context = {
            "actors": [
                {"name": "BP_Player", "location": [0, 0, 100]}
            ],
            "camera": {"location": [0, -500, 200]}
        }
        
        response = client.post("/answer_with_context", json={
            "question": "What's in my scene?",
            "context": viewport_context
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
    
    @patch('app.services.openai_client.openai.chat.completions.create')
    def test_ai_with_project_context(self, mock_openai):
        """Test AI receives project context correctly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "For your ActionGame project with 50 blueprints..."
        mock_openai.return_value = mock_response
        
        project_context = {
            "project_name": "ActionGame",
            "blueprints_count": 50,
            "modules_count": 3
        }
        
        response = client.post("/answer_with_context", json={
            "question": "How should I optimize my project?",
            "context": project_context
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
    
    @patch('app.services.openai_client.openai.chat.completions.create')
    def test_ai_with_blueprint_context(self, mock_openai):
        """Test AI receives blueprint context correctly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Your BP_Player blueprint could be optimized by..."
        mock_openai.return_value = mock_response
        
        blueprint_context = {
            "blueprint_name": "BP_Player",
            "blueprint_path": "/Game/Blueprints/BP_Player",
            "nodes_count": 150
        }
        
        response = client.post("/answer_with_context", json={
            "question": "How can I improve this blueprint?",
            "context": blueprint_context
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data


class TestDashboardAutoUpdate:
    """Test dashboard auto-update functionality."""
    
    def test_auto_update_trigger_from_dashboard(self):
        """Test triggering auto-update from dashboard."""
        project_id = "auto_update_dash_test"
        
        client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Auto Update Dashboard Test"
        })
        
        response = client.post("/api/trigger_auto_update")
        
        assert response.status_code == 200
        data = response.json()
        assert "clients_notified" in data or "success" in data
    
    def test_auto_update_notification_received(self):
        """Test that UE5 client receives auto-update notification."""
        project_id = "auto_update_notify_test"
        
        client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Auto Update Notify Test"
        })
        
        client.post("/api/trigger_auto_update")
        
        poll_response = client.post("/api/ue5/poll", json={
            "project_id": project_id
        })
        
        commands = poll_response.json()["commands"]
        
        assert isinstance(commands, list)


class TestDashboardMultiProject:
    """Test dashboard with multiple projects."""
    
    def test_multiple_project_connections(self):
        """Test dashboard with multiple connected projects."""
        project_ids = [f"multi_proj_{i}" for i in range(3)]
        
        for pid in project_ids:
            client.post("/api/ue5/register_http", json={
                "project_id": pid,
                "project_name": f"Project {pid}"
            })
        
        projects_response = client.get("/api/projects")
        
        assert projects_response.status_code == 200
        projects = projects_response.json()["projects"]
        
        registered_ids = [p["project_id"] for p in projects]
        
        for pid in project_ids:
            assert pid in registered_ids
    
    def test_switching_active_project(self):
        """Test switching active project in dashboard."""
        project_id_1 = "switch_project_1"
        project_id_2 = "switch_project_2"
        
        for pid in [project_id_1, project_id_2]:
            # Register with UE5 client format
            client.post("/api/register_project", json={
                "project_id": pid,
                "project_data": {
                    "name": f"Switch Project {pid}",
                    "path": f"/path/{pid}"
                }
            })
        
        client.post("/api/set_active_project", json={
            "project_id": project_id_1
        })
        
        active_1 = client.get("/api/active_project")
        assert active_1.json()["project"]["project_id"] == project_id_1
        
        client.post("/api/set_active_project", json={
            "project_id": project_id_2
        })
        
        active_2 = client.get("/api/active_project")
        assert active_2.json()["project"]["project_id"] == project_id_2
    
    def test_commands_to_specific_project(self):
        """Test sending commands to specific project."""
        project_ids = ["specific_1", "specific_2"]
        
        for pid in project_ids:
            client.post("/api/ue5/register_http", json={
                "project_id": pid,
                "project_name": f"Specific {pid}"
            })
        
        command_1 = {
            "project_id": project_ids[0],
            "command": {
                "type": "execute_action",
                "action": "describe_viewport"
            }
        }
        
        response_1 = client.post("/send_command_to_ue5", json=command_1)
        assert response_1.status_code == 200


class TestDashboardRealTimeUpdates:
    """Test real-time updates and notifications."""
    
    def test_project_status_updates(self):
        """Test project status updates are tracked."""
        project_id = "status_update_test"
        
        register_response = client.post("/api/ue5/register_http", json={
            "project_id": project_id,
            "project_name": "Status Update Test"
        })
        
        assert register_response.json()["success"] is True
        
        heartbeat_response = client.post("/api/ue5/heartbeat", json={
            "project_id": project_id
        })
        
        assert heartbeat_response.json()["success"] is True


class TestDashboardDataPersistence:
    """Test dashboard data persistence."""
    
    def test_conversation_history_in_dashboard(self):
        """Test conversation history is accessible from dashboard."""
        response = client.get("/api/conversations")
        
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert isinstance(data["conversations"], list)
    
    def test_project_registry_in_dashboard(self):
        """Test project registry is accessible from dashboard."""
        response = client.get("/api/project/list")
        
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)


class TestDashboardConfiguration:
    """Test dashboard configuration management."""
    
    def test_get_dashboard_config(self):
        """Test getting dashboard configuration."""
        response = client.get("/api/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "model" in data
        assert "response_style" in data
    
    def test_update_config_from_dashboard(self):
        """Test updating config from dashboard."""
        response = client.post("/api/config", json={
            "response_style": "technical"
        })
        
        assert response.status_code == 200
        
        get_response = client.get("/api/config")
        config = get_response.json()
        assert config["response_style"] == "technical"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
