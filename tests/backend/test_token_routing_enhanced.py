"""
Enhanced Token Routing Tests
=============================
Validates complete end-to-end flow with actual JSON structures and UE5 callback simulation.

Test Coverage:
1. JSON payload validation for /execute_command responses
2. Token structure validation against UE5 client contract
3. UE5 callback simulation (context collection → /answer_with_context)
4. Context-aware AI response validation
5. Complete round-trip integration tests
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from tests.fixtures.mock_viewport_data import get_mock_viewport_context

client = TestClient(app)


class TestExecuteCommandJSONValidation:
    """Validate exact JSON response structure from /execute_command."""
    
    def test_viewport_token_json_structure(self):
        """Validate /execute_command returns correct JSON structure for viewport query."""
        response = client.post("/execute_command", json={"prompt": "What do I see in the viewport?"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate required fields
        assert "success" in data, "Response must have 'success' field"
        assert "response" in data, "Response must have 'response' field"
        assert data["success"] is True, "Success should be True"
        
        # Validate token format
        token = data["response"]
        assert token == "[UE_REQUEST] describe_viewport", \
            f"Expected exact token '[UE_REQUEST] describe_viewport' but got '{token}'"
        
        print(f"✅ JSON Structure Valid: {data}")
    
    def test_project_info_context_token_json_structure(self):
        """Validate /execute_command returns correct JSON for context request."""
        query = "Tell me about my project"  # Use exact keyword match
        response = client.post("/execute_command", json={"prompt": query})
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate structure
        assert data["success"] is True
        assert "response" in data
        
        # Response may be either:
        # 1. Direct token: "[UE_CONTEXT_REQUEST] project_info|question"
        # 2. AI response with token: "Let me gather... [UE_REQUEST] get_project_info"
        token = data["response"]
        
        # Check if it contains a UE token
        assert any(tok in token for tok in ["[UE_CONTEXT_REQUEST]", "[UE_REQUEST]"]), \
            f"Response should contain a UE token but got '{token}'"
        
        # If it's a direct context request token, validate format
        if token.startswith("[UE_CONTEXT_REQUEST] "):
            token_body = token.replace("[UE_CONTEXT_REQUEST] ", "")
            assert "|" in token_body, "Context token must have '|' separator"
            parts = token_body.split("|", 1)
            context_type = parts[0]
            print(f"✅ Direct Context Token: type='{context_type}'")
        else:
            # AI response with embedded token
            print(f"✅ AI Response with Token: {token[:80]}...")
    
    def test_blueprint_token_json_structure(self):
        """Validate blueprint list token JSON structure."""
        response = client.post("/execute_command", json={"prompt": "List all blueprints"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["response"] == "[UE_REQUEST] list_blueprints"
        
        print(f"✅ Blueprint Token Valid: {data['response']}")
    
    def test_error_response_json_structure(self):
        """Validate error response JSON structure."""
        response = client.post("/execute_command", json={})
        
        assert response.status_code == 200
        data = response.json()
        
        # Error responses have success=False and error field
        assert "success" in data
        assert data["success"] is False
        assert "error" in data
        assert isinstance(data["error"], str)
        
        print(f"✅ Error Structure Valid: {data}")


class TestUE5CallbackSimulation:
    """Simulate complete UE5 callback flow: token → context collection → /answer_with_context."""
    
    def test_project_info_complete_roundtrip(self):
        """
        Simulate complete flow:
        1. User asks 'what project am I in?'
        2. Backend returns token (direct or in AI response)
        3. UE5 collects project_info context
        4. UE5 calls /answer_with_context with context
        5. Backend returns natural language AI response
        """
        # Step 1: User query → token generation
        user_query = "Tell me about this project"  # Use exact keyword match
        token_response = client.post("/execute_command", json={"prompt": user_query})
        
        assert token_response.status_code == 200
        token_data = token_response.json()
        assert token_data["success"] is True
        
        # Step 2: Extract token (may be direct or embedded in AI response)
        response_text = token_data["response"]
        
        # Response should contain either context request or direct action
        assert any(tok in response_text for tok in ["[UE_CONTEXT_REQUEST]", "[UE_REQUEST]"]), \
            f"Response should contain token: {response_text}"
        
        # For this test, we'll simulate project_info context regardless of token type
        context_type = "project_info"
        original_question = user_query
        
        # Step 3: Simulate UE5 context collection
        mock_project_context = {
            "project_name": "MyAwesomeGame",
            "engine_version": "5.6.0",
            "platform": "Windows",
            "num_blueprints": 42,
            "num_maps": 3
        }
        
        # Step 4: Simulate UE5 callback to /answer_with_context
        ai_response = client.post("/answer_with_context", json={
            "question": original_question,
            "context": mock_project_context,
            "context_type": context_type
        })
        
        assert ai_response.status_code == 200
        ai_data = ai_response.json()
        
        # Step 5: Validate AI response
        assert "response" in ai_data
        response_text = ai_data["response"]
        
        # AI should reference the project name from context
        assert "MyAwesomeGame" in response_text, \
            f"AI should mention project name from context but got: {response_text}"
        
        print(f"✅ Complete Roundtrip Success!")
        print(f"   Query: {user_query}")
        print(f"   Token Response: {response_text[:80]}...")
        print(f"   Context Type: {context_type}")
        print(f"   AI Response: {ai_data['response'][:100]}...")
    
    def test_blueprint_capture_complete_roundtrip(self):
        """
        Simulate blueprint capture flow:
        1. User asks 'show me BP_Player blueprint'
        2. Backend returns token (may be AI response with capture_blueprint)
        3. UE5 captures blueprint screenshot
        4. UE5 calls /answer_with_context with base64 image
        5. Backend uses GPT-4 Vision to analyze
        """
        # Step 1: User query
        user_query = "Capture screenshot of BP_Player blueprint"  # Use exact keywords
        token_response = client.post("/execute_command", json={"prompt": user_query})
        
        assert token_response.status_code == 200
        token_data = token_response.json()
        
        # Step 2: Check for token (direct or embedded)
        response_text = token_data["response"]
        assert any(tok in response_text for tok in ["[UE_CONTEXT_REQUEST]", "[UE_REQUEST]", "blueprint", "capture"]), \
            f"Response should relate to blueprint capture: {response_text}"
        
        # Step 3: Simulate UE5 blueprint capture
        mock_blueprint_context = {
            "blueprint_name": "BP_Player",
            "blueprint_class": "Character",
            "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "num_nodes": 23
        }
        
        # Step 4: Simulate callback
        ai_response = client.post("/answer_with_context", json={
            "question": user_query,
            "context": mock_blueprint_context,
            "context_type": "blueprint_capture"
        })
        
        assert ai_response.status_code == 200
        ai_data = ai_response.json()
        
        # Step 5: Validate vision analysis
        response_text = ai_data["response"]
        assert "BP_Player" in response_text, \
            f"AI should mention blueprint name but got: {response_text}"
        
        print(f"✅ Blueprint Capture Roundtrip Success!")
        print(f"   AI Vision Response: {response_text[:100]}...")
    
    def test_browse_files_complete_roundtrip(self):
        """
        Simulate file browsing flow:
        1. User asks 'show me project files'
        2. Backend returns [UE_REQUEST] browse_files (direct action, no AI needed)
        """
        user_query = "Show me all project files"
        response = client.post("/execute_command", json={"prompt": user_query})
        
        assert response.status_code == 200
        data = response.json()
        
        # This is a direct action token, not a context request
        assert data["success"] is True
        assert data["response"] == "[UE_REQUEST] browse_files"
        
        print(f"✅ Direct Action Token: {data['response']}")


class TestContextAwareResponseValidation:
    """Verify AI responses are truly conditioned on provided context."""
    
    def test_ai_uses_distinctive_project_data(self):
        """Test that AI incorporates distinctive context data in response."""
        distinctive_project_name = "SuperUniqueGameName_XYZ123"
        
        context = {
            "project_name": distinctive_project_name,
            "engine_version": "5.6.0",
            "num_blueprints": 99
        }
        
        response = client.post("/answer_with_context", json={
            "question": "What's the name of my project?",
            "context": context,
            "context_type": "project_info"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # AI MUST include the distinctive project name
        assert distinctive_project_name in data["response"], \
            f"AI must use provided context. Expected '{distinctive_project_name}' in response but got: {data['response']}"
        
        print(f"✅ AI Context-Aware: Found '{distinctive_project_name}' in response")
    
    def test_ai_uses_viewport_camera_position(self):
        """Test that AI references actual camera position from context."""
        viewport_data = get_mock_viewport_context()
        
        # Extract distinctive camera position (it's a list [x, y, z])
        camera_location = viewport_data["camera"]["location"]
        
        response = client.post("/answer_with_context", json={
            "question": "Where is the camera located?",
            "context": viewport_data,
            "context_type": "viewport"
        })
        
        assert response.status_code == 200
        data = response.json()
        response_text = data["response"]
        
        # AI should reference camera coordinates (list format: [x, y, z])
        assert any(str(coord) in response_text for coord in camera_location), \
            f"AI should reference camera coordinates from context: {camera_location}\nGot: {response_text}"
        
        print(f"✅ AI References Camera Position: {camera_location}")
    
    def test_ai_distinguishes_different_contexts(self):
        """Test that AI gives different responses for different contexts."""
        # Same question, different contexts
        question = "What do you see?"
        
        # Context 1: Project with many actors
        context1 = {
            "actors": [
                {"name": "StaticMeshActor_1", "type": "StaticMeshActor"},
                {"name": "PointLight_5", "type": "PointLight"},
                {"name": "PlayerStart", "type": "PlayerStart"}
            ]
        }
        
        # Context 2: Project with few actors
        context2 = {
            "actors": [
                {"name": "EmptyActor", "type": "Actor"}
            ]
        }
        
        response1 = client.post("/answer_with_context", json={
            "question": question,
            "context": context1,
            "context_type": "viewport"
        })
        
        response2 = client.post("/answer_with_context", json={
            "question": question,
            "context": context2,
            "context_type": "viewport"
        })
        
        text1 = response1.json()["response"]
        text2 = response2.json()["response"]
        
        # Responses should be different due to different contexts
        assert text1 != text2, \
            "AI should give different responses for different contexts"
        
        # First should mention multiple actors
        assert "StaticMeshActor" in text1 or "PointLight" in text1, \
            f"AI should reference specific actors from context1: {text1}"
        
        print(f"✅ AI Distinguishes Contexts:")
        print(f"   Context 1 (3 actors): {text1[:80]}...")
        print(f"   Context 2 (1 actor): {text2[:80]}...")


class TestTokenInterpretationVariations:
    """Test that backend correctly interprets various query formulations."""
    
    def test_viewport_query_variations(self):
        """Test different ways to ask about viewport all return viewport-related response."""
        queries = [
            "What do I see in the viewport?",
            "Describe the viewport",
            "What's in the scene?"
        ]
        
        for query in queries:
            response = client.post("/execute_command", json={"prompt": query})
            data = response.json()
            
            assert data["success"] is True
            # Response should contain viewport-related token or mention viewport
            response_text = data["response"]
            assert "describe_viewport" in response_text or "viewport" in response_text.lower(), \
                f"Query '{query}' should produce viewport-related response but got '{response_text}'"
        
        print(f"✅ All viewport variations produce viewport-related responses")
    
    def test_project_info_query_variations(self):
        """Test different project queries all return project-related tokens."""
        queries = [
            "Tell me about this project",  # keyword match
            "What's my project called?",   # keyword match
            "Project breakdown please"     # keyword match
        ]
        
        for query in queries:
            response = client.post("/execute_command", json={"prompt": query})
            data = response.json()
            
            assert data["success"] is True
            response_text = data["response"]
            
            # All should contain either context request or project-related token
            assert any(tok in response_text for tok in ["[UE_CONTEXT_REQUEST]", "[UE_REQUEST]", "project"]), \
                f"Query '{query}' should produce project-related response but got '{response_text}'"
        
        print(f"✅ All project info variations produce project-related tokens")


class TestEdgeCasesAndErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_prompt_returns_error(self):
        """Test that empty prompt returns proper error structure."""
        response = client.post("/execute_command", json={"prompt": ""})
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "No prompt" in data["error"]
        
        print(f"✅ Empty prompt error: {data['error']}")
    
    def test_missing_prompt_field_returns_error(self):
        """Test that missing prompt field returns error."""
        response = client.post("/execute_command", json={})
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        
        print(f"✅ Missing prompt error: {data['error']}")
    
    def test_answer_with_context_missing_fields(self):
        """Test /answer_with_context validates required fields."""
        # Missing question
        response = client.post("/answer_with_context", json={
            "context": {},
            "context_type": "viewport"
        })
        
        assert response.status_code == 422 or "error" in response.json()
        
        print(f"✅ Missing field validation works")
    
    def test_answer_with_context_empty_context(self):
        """Test AI handles empty context gracefully."""
        response = client.post("/answer_with_context", json={
            "question": "What do you see?",
            "context": {},
            "context_type": "viewport"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        
        # AI should still provide a response even with empty context
        assert len(data["response"]) > 0
        
        print(f"✅ Empty context handled: {data['response'][:80]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
