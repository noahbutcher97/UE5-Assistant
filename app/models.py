"""Pydantic data models for the UE5 AI Assistant backend."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ViewportContext(BaseModel):
    """
    Describes the Unreal Engine editor viewport context.
    Compatible with modular AIAssistant v2.0 structure.
    """
    # New v2.0 structure (modular)
    camera: Optional[Dict[str, Any]] = None
    actors: Optional[Dict[str, Any]] = None
    lighting: Optional[Dict[str, Any]] = None
    environment: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None
    project_metadata: Optional[Dict[str, Any]] = None
    
    # Legacy v1.0 fields (backward compatibility)
    camera_location: Optional[List[float]] = None
    camera_rotation: Optional[List[float]] = None
    visible_actors: Optional[List[str]] = None
    selected_actor: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class ConversationEntry(BaseModel):
    """A single conversation exchange."""
    timestamp: str
    user_input: str
    assistant_response: str
    command_type: str
    metadata: Optional[Dict[str, Any]] = None


class ConfigUpdate(BaseModel):
    """Configuration update model."""
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_context_turns: Optional[int] = None
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    retry_delay: Optional[float] = None
    verbose: Optional[bool] = None
    response_style: Optional[str] = None
