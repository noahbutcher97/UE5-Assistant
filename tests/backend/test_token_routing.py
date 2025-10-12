"""
Test UE_REQUEST token routing and context collection flow.

This validates the complete workflow:
1. User asks question on dashboard
2. AI interprets and returns UE_REQUEST token
3. Backend routes token to UE5 for context collection  
4. UE5 collects editor context (viewport/blueprints/project info)
5. Context is passed to AI via /answer_with_context
6. AI generates natural language response
7. Response is displayed on dashboard
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

from main import app
from tests.fixtures.mock_viewport_data import (
    get_mock_viewport_context,
    get_mock_blueprint_list,
    get_mock_project_profile,
    get_mock_file_context
)

client = TestClient(app)


class TestTokenRouting:
    """Test UE_REQUEST token routing and interpretation."""
    
    def test_viewport_token_routing(self):
        """Test: User asks 'describe viewport' → [UE_REQUEST] describe_viewport token."""
        
        # Step 1: User asks about viewport
        query = "Describe my viewport"
        
        # Step 2: Execute command (AI should return UE_REQUEST token)
        response = client.post("/execute_command", json={"prompt": query})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a UE_REQUEST token for viewport data
        assert "[UE_REQUEST]" in data.get("response", "")
        assert "describe_viewport" in data.get("response", "").lower()
        
        print(f"✅ Token Generated: {data['response']}")
        return data["response"]
    
    def test_blueprint_token_routing(self):
        """Test: User asks 'list blueprints' -> [UE_REQUEST] list_blueprints or [UE_CONTEXT_REQUEST] with blueprints."""
        
        query = "List all blueprints in my project"
        
        response = client.post("/execute_command", json={"prompt": query})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a UE token for blueprint listing
        response_text = data.get("response", "")
        assert any(token in response_text for token in ["[UE_REQUEST]", "[UE_CONTEXT_REQUEST]"]), \
            f"Expected UE token but got: {response_text}"
        
        # Verify it references blueprints or the command to list them
        assert any(cmd in response_text.lower() for cmd in ["list_blueprints", "blueprint", "project_info"]), \
            f"Token should reference blueprint listing but got: {response_text}"
        
        print(f"✅ Token Generated: {data['response']}")
        return data["response"]
    
    def test_project_info_token_routing(self):
        """Test: User asks 'what project am I in' -> [UE_REQUEST] get_project_info or [UE_CONTEXT_REQUEST] project_info."""
        
        query = "What project am I working on?"
        
        response = client.post("/execute_command", json={"prompt": query})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return UE token for project info
        response_text = data.get("response", "")
        assert "[UE_REQUEST]" in response_text or "[UE_CONTEXT_REQUEST]" in response_text, \
            f"Expected UE token but got: {response_text}"
        
        # Verify it references project info
        assert any(cmd in response_text.lower() for cmd in ["project_info", "get_project"]), \
            f"Token should reference project info but got: {response_text}"
        
        print(f"✅ Token Generated: {data['response']}")
        return data["response"]
    
    def test_browse_files_token_routing(self):
        """Test browse files token routing."""
        
        query = "Show me all files in my project"
        
        response = client.post("/execute_command", json={"prompt": query})
        
        assert response.status_code == 200
        data = response.json()
        
        response_text = data.get("response", "")
        assert any(token in response_text for token in ["[UE_REQUEST]", "[UE_CONTEXT_REQUEST]"])
        assert any(cmd in response_text.lower() for cmd in ["browse_files", "files", "project_info"])
        
        print(f"Token Generated: {data['response']}")
        return data["response"]


class TestContextCollection:
    """Test that tokens trigger proper context collection (simulated)."""
    
    def test_viewport_context_collection(self):
        """
        Simulate: [UE_REQUEST] describe_viewport → UE5 collects viewport context.
        
        In real flow:
        1. Token sent to UE5
        2. UE5 collects camera, actors, lighting, environment
        3. UE5 sends context back to backend
        """
        
        # This simulates what UE5 would send back after receiving the token
        viewport_context = get_mock_viewport_context()
        
        # Verify context has all required fields
        assert "camera" in viewport_context
        assert "actors" in viewport_context
        assert "lighting" in viewport_context
        assert "environment" in viewport_context
        
        # Verify camera data structure
        camera = viewport_context["camera"]
        assert "location" in camera or "position" in camera  # Can be either
        assert "rotation" in camera
        assert "fov" in camera
        
        # Verify actors are collected (can be list or dict)
        actors = viewport_context["actors"]
        if isinstance(actors, list):
            assert len(actors) > 0
            first_actor = actors[0]
            assert "name" in first_actor
            assert "location" in first_actor
        elif isinstance(actors, dict):
            # Dict format with level, names, total, types
            assert "level" in actors or "names" in actors or "total" in actors
        else:
            raise AssertionError(f"Unexpected actors format: {type(actors)}")
        
        print(f"✅ Viewport Context: {len(actors)} actors, {len(viewport_context['lighting'])} lights")
        return viewport_context
    
    def test_blueprint_context_collection(self):
        """
        Simulate: [UE_REQUEST] list_blueprints → UE5 collects blueprint list.
        """
        
        blueprint_list = get_mock_blueprint_list()
        
        # Verify blueprint data structure
        assert len(blueprint_list) > 0
        
        for bp in blueprint_list:
            assert "name" in bp, f"Blueprint missing 'name': {bp}"
            assert "path" in bp, f"Blueprint missing 'path': {bp}"
            assert "class" in bp or "type" in bp, f"Blueprint missing 'class' or 'type': {bp}"
        
        print(f"✅ Blueprint Context: {len(blueprint_list)} blueprints collected")
        return blueprint_list
    
    def test_project_info_context_collection(self):
        """
        Simulate: [UE_REQUEST] get_project_info → UE5 collects project metadata.
        """
        
        project_info = get_mock_project_profile()
        
        # Verify project data structure
        assert "project_name" in project_info
        assert "engine_version" in project_info
        assert "modules" in project_info
        assert "plugins" in project_info
        
        print(f"✅ Project Context: {project_info['project_name']} (UE {project_info['engine_version']})")
        return project_info
    
    def test_file_context_collection(self):
        """
        Simulate: [UE_REQUEST] browse_files → UE5 collects file structure.
        """
        
        file_context = get_mock_file_context()
        
        # Verify file data structure
        assert "files" in file_context
        assert len(file_context["files"]) > 0
        
        for file in file_context["files"]:
            assert "path" in file, f"File missing 'path': {file}"
            assert "size" in file, f"File missing 'size': {file}"
            assert "type" in file, f"File missing 'type': {file}"
        
        print(f"✅ File Context: {len(file_context['files'])} files collected")
        return file_context


class TestAIContextProcessing:
    """Test that collected context is properly passed to AI for natural language generation."""
    
    def test_viewport_context_to_ai_response(self):
        """
        Test: Viewport context → AI → Natural language description.
        
        Flow:
        1. Context collected from UE5
        2. Passed to /answer_with_context
        3. AI generates natural language description
        """
        
        viewport_context = get_mock_viewport_context()
        
        # Send context to AI for processing
        request_data = {
            "question": "Describe what's in the viewport",
            "context": viewport_context,
            "context_type": "viewport"
        }
        
        response = client.post("/answer_with_context", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        ai_response = data["response"]
        
        # Verify AI generated a meaningful response
        assert len(ai_response) > 50
        
        # Should mention viewport elements
        assert any(word in ai_response.lower() for word in 
                  ["camera", "actor", "scene", "viewport", "position", "light"])
        
        print(f"✅ AI Response: {ai_response[:100]}...")
        return ai_response
    
    def test_blueprint_context_to_ai_response(self):
        """
        Test: Blueprint context → AI → Blueprint list description.
        """
        
        blueprint_context = {"blueprints": get_mock_blueprint_list()}
        
        request_data = {
            "question": "What blueprints are in the project?",
            "context": blueprint_context,
            "context_type": "blueprints"
        }
        
        response = client.post("/answer_with_context", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        ai_response = data["response"]
        
        # Verify AI listed blueprints
        assert len(ai_response) > 30
        assert any(word in ai_response.lower() for word in 
                  ["blueprint", "bp_", "player", "enemy", "gamemode"])
        
        print(f"✅ AI Response: {ai_response[:100]}...")
        return ai_response
    
    def test_project_info_context_to_ai_response(self):
        """
        Test: Project info context → AI → Project summary.
        """
        
        project_context = get_mock_project_profile()
        
        request_data = {
            "question": "Tell me about this project",
            "context": project_context,
            "context_type": "project_info"
        }
        
        response = client.post("/answer_with_context", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        ai_response = data["response"]
        
        # Verify AI summarized project
        assert len(ai_response) > 30
        assert any(word in ai_response.lower() for word in 
                  ["project", "testproject", "unreal", "engine", "5.6"])
        
        print(f"✅ AI Response: {ai_response[:100]}...")
        return ai_response
    
    def test_file_context_to_ai_response(self):
        """
        Test: File context → AI → File structure description.
        """
        
        file_context = get_mock_file_context()
        
        request_data = {
            "question": "What files are in the project?",
            "context": file_context,
            "context_type": "files"
        }
        
        response = client.post("/answer_with_context", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        ai_response = data["response"]
        
        # Verify AI described files
        assert len(ai_response) > 30
        assert any(word in ai_response.lower() for word in 
                  ["file", "asset", "blueprint", "texture", "material"])
        
        print(f"✅ AI Response: {ai_response[:100]}...")
        return ai_response


class TestEndToEndTokenFlow:
    """Test complete end-to-end token routing flow."""
    
    def test_complete_viewport_flow(self):
        """
        Complete flow: Question → Token → Context → AI → Response.
        
        Steps:
        1. User: "Describe my viewport"
        2. AI: "[UE_REQUEST] describe_viewport"
        3. UE5: Collects viewport context
        4. Backend: Passes context to AI
        5. AI: Generates natural language description
        6. Dashboard: Displays response
        """
        
        print("\n" + "="*70)
        print("COMPLETE VIEWPORT TOKEN FLOW TEST")
        print("="*70)
        
        # Step 1: User question
        print("\n[1] User asks: 'Describe my viewport'")
        question = "Describe my viewport"
        
        # Step 2: AI generates token
        print("[2] Executing command...")
        cmd_response = client.post("/execute_command", json={"prompt": question})
        token = cmd_response.json()["response"]
        print(f"    → Token: {token}")
        
        assert "[UE_REQUEST]" in token
        assert "describe_viewport" in token.lower()
        
        # Step 3: Simulate UE5 context collection
        print("[3] UE5 collects viewport context...")
        viewport_context = get_mock_viewport_context()
        print(f"    → Collected: {len(viewport_context['actors'])} actors, "
              f"{len(viewport_context['lighting'])} lights")
        
        # Step 4: Pass context to AI
        print("[4] Passing context to AI for natural language generation...")
        ai_request = {
            "question": "Describe what's in the viewport",
            "context": viewport_context,
            "context_type": "viewport"
        }
        
        ai_response = client.post("/answer_with_context", json=ai_request)
        final_response = ai_response.json()["response"]
        
        # Step 5: Verify final response
        print(f"[5] AI Response: {final_response[:150]}...")
        
        assert len(final_response) > 50
        assert any(word in final_response.lower() for word in 
                  ["camera", "viewport", "scene", "actor"])
        
        print("\n✅ COMPLETE FLOW SUCCESSFUL")
        print("="*70)
    
    def test_complete_blueprint_flow(self):
        """
        Complete flow: Blueprint query → Token → Context → AI → Response.
        """
        
        print("\n" + "="*70)
        print("COMPLETE BLUEPRINT TOKEN FLOW TEST")
        print("="*70)
        
        # Step 1: User question
        print("\n[1] User asks: 'List all blueprints'")
        question = "List all blueprints in my project"
        
        # Step 2: AI generates token
        print("[2] Executing command...")
        cmd_response = client.post("/execute_command", json={"prompt": question})
        token = cmd_response.json()["response"]
        print(f"    → Token: {token}")
        
        # Accept both UE_REQUEST and UE_CONTEXT_REQUEST tokens
        assert any(t in token for t in ["[UE_REQUEST]", "[UE_CONTEXT_REQUEST]"]), \
            f"Expected UE token but got: {token}"
        
        # Verify it's blueprint-related
        assert "blueprint" in token.lower() or "project_info" in token.lower(), \
            f"Token should reference blueprints or project_info: {token}"
        
        # Step 3: Simulate UE5 context collection
        print("[3] UE5 collects blueprint list...")
        blueprint_list = get_mock_blueprint_list()
        print(f"    → Collected: {len(blueprint_list)} blueprints")
        
        # Step 4: Pass context to AI
        print("[4] Passing context to AI...")
        ai_request = {
            "question": "List the blueprints",
            "context": {"blueprints": blueprint_list},
            "context_type": "blueprints"
        }
        
        ai_response = client.post("/answer_with_context", json=ai_request)
        final_response = ai_response.json()["response"]
        
        # Step 5: Verify final response
        print(f"[5] AI Response: {final_response[:150]}...")
        
        assert len(final_response) > 30
        assert "blueprint" in final_response.lower() or "bp_" in final_response.lower()
        
        print("\n✅ COMPLETE FLOW SUCCESSFUL")
        print("="*70)


class TestTokenInterpretation:
    """Test that various user questions are properly interpreted into tokens."""
    
    def test_viewport_question_variations(self):
        """Test different ways users might ask about viewport."""
        
        viewport_questions = [
            "describe my viewport",
            "what's in my scene",
            "what do I see",
            "describe the viewport",
            "what's in the scene"
        ]
        
        for question in viewport_questions:
            response = client.post("/execute_command", json={"prompt": question})
            token = response.json().get("response", "")
            
            assert "[UE_REQUEST]" in token, f"Failed for: {question}"
            assert "describe_viewport" in token.lower(), f"Wrong token for: {question}"
            
            print(f"✅ '{question}' → {token}")
    
    def test_blueprint_question_variations(self):
        """Test different ways users might ask about blueprints."""
        
        blueprint_questions = [
            "list all blueprints",
            "show me blueprints",
            "what blueprints are there",
            "list blueprints in project"
        ]
        
        for question in blueprint_questions:
            response = client.post("/execute_command", json={"prompt": question})
            token = response.json().get("response", "")
            
            assert "[UE_REQUEST]" in token, f"Failed for: {question}"
            
            print(f"✅ '{question}' → {token}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
