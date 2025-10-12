"""
Mock OpenAI Responses for Deterministic Testing
Provides stubbed responses that match actual OpenAI API behavior
without external dependencies or rate limits.
"""

from typing import Dict, Any
from unittest.mock import MagicMock


def create_mock_openai_response(content: str) -> MagicMock:
    """Create a mock OpenAI ChatCompletion response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = content
    return mock_response


# Deterministic token responses (no AI processing needed)
DIRECT_TOKEN_RESPONSES = {
    "viewport": "[UE_REQUEST] describe_viewport",
    "list_actors": "[UE_REQUEST] list_actors",
    "list_blueprints": "[UE_REQUEST] list_blueprints",
    "browse_files": "[UE_REQUEST] browse_files",
    "get_selected": "[UE_REQUEST] get_selected_info",
}

# Deterministic context request tokens
CONTEXT_REQUEST_TOKENS = {
    "project_info": lambda q: f"[UE_CONTEXT_REQUEST] project_info|{q}",
    "blueprint_capture": lambda q: f"[UE_CONTEXT_REQUEST] blueprint_capture|{q}",
}

# Deterministic AI responses for /answer_with_context
def get_viewport_context_response(context: Dict[str, Any]) -> str:
    """Generate deterministic response for viewport context."""
    camera = context.get("camera", {})
    actors = context.get("actors", {})
    
    if isinstance(camera.get("location"), list):
        loc = camera["location"]
        location_str = f"at position ({loc[0]}, {loc[1]}, {loc[2]})"
    else:
        location_str = "at the current position"
    
    actor_count = actors.get("total", 0)
    
    return f"The viewport shows {actor_count} actors. The camera is located {location_str}."


def get_project_info_response(context: Dict[str, Any]) -> str:
    """Generate deterministic response for project info context."""
    project_name = context.get("project_name", "Unknown Project")
    engine_version = context.get("engine_version", "Unknown")
    num_blueprints = context.get("num_blueprints", 0)
    
    return f"You are working on the project '{project_name}' using Unreal Engine {engine_version}. The project contains {num_blueprints} blueprints."


def get_blueprint_context_response(context: Dict[str, Any]) -> str:
    """Generate deterministic response for blueprint context."""
    bp_name = context.get("blueprint_name", "Unknown Blueprint")
    bp_class = context.get("blueprint_class", "Unknown")
    num_nodes = context.get("num_nodes", 0)
    
    return f"The blueprint '{bp_name}' is a {bp_class} blueprint containing {num_nodes} nodes."


def get_file_context_response(context: Dict[str, Any]) -> str:
    """Generate deterministic response for file context."""
    total_files = context.get("total_files", 0)
    files = context.get("files", [])
    
    if files:
        file_types = {f.get("type", "Unknown") for f in files}
        types_str = ", ".join(file_types)
        return f"The project contains {total_files} files including: {types_str}."
    return f"The project contains {total_files} files."


# AI responses with embedded tokens (for queries that don't match keywords)
AI_RESPONSES_WITH_TOKENS = {
    "generic_viewport": "Let me gather the viewport information for you.\n\n[UE_REQUEST] describe_viewport",
    "generic_project": "To determine your current project, I'll collect the project information.\n\n[UE_REQUEST] get_project_info",
    "generic_blueprints": "I'll retrieve the list of blueprints in your project.\n\n[UE_REQUEST] list_blueprints",
}


def get_mock_context_response(question: str, context: Dict[str, Any], context_type: str) -> str:
    """
    Generate deterministic AI response based on context type.
    This simulates what OpenAI would return but with predictable output.
    """
    handlers = {
        "viewport": get_viewport_context_response,
        "project_info": get_project_info_response,
        "blueprint_capture": get_blueprint_context_response,
        "browse_files": get_file_context_response,
    }
    
    handler = handlers.get(context_type)
    if handler:
        return handler(context)
    
    # Fallback
    return f"Based on the provided {context_type} context: {question}"
