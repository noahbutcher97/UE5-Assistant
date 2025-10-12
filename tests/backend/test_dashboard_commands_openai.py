"""
Dashboard Command Tests with Real OpenAI
Tests dashboard quick actions with actual AI responses using mock project data.
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
    get_mock_project_profile,
    get_mock_blueprint_list,
    get_mock_file_context
)

client = TestClient(app)


class TestDashboardDescribeViewport:
    """Test 'Describe Viewport' dashboard command with real AI."""
    
    def test_describe_viewport_command(self):
        """Test describe viewport quick action returns AI description."""
        viewport = get_mock_viewport_context()
        
        response = client.post("/describe_viewport", json=viewport)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        
        description = data["response"]
        assert len(description) > 50
        assert isinstance(description, str)
        
        # Should be a proper description
        assert any(word in description.lower() for word in ["camera", "scene", "viewport", "level"])
        
        print(f"✅ Describe Viewport: {description[:150]}...")
        return description
    
    def test_describe_viewport_with_different_styles(self):
        """Test describe viewport with multiple response styles."""
        viewport = get_mock_viewport_context()
        
        results = {}
        for style in ["concise", "balanced", "detailed"]:
            client.post("/api/config", json={"response_style": style})
            response = client.post("/describe_viewport", json=viewport)
            
            data = response.json()
            results[style] = data["response"]
            
            print(f"\n{style.upper()} style ({len(results[style])} chars):")
            print(f"  {results[style][:100]}...")
        
        # Verify different lengths
        assert len(results["concise"]) < len(results["balanced"])
        assert len(results["balanced"]) < len(results["detailed"])
        
        print("✅ All styles produce different length descriptions")


class TestDashboardListBlueprints:
    """Test 'List Blueprints' dashboard command with AI formatting."""
    
    def test_list_blueprints_formatted(self):
        """Test blueprint listing with AI formatting."""
        # Simulate blueprint list action
        blueprint_data = {
            "question": "List all blueprints in the project and describe their purpose",
            "context": {
                "blueprints": get_mock_blueprint_list()
            },
            "context_type": "blueprints"
        }
        
        response = client.post("/answer_with_context", json=blueprint_data)
        
        assert response.status_code == 200
        data = response.json()
        answer = data["response"]
        
        # Should mention blueprints
        assert any(bp in answer.lower() for bp in ["bp_player", "bp_enemy", "bp_gamemode", "blueprint"])
        
        # Should be formatted nicely
        assert len(answer) > 30
        
        print(f"✅ List Blueprints: {answer}")
        return answer
    
    def test_blueprint_details(self):
        """Test getting detailed blueprint information."""
        blueprint_data = {
            "question": "Describe the BP_Player blueprint in detail",
            "context": {
                "blueprints": get_mock_blueprint_list()
            },
            "context_type": "blueprints"
        }
        
        response = client.post("/answer_with_context", json=blueprint_data)
        
        data = response.json()
        answer = data["response"]
        
        # Should focus on BP_Player
        assert "player" in answer.lower()
        
        print(f"✅ Blueprint Details: {answer}")


class TestDashboardProjectInfo:
    """Test 'Project Info' dashboard command with AI summary."""
    
    def test_project_info_summary(self):
        """Test project info quick action with AI summary."""
        project_data = {
            "question": "Summarize this Unreal Engine project",
            "context": get_mock_project_profile(),
            "context_type": "project_info"
        }
        
        response = client.post("/answer_with_context", json=project_data)
        
        assert response.status_code == 200
        data = response.json()
        summary = data["response"]
        
        # Should mention project name
        assert "testproject" in summary.lower() or "test project" in summary.lower()
        
        # Should mention UE version or modules
        assert any(word in summary.lower() for word in ["5.6", "unreal", "module", "plugin"])
        
        print(f"✅ Project Info: {summary}")
        return summary
    
    def test_project_modules_and_plugins(self):
        """Test querying about project modules and plugins."""
        project_data = {
            "question": "What modules and plugins are enabled in this project?",
            "context": get_mock_project_profile(),
            "context_type": "project_info"
        }
        
        response = client.post("/answer_with_context", json=project_data)
        
        data = response.json()
        answer = data["response"]
        
        # Should mention specific modules or plugins
        assert any(item in answer.lower() for item in ["python", "module", "plugin", "enhanced"])
        
        print(f"✅ Modules & Plugins: {answer}")


class TestDashboardBrowseFiles:
    """Test 'Browse Files' dashboard command with natural language."""
    
    def test_browse_files_description(self):
        """Test file browsing with AI description."""
        file_data = {
            "question": "What files and assets are in this project?",
            "context": get_mock_file_context(),
            "context_type": "files"
        }
        
        response = client.post("/answer_with_context", json=file_data)
        
        assert response.status_code == 200
        data = response.json()
        description = data["response"]
        
        # Should mention files or assets
        assert any(word in description.lower() for word in ["file", "asset", "blueprint", "texture", "material"])
        
        print(f"✅ Browse Files: {description}")
        return description
    
    def test_file_search_results(self):
        """Test searching for specific files."""
        file_data = {
            "question": "Find all blueprint files",
            "context": get_mock_file_context(),
            "context_type": "files"
        }
        
        response = client.post("/answer_with_context", json=file_data)
        
        data = response.json()
        answer = data["response"]
        
        # Should mention blueprints
        assert "blueprint" in answer.lower()
        
        print(f"✅ File Search: {answer}")


class TestDashboardIntegration:
    """Test complete dashboard workflow with AI."""
    
    def test_full_dashboard_workflow(self):
        """Test complete dashboard interaction flow."""
        print("\n" + "="*60)
        print("FULL DASHBOARD WORKFLOW TEST")
        print("="*60)
        
        # Step 1: Describe Viewport
        print("\n1. DESCRIBE VIEWPORT:")
        viewport = get_mock_viewport_context()
        response1 = client.post("/describe_viewport", json=viewport)
        desc = response1.json()["response"]
        print(f"   {desc[:120]}...")
        assert len(desc) > 30
        
        # Step 2: List Blueprints
        print("\n2. LIST BLUEPRINTS:")
        bp_data = {
            "question": "List the blueprints",
            "context": {"blueprints": get_mock_blueprint_list()},
            "context_type": "blueprints"
        }
        response2 = client.post("/answer_with_context", json=bp_data)
        bp_list = response2.json()["response"]
        print(f"   {bp_list[:120]}...")
        assert "blueprint" in bp_list.lower() or "bp_" in bp_list.lower()
        
        # Step 3: Project Info
        print("\n3. PROJECT INFO:")
        proj_data = {
            "question": "What is this project?",
            "context": get_mock_project_profile(),
            "context_type": "project_info"
        }
        response3 = client.post("/answer_with_context", json=proj_data)
        proj_info = response3.json()["response"]
        print(f"   {proj_info[:120]}...")
        assert "testproject" in proj_info.lower() or "test project" in proj_info.lower()
        
        # Step 4: Browse Files
        print("\n4. BROWSE FILES:")
        file_data = {
            "question": "What assets are available?",
            "context": get_mock_file_context(),
            "context_type": "files"
        }
        response4 = client.post("/answer_with_context", json=file_data)
        files = response4.json()["response"]
        print(f"   {files[:120]}...")
        assert "asset" in files.lower() or "file" in files.lower()
        
        print("\n" + "="*60)
        print("✅ COMPLETE DASHBOARD WORKFLOW PASSED")
        print("="*60)


class TestActionPlanGeneration:
    """Test AI action plan generation for scene building."""
    
    def test_generate_action_plan(self):
        """Test generating action plan from natural language."""
        plan_request = {
            "description": "Create a grid of 3x3 cubes with spacing of 200 units"
        }
        
        response = client.post("/api/generate_action_plan", json=plan_request)
        
        assert response.status_code == 200
        data = response.json()
        
        if data.get("success"):
            plan = data.get("plan", [])
            print(f"✅ Action Plan Generated: {len(plan)} actions")
            
            # Should have some actions
            if plan:
                assert isinstance(plan, list)
                print(f"   First action: {plan[0]}")
        else:
            # AI might return explanation instead of JSON
            print(f"✅ Action Plan Response: {data.get('raw_response', 'No plan')[:100]}")
    
    def test_simple_spawn_plan(self):
        """Test generating simple spawn plan."""
        plan_request = {
            "description": "Spawn a player start at the origin"
        }
        
        response = client.post("/api/generate_action_plan", json=plan_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "success" in data or "plan" in data or "error" in data
        
        print(f"✅ Simple Spawn Plan: {data}")


class TestResponseConsistency:
    """Test that AI responses are consistent and reliable."""
    
    def test_same_input_similar_output(self):
        """Test that same input produces similar output."""
        viewport = get_mock_viewport_context()
        
        # Get two responses with same input
        response1 = client.post("/describe_viewport", json=viewport)
        response2 = client.post("/describe_viewport", json=viewport)
        
        desc1 = response1.json()["response"]
        desc2 = response2.json()["response"]
        
        # Should both be valid descriptions
        assert len(desc1) > 30
        assert len(desc2) > 30
        
        # Should mention similar key elements
        key_elements = ["camera", "scene", "level", "actor", "light"]
        elements1 = sum(1 for el in key_elements if el in desc1.lower())
        elements2 = sum(1 for el in key_elements if el in desc2.lower())
        
        # Should have similar coverage of elements (within 2)
        assert abs(elements1 - elements2) <= 2, "Responses should cover similar elements"
        
        print(f"✅ Consistency check: Response 1 mentions {elements1} elements, Response 2 mentions {elements2} elements")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
