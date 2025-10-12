"""
OpenAI Integration Tests - Test Real AI Responses
Tests all 7 response styles with actual OpenAI API calls using mock viewport data.
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from tests.fixtures.mock_viewport_data import (
    get_mock_viewport_context,
    get_minimal_viewport_context,
    get_complex_viewport_context,
    get_mock_project_profile
)

client = TestClient(app)


class TestResponseStyles:
    """Test all 7 response styles with real OpenAI."""
    
    def test_descriptive_style(self):
        """Test descriptive (default) response style."""
        # Set style to descriptive
        client.post("/api/config", json={"response_style": "descriptive"})
        
        # Send viewport context
        viewport = get_mock_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        
        description = data["response"]
        assert len(description) > 50  # Should be substantial
        assert len(description.split()) <= 450  # ~400 tokens max
        
        # Should mention key elements
        assert any(word in description.lower() for word in ["camera", "viewport", "scene"])
        print(f"✅ Descriptive style response ({len(description)} chars): {description[:100]}...")
    
    def test_technical_style(self):
        """Test technical/precise response style."""
        client.post("/api/config", json={"response_style": "technical"})
        
        viewport = get_mock_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        assert response.status_code == 200
        data = response.json()
        description = data["response"]
        
        # Technical style should include precise details
        assert len(description) > 100
        assert len(description.split()) <= 550  # ~500 tokens max
        
        # Should mention technical details (coordinates, counts, etc.)
        has_numbers = any(char.isdigit() for char in description)
        assert has_numbers, "Technical style should include numeric details"
        
        print(f"✅ Technical style response ({len(description)} chars): {description[:100]}...")
    
    def test_natural_style(self):
        """Test natural/conversational response style."""
        client.post("/api/config", json={"response_style": "natural"})
        
        viewport = get_mock_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        assert response.status_code == 200
        data = response.json()
        description = data["response"]
        
        # Natural style should be conversational and concise
        assert len(description) > 30
        assert len(description.split()) <= 350  # ~300 tokens max
        
        # Should sound conversational
        conversational_indicators = ["see", "you", "there", "the", "is", "are"]
        assert any(word in description.lower() for word in conversational_indicators)
        
        print(f"✅ Natural style response ({len(description)} chars): {description[:100]}...")
    
    def test_balanced_style(self):
        """Test balanced response style."""
        client.post("/api/config", json={"response_style": "balanced"})
        
        viewport = get_mock_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        assert response.status_code == 200
        data = response.json()
        description = data["response"]
        
        # Balanced should be medium length
        assert len(description) > 50
        assert len(description.split()) <= 400  # ~350 tokens max
        
        print(f"✅ Balanced style response ({len(description)} chars): {description[:100]}...")
    
    def test_concise_style(self):
        """Test concise/brief response style."""
        client.post("/api/config", json={"response_style": "concise"})
        
        viewport = get_minimal_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        assert response.status_code == 200
        data = response.json()
        description = data["response"]
        
        # Concise should be very brief
        assert len(description) > 20
        assert len(description.split()) <= 180  # ~150 tokens max, should be brief
        
        # Should focus on essentials
        assert any(word in description.lower() for word in ["camera", "actor"])
        
        print(f"✅ Concise style response ({len(description)} chars): {description}")
    
    def test_detailed_style(self):
        """Test detailed/verbose response style."""
        client.post("/api/config", json={"response_style": "detailed"})
        
        viewport = get_complex_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        assert response.status_code == 200
        data = response.json()
        description = data["response"]
        
        # Detailed should be comprehensive
        assert len(description) > 200
        assert len(description.split()) <= 900  # ~800 tokens max
        
        # Should include extensive details
        assert "light" in description.lower() or "lighting" in description.lower()
        
        print(f"✅ Detailed style response ({len(description)} chars): {description[:150]}...")
    
    def test_creative_style(self):
        """Test creative/imaginative response style."""
        client.post("/api/config", json={"response_style": "creative"})
        
        viewport = get_mock_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        assert response.status_code == 200
        data = response.json()
        description = data["response"]
        
        # Creative should be vivid and descriptive
        assert len(description) > 80
        assert len(description.split()) <= 500  # ~450 tokens max
        
        # Creative style often uses metaphors, imagery
        # Just verify it's engaging and narrative-like
        assert len(description.split()) > 30  # Should be substantial
        
        print(f"✅ Creative style response ({len(description)} chars): {description[:100]}...")


class TestViewportDescriptionQuality:
    """Test quality and accuracy of viewport descriptions."""
    
    def test_viewport_with_selection(self):
        """Test that selection is mentioned in description."""
        client.post("/api/config", json={"response_style": "balanced"})
        
        viewport = get_mock_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        data = response.json()
        description = data["response"]
        
        # Should mention the selected actor (BP_Player_2)
        assert "player" in description.lower() or "selected" in description.lower()
        
        print(f"✅ Selection mentioned in description")
    
    def test_viewport_with_lighting(self):
        """Test that lighting is described."""
        client.post("/api/config", json={"response_style": "technical"})
        
        viewport = get_mock_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        data = response.json()
        description = data["response"]
        
        # Should mention lighting
        assert any(word in description.lower() for word in ["light", "lighting", "illumination", "directional"])
        
        print(f"✅ Lighting mentioned in description")
    
    def test_viewport_with_camera_position(self):
        """Test that camera position is described."""
        client.post("/api/config", json={"response_style": "descriptive"})
        
        viewport = get_mock_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        data = response.json()
        description = data["response"]
        
        # Should mention camera or view
        assert any(word in description.lower() for word in ["camera", "view", "viewport", "position"])
        
        print(f"✅ Camera position mentioned in description")


class TestContextAwareResponses:
    """Test context-aware AI responses with project metadata."""
    
    def test_answer_with_project_context(self):
        """Test answering questions with project context."""
        context_data = {
            "question": "What is the name of this project?",
            "context": get_mock_project_profile(),
            "context_type": "project_info"
        }
        
        response = client.post("/answer_with_context", json=context_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        
        answer = data["response"]
        # Should mention TestProject
        assert "testproject" in answer.lower() or "test project" in answer.lower()
        
        print(f"✅ Context-aware response: {answer}")
    
    def test_answer_with_viewport_context(self):
        """Test answering questions about viewport."""
        context_data = {
            "question": "What lighting is in the scene?",
            "context": get_mock_viewport_context(),
            "context_type": "viewport"
        }
        
        response = client.post("/answer_with_context", json=context_data)
        
        assert response.status_code == 200
        data = response.json()
        answer = data["response"]
        
        # Should mention the lighting
        assert any(word in answer.lower() for word in ["light", "directional", "point"])
        
        print(f"✅ Viewport context response: {answer[:100]}...")
    
    def test_answer_about_blueprints(self):
        """Test answering questions about project blueprints."""
        from tests.fixtures.mock_viewport_data import get_mock_blueprint_list
        
        context_data = {
            "question": "What blueprints are in this project?",
            "context": {
                "blueprints": get_mock_blueprint_list()
            },
            "context_type": "blueprints"
        }
        
        response = client.post("/answer_with_context", json=context_data)
        
        assert response.status_code == 200
        data = response.json()
        answer = data["response"]
        
        # Should mention blueprints
        assert any(bp in answer.lower() for bp in ["bp_player", "bp_enemy", "bp_gamemode", "player", "enemy", "gamemode"])
        
        print(f"✅ Blueprint context response: {answer}")


class TestTokenLimits:
    """Verify token limits are respected for each style."""
    
    def test_all_styles_respect_token_limits(self):
        """Test that all styles stay within token limits."""
        styles_and_limits = {
            "concise": 180,      # 150 tokens ~= 180 words max
            "natural": 350,      # 300 tokens ~= 350 words max
            "balanced": 400,     # 350 tokens ~= 400 words max
            "descriptive": 450,  # 400 tokens ~= 450 words max
            "creative": 500,     # 450 tokens ~= 500 words max
            "technical": 550,    # 500 tokens ~= 550 words max
            "detailed": 900      # 800 tokens ~= 900 words max
        }
        
        viewport = get_mock_viewport_context()
        
        for style, max_words in styles_and_limits.items():
            client.post("/api/config", json={"response_style": style})
            response = client.post("/describe_viewport", json=viewport)
            
            data = response.json()
            description = data["response"]
            word_count = len(description.split())
            
            assert word_count <= max_words, f"{style} style exceeded word limit: {word_count} > {max_words}"
            print(f"✅ {style.capitalize()} style: {word_count} words (limit: {max_words})")


class TestDataFiltering:
    """Test that data filtering works correctly for different styles."""
    
    def test_minimal_filter_for_concise(self):
        """Test that concise style uses minimal filtering."""
        client.post("/api/config", json={"response_style": "concise"})
        
        viewport = get_complex_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        data = response.json()
        description = data["response"]
        
        # Concise should focus on essentials only
        # Should be brief despite complex input
        assert len(description.split()) <= 180
        
        print(f"✅ Concise style filters complex data: {len(description.split())} words")
    
    def test_complete_filter_for_detailed(self):
        """Test that detailed style includes comprehensive data."""
        client.post("/api/config", json={"response_style": "detailed"})
        
        viewport = get_complex_viewport_context()
        response = client.post("/describe_viewport", json=viewport)
        
        data = response.json()
        description = data["response"]
        
        # Detailed should include extensive information
        assert len(description.split()) > 100
        
        # Should mention multiple elements
        element_mentions = sum([
            "light" in description.lower(),
            "actor" in description.lower(),
            "camera" in description.lower(),
            "atmosphere" in description.lower() or "sky" in description.lower()
        ])
        assert element_mentions >= 2, "Detailed style should mention multiple scene elements"
        
        print(f"✅ Detailed style includes comprehensive data: {len(description.split())} words")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
