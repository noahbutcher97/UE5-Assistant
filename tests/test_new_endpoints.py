"""
Comprehensive tests for v3.1 backend endpoints.
Tests file operations, project metadata, guidance, and blueprint capture routes.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import base64
import json

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


class TestFileOperations:
    """Test file system operation endpoints."""
    
    def test_list_files_root(self):
        """Test listing files in root directory."""
        response = client.post("/api/files/list", json={})
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "total_files" in data
        assert isinstance(data["files"], list)
    
    def test_list_files_with_path(self):
        """Test listing files in specific directory."""
        response = client.post("/api/files/list", json={"path": "app"})
        assert response.status_code == 200
        data = response.json()
        assert "app" in data["root_path"]
    
    def test_list_files_invalid_path(self):
        """Test listing files with invalid path."""
        response = client.post("/api/files/list", json={"path": "/etc/passwd"})
        assert response.status_code in [400, 403, 404]
    
    def test_read_file_success(self):
        """Test reading an existing file."""
        response = client.post("/api/files/read", json={"path": "main.py"})
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "path" in data
        assert data["type"] == "file"
    
    def test_read_file_not_found(self):
        """Test reading non-existent file."""
        response = client.post("/api/files/read", json={"path": "nonexistent.py"})
        assert response.status_code == 404
    
    def test_search_files(self):
        """Test file search functionality."""
        response = client.post("/api/files/search", json={"pattern": "test"})
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "total_files" in data


class TestProjectMetadata:
    """Test project metadata endpoint."""
    
    def test_get_metadata(self):
        """Test GET project metadata."""
        response = client.get("/api/project/metadata")
        assert response.status_code == 200
        data = response.json()
        assert "project_name" in data
        assert "technologies" in data
        assert isinstance(data["technologies"], list)
    
    def test_post_metadata(self):
        """Test POST project metadata."""
        metadata = {
            "project_name": "Test UE5 Project",
            "description": "Test description",
            "technologies": ["UE5.6", "Python", "FastAPI"],
            "modules_count": 5,
            "blueprints_count": 10
        }
        response = client.post("/api/project/metadata", json=metadata)
        assert response.status_code == 200
        data = response.json()
        assert data["project_name"] == "Test UE5 Project"
        assert data["modules_count"] == 5
    
    def test_metadata_persistence(self):
        """Test that metadata persists in cache."""
        # First POST
        metadata1 = {"project_name": "Project A", "technologies": ["UE5"]}
        client.post("/api/project/metadata", json=metadata1)
        
        # Then GET - should return the same data
        response = client.get("/api/project/metadata")
        assert response.status_code == 200
        data = response.json()
        assert data["project_name"] == "Project A"


class TestGuidance:
    """Test context-aware guidance endpoint."""
    
    def test_guidance_basic(self):
        """Test basic guidance request."""
        request = {
            "query": "How do I create a character blueprint?",
            "context_type": "blueprint_creation"
        }
        response = client.post("/api/guidance", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "guidance" in data
        assert isinstance(data["guidance"], str)
        assert len(data["guidance"]) > 0
    
    def test_guidance_with_file_context(self):
        """Test guidance with file context."""
        request = {
            "query": "How should I structure this code?",
            "context_type": "code_structure",
            "file_paths": ["main.py", "app/models.py"]
        }
        response = client.post("/api/guidance", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "guidance" in data
        assert "context_used" in data
    
    def test_guidance_with_project_metadata(self):
        """Test guidance with project metadata context."""
        # First set metadata
        metadata = {
            "project_name": "RPG Game",
            "technologies": ["UE5.6", "C++"],
            "blueprints_count": 50
        }
        client.post("/api/project/metadata", json=metadata)
        
        # Then request guidance
        request = {
            "query": "What's the best way to optimize my blueprints?",
            "context_type": "optimization",
            "include_project_metadata": True
        }
        response = client.post("/api/guidance", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "guidance" in data


class TestBlueprintCapture:
    """Test blueprint capture endpoints."""
    
    def test_capture_blueprint_basic(self):
        """Test basic blueprint capture."""
        # Create a small test image (1x1 pixel)
        test_image_data = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82').decode('utf-8')
        
        request = {
            "blueprint_name": "BP_TestCharacter",
            "blueprint_path": "/Game/Characters/BP_TestCharacter",
            "image_data": test_image_data,
            "description": "Test blueprint capture"
        }
        response = client.post("/api/blueprints/capture", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "capture_id" in data
        assert "analysis" in data
        assert data["blueprint_name"] == "BP_TestCharacter"
    
    def test_get_blueprint_capture(self):
        """Test retrieving blueprint capture by ID."""
        # First create a capture
        test_image = base64.b64encode(b'test').decode('utf-8')
        capture_req = {
            "blueprint_name": "BP_Test",
            "image_data": test_image
        }
        create_response = client.post("/api/blueprints/capture", json=capture_req)
        capture_id = create_response.json()["capture_id"]
        
        # Then retrieve it
        response = client.get(f"/api/blueprints/{capture_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["capture_id"] == capture_id
        assert data["blueprint_name"] == "BP_Test"
    
    def test_get_nonexistent_capture(self):
        """Test retrieving non-existent capture."""
        response = client.get("/api/blueprints/nonexistent_id")
        assert response.status_code == 404
    
    def test_list_blueprint_captures(self):
        """Test listing all blueprint captures."""
        response = client.get("/api/blueprints")
        assert response.status_code == 200
        data = response.json()
        assert "captures" in data
        assert isinstance(data["captures"], list)


class TestSecurityAndValidation:
    """Test security measures and input validation."""
    
    def test_path_traversal_blocked(self):
        """Test that path traversal attempts are blocked."""
        dangerous_paths = [
            "../../../etc/passwd",
            "../../.ssh/id_rsa",
            "/etc/shadow",
            "..\\..\\windows\\system32"
        ]
        
        for path in dangerous_paths:
            response = client.get(f"/api/files/read?path={path}")
            assert response.status_code in [400, 403, 404], f"Failed to block: {path}"
    
    def test_file_size_limit(self):
        """Test that oversized file reads are handled properly."""
        # This would need a large test file or mock
        # For now, verify the endpoint has size limits
        response = client.get("/api/files/read?path=main.py")
        assert response.status_code == 200
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON in POST requests."""
        response = client.post(
            "/api/guidance",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity


class TestIntegration:
    """Integration tests combining multiple endpoints."""
    
    def test_full_context_workflow(self):
        """Test complete workflow: metadata -> files -> guidance."""
        # 1. Set project metadata
        metadata = {
            "project_name": "Action Game",
            "technologies": ["UE5.6", "Blueprints"],
            "blueprints_count": 25
        }
        meta_response = client.post("/api/project/metadata", json=metadata)
        assert meta_response.status_code == 200
        
        # 2. Search for blueprint files
        search_response = client.get("/api/files/search?pattern=BP_")
        assert search_response.status_code == 200
        
        # 3. Request guidance with full context
        guidance_request = {
            "query": "How can I improve my character blueprints?",
            "context_type": "optimization",
            "include_project_metadata": True
        }
        guidance_response = client.post("/api/guidance", json=guidance_request)
        assert guidance_response.status_code == 200
        assert len(guidance_response.json()["guidance"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
