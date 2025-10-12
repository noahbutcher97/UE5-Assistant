"""
Production-Ready Token Routing Tests
====================================
Deterministic tests with mocked OpenAI responses and strict assertions.
Validates exact JSON payloads and token formats without external dependencies.

Test Categories:
1. Unit Tests - Keyword routing logic (no OpenAI calls)
2. Integration Tests - Full flow with mocked AI responses
3. Strict Contract Validation - Exact JSON structure matching
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from tests.fixtures.mock_viewport_data import get_mock_viewport_context
from tests.fixtures.mock_openai_responses import (
    create_mock_openai_response,
    DIRECT_TOKEN_RESPONSES,
    get_mock_context_response
)

client = TestClient(app)


class TestKeywordRoutingUnitTests:
    """Unit tests for direct keyword-based token routing (no OpenAI calls)."""
    
    def test_viewport_keyword_exact_token(self):
        """Test 'viewport' keyword returns exact direct token."""
        response = client.post("/execute_command", json={"prompt": "What do I see in the viewport?"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Exact structure validation
        assert data == {
            "success": True,
            "response": "[UE_REQUEST] describe_viewport"
        }, f"Expected exact token but got: {data}"
    
    def test_scene_keyword_exact_token(self):
        """Test 'scene' keyword returns exact viewport token."""
        response = client.post("/execute_command", json={"prompt": "Describe the scene"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data == {
            "success": True,
            "response": "[UE_REQUEST] describe_viewport"
        }
    
    def test_list_actors_keyword_exact_token(self):
        """Test 'list actors' keyword returns exact token."""
        response = client.post("/execute_command", json={"prompt": "List actors in the level"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data == {
            "success": True,
            "response": "[UE_REQUEST] list_actors"
        }
    
    def test_list_blueprints_keyword_exact_token(self):
        """Test 'list blueprints' keyword returns exact token."""
        response = client.post("/execute_command", json={"prompt": "List all blueprints"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data == {
            "success": True,
            "response": "[UE_REQUEST] list_blueprints"
        }
    
    def test_browse_files_keyword_exact_token(self):
        """Test 'browse files' keyword returns exact token."""
        response = client.post("/execute_command", json={"prompt": "Show me the project files"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data == {
            "success": True,
            "response": "[UE_REQUEST] browse_files"
        }
    
    def test_project_info_context_request_exact_format(self):
        """Test 'project info' keyword returns exact context request format."""
        query = "Tell me about my project"
        response = client.post("/execute_command", json={"prompt": query})
        
        assert response.status_code == 200
        data = response.json()
        
        # Exact context request format: [UE_CONTEXT_REQUEST] context_type|original_question
        assert data["success"] is True
        assert data["response"] == f"[UE_CONTEXT_REQUEST] project_info|{query}"
    
    def test_blueprint_capture_context_request_exact_format(self):
        """Test blueprint capture keywords return exact context request."""
        query = "Capture screenshot of BP_Player blueprint"
        response = client.post("/execute_command", json={"prompt": query})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["response"] == f"[UE_CONTEXT_REQUEST] blueprint_capture|{query}"
    
    def test_selected_info_keyword_exact_token(self):
        """Test 'selected info' keywords return exact token."""
        response = client.post("/execute_command", json={"prompt": "Show details of selected actor"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data == {
            "success": True,
            "response": "[UE_REQUEST] get_selected_info"
        }


class TestOpenAIMockedIntegration:
    """Integration tests with mocked OpenAI responses for deterministic behavior."""
    
    @patch('openai.chat.completions.create')
    def test_non_keyword_query_calls_openai(self, mock_openai):
        """Test that non-keyword queries fall through to OpenAI."""
        # Setup mock
        mock_openai.return_value = create_mock_openai_response(
            "[UE_REQUEST] describe_viewport"
        )
        
        response = client.post("/execute_command", json={"prompt": "What's happening in the editor?"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should call OpenAI
        assert mock_openai.called
        
        # Should extract and return clean token
        assert data == {
            "success": True,
            "response": "[UE_REQUEST] describe_viewport"
        }
    
    @patch('openai.chat.completions.create')
    def test_openai_response_starting_with_token_gets_extracted(self, mock_openai):
        """Test that OpenAI responses starting with [UE_REQUEST] get extracted correctly."""
        # Mock AI response that STARTS with token (will be extracted and reformatted)
        mock_openai.return_value = create_mock_openai_response(
            "[UE_REQUEST] describe_viewport"
        )
        
        # Use non-keyword query to trigger OpenAI
        response = client.post("/execute_command", json={"prompt": "Can you help me understand the editor?"})
        
        assert response.status_code == 200
        data = response.json()
        
        # When OpenAI response starts with [UE_REQUEST], route extracts and reformats it
        assert data == {
            "success": True,
            "response": "[UE_REQUEST] describe_viewport"
        }


class TestAnswerWithContextDeterministic:
    """Test /answer_with_context with mocked OpenAI for deterministic responses."""
    
    @patch('openai.chat.completions.create')
    def test_viewport_context_processing_exact_response(self, mock_openai):
        """Test viewport context produces deterministic AI response."""
        viewport_context = get_mock_viewport_context()
        
        # Mock deterministic response
        expected_response = get_mock_context_response(
            "Where is the camera?",
            viewport_context,
            "viewport"
        )
        mock_openai.return_value = create_mock_openai_response(expected_response)
        
        response = client.post("/answer_with_context", json={
            "question": "Where is the camera?",
            "context": viewport_context,
            "context_type": "viewport"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert data["response"] == expected_response
    
    @patch('openai.chat.completions.create')
    def test_project_info_context_with_distinctive_data(self, mock_openai):
        """Test project context with distinctive data produces exact expected response."""
        distinctive_project = {
            "project_name": "ProductionGameAlpha2024",
            "engine_version": "5.6.0",
            "num_blueprints": 42
        }
        
        expected_response = get_mock_context_response(
            "What project am I working on?",
            distinctive_project,
            "project_info"
        )
        mock_openai.return_value = create_mock_openai_response(expected_response)
        
        response = client.post("/answer_with_context", json={
            "question": "What project am I working on?",
            "context": distinctive_project,
            "context_type": "project_info"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Exact match with mocked response
        assert data == {
            "response": expected_response
        }


class TestCompleteRoundtripWithMocks:
    """Test complete flow: query → token → context → AI response (all mocked)."""
    
    @patch('openai.chat.completions.create')
    def test_project_info_complete_flow_deterministic(self, mock_openai):
        """Test complete project info flow with deterministic mocked responses."""
        
        # Step 1: User query (keyword match - no OpenAI call)
        query = "Tell me about this project"
        token_response = client.post("/execute_command", json={"prompt": query})
        
        assert token_response.status_code == 200
        token_data = token_response.json()
        
        # Should return exact context request token
        assert token_data == {
            "success": True,
            "response": f"[UE_CONTEXT_REQUEST] project_info|{query}"
        }
        
        # Step 2: Simulate UE5 context collection
        project_context = {
            "project_name": "TestGameProject",
            "engine_version": "5.6.0",
            "num_blueprints": 15
        }
        
        # Step 3: Mock AI response for context processing
        expected_ai_response = get_mock_context_response(query, project_context, "project_info")
        mock_openai.return_value = create_mock_openai_response(expected_ai_response)
        
        # Step 4: UE5 calls /answer_with_context
        ai_response = client.post("/answer_with_context", json={
            "question": query,
            "context": project_context,
            "context_type": "project_info"
        })
        
        assert ai_response.status_code == 200
        ai_data = ai_response.json()
        
        # Validate deterministic response
        assert "response" in ai_data
        assert "TestGameProject" in ai_data["response"]
        assert "5.6.0" in ai_data["response"]
    
    def test_viewport_token_no_openai_needed(self):
        """Test viewport query completes without OpenAI (keyword match)."""
        # Step 1: Query with keyword match
        response = client.post("/execute_command", json={"prompt": "Describe the viewport"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return direct token without calling OpenAI
        assert data == {
            "success": True,
            "response": "[UE_REQUEST] describe_viewport"
        }
        
        # This is a direct action token - UE5 would execute immediately
        # No context collection or AI processing needed


class TestStrictJSONContractValidation:
    """Validate exact JSON structures match API contract."""
    
    def test_execute_command_success_structure(self):
        """Validate success response has exact required fields."""
        response = client.post("/execute_command", json={"prompt": "List actors"})
        
        data = response.json()
        
        # Exact keys check
        assert set(data.keys()) == {"success", "response"}
        assert isinstance(data["success"], bool)
        assert isinstance(data["response"], str)
        assert data["success"] is True
    
    def test_execute_command_error_structure(self):
        """Validate error response has exact required fields."""
        response = client.post("/execute_command", json={})
        
        data = response.json()
        
        # Error responses must have success=False and error field
        assert "success" in data
        assert "error" in data
        assert data["success"] is False
        assert isinstance(data["error"], str)
    
    def test_answer_with_context_response_structure(self):
        """Validate /answer_with_context response structure."""
        with patch('openai.chat.completions.create') as mock_openai:
            mock_openai.return_value = create_mock_openai_response("Test response")
            
            response = client.post("/answer_with_context", json={
                "question": "test",
                "context": {},
                "context_type": "viewport"
            })
            
            data = response.json()
            
            # Must have response field
            assert "response" in data
            assert isinstance(data["response"], str)


class TestTokenFormatValidation:
    """Validate exact token formats match UE5 client expectations."""
    
    def test_direct_action_token_format(self):
        """Validate [UE_REQUEST] action_token format."""
        response = client.post("/execute_command", json={"prompt": "List actors"})
        data = response.json()
        
        token = data["response"]
        
        # Exact format: [UE_REQUEST] action_token
        assert token.startswith("[UE_REQUEST] ")
        parts = token.split(" ", 1)
        assert len(parts) == 2
        assert parts[0] == "[UE_REQUEST]"
        assert parts[1] in ["list_actors", "describe_viewport", "list_blueprints", "browse_files", "get_selected_info", "get_project_info"]
    
    def test_context_request_token_format(self):
        """Validate [UE_CONTEXT_REQUEST] context_type|question format."""
        query = "Tell me about this project"
        response = client.post("/execute_command", json={"prompt": query})
        data = response.json()
        
        token = data["response"]
        
        # Exact format: [UE_CONTEXT_REQUEST] context_type|original_question
        assert token.startswith("[UE_CONTEXT_REQUEST] ")
        token_body = token.replace("[UE_CONTEXT_REQUEST] ", "")
        assert "|" in token_body
        
        parts = token_body.split("|", 1)
        context_type = parts[0]
        original_question = parts[1]
        
        assert context_type == "project_info"
        assert original_question == query


class TestErrorHandlingDeterministic:
    """Test error handling with deterministic assertions."""
    
    def test_empty_prompt_exact_error(self):
        """Test empty prompt returns exact error structure."""
        response = client.post("/execute_command", json={"prompt": ""})
        
        data = response.json()
        
        assert data == {
            "success": False,
            "error": "No prompt provided."
        }
    
    def test_missing_prompt_field_exact_error(self):
        """Test missing prompt field returns exact error."""
        response = client.post("/execute_command", json={})
        
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
        assert "No prompt" in data["error"]
    
    def test_answer_with_context_missing_question(self):
        """Test /answer_with_context validates required question field with exact error."""
        response = client.post("/answer_with_context", json={
            "context": {},
            "context_type": "viewport"
        })
        
        # Should return exact error response
        assert response.status_code == 200
        data = response.json()
        
        # Exact error structure
        assert data == {
            "error": "No question provided"
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
