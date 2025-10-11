"""Pydantic data models for the UE5 AI Assistant backend."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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


class FileEntry(BaseModel):
    """Represents a single file or directory entry."""
    path: str
    name: str
    type: str  # "file" or "directory"
    extension: Optional[str] = None
    size: Optional[int] = None
    modified: Optional[str] = None
    content: Optional[str] = None  # Populated when reading file content


class FileContext(BaseModel):
    """File system context for AI analysis."""
    root_path: str
    files: List[FileEntry] = Field(default_factory=list)
    search_query: Optional[str] = None
    total_files: int = 0
    total_size: int = 0


class ProjectProfile(BaseModel):
    """Comprehensive project metadata and structure."""
    project_name: str
    project_path: str
    engine_version: Optional[str] = None
    modules: List[str] = Field(default_factory=list)
    plugins: List[str] = Field(default_factory=list)
    content_stats: Optional[Dict[str, Any]] = None  # Asset counts by type
    source_stats: Optional[Dict[str, Any]] = None  # C++ file counts
    build_targets: List[str] = Field(default_factory=list)
    gameplay_tags: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class BlueprintCapture(BaseModel):
    """Blueprint screenshot and metadata."""
    blueprint_name: str
    blueprint_path: str
    capture_id: str
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None  # Graph info, node count, etc.
    timestamp: str


class GuidanceRequest(BaseModel):
    """Request for context-aware implementation guidance."""
    query: str
    viewport_context: Optional[ViewportContext] = None
    file_context: Optional[FileContext] = None
    project_profile: Optional[ProjectProfile] = None
    blueprint_captures: Optional[List[BlueprintCapture]] = None
    focus_area: Optional[str] = None  # "gameplay", "rendering", "networking", etc.


class ContextBundle(BaseModel):
    """Unified context bundle for comprehensive AI analysis."""
    request_type: str  # "guidance", "analysis", "description"
    viewport: Optional[ViewportContext] = None
    files: Optional[FileContext] = None
    project: Optional[ProjectProfile] = None
    blueprints: Optional[List[BlueprintCapture]] = None
    user_query: str
    metadata: Optional[Dict[str, Any]] = None
