# Data Models Documentation

## Overview

All data models use Pydantic v2 for validation, serialization, and type safety. Models support both v2.0 (modular) and v1.0 (legacy) data structures for backward compatibility.

## Core Models

### ViewportContext

**Purpose**: Represents Unreal Engine viewport state sent from UE5 client.

**Structure**:

```python
class ViewportContext(BaseModel):
    # v2.0 Modular Structure (Current)
    camera: Optional[Dict[str, Any]] = None
    actors: Optional[Dict[str, Any]] = None
    lighting: Optional[Dict[str, Any]] = None
    environment: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None
    project_metadata: Optional[Dict[str, Any]] = None
    
    # v1.0 Legacy Fields (Backward Compatibility)
    camera_location: Optional[List[float]] = None
    camera_rotation: Optional[List[float]] = None
    visible_actors: Optional[List[str]] = None
    selected_actor: Optional[str]] = None
    additional_info: Optional[Dict[str, Any]] = None
```

**v2.0 Structure Details**:

#### camera
```json
{
  "location": [x, y, z],
  "rotation": [pitch, yaw, roll]
}
```

#### actors
```json
{
  "total": 47,
  "names": ["Actor1", "Actor2", ...],
  "types": {"StaticMeshActor": 12, "PointLight": 3},
  "level": "LevelName"
}
```

#### lighting
```json
{
  "directional_lights": [
    {"name": "DirectionalLight", "location": [...], "rotation": [...], "intensity": 10}
  ],
  "point_lights": [...],
  "spot_lights": [...],
  "sky_atmosphere": "SkyAtmosphere_0"
}
```

#### environment
```json
{
  "fog": ["ExponentialHeightFog"],
  "post_process_volumes": ["PostProcessVolume_0"],
  "landscape": "Landscape_0"
}
```

#### selection
```json
{
  "count": 2,
  "actors": [
    {
      "name": "Cube_1",
      "class": "StaticMeshActor",
      "location": [100, 200, 50],
      "materials": ["Material_0", "Material_1"]
    }
  ]
}
```

#### project_metadata (optional)
```json
{
  "project_name": "MyUE5Project",
  "project_path": "/path/to/project",
  "content_folder_stats": {
    "uasset_count": 450,
    "level_count": 3,
    "total_mb": 1250.5
  },
  "source_code_stats": {
    "has_source": true,
    "cpp_file_count": 25,
    "header_file_count": 30
  },
  "asset_summary": {
    "total_assets": 450,
    "asset_types": {"StaticMesh": 120, "Material": 80, ...},
    "top_asset_types": [["StaticMesh", 120], ["Material", 80], ...]
  }
}
```

**Validation Rules**:
- All fields are optional to support partial data
- Type validation ensures correct data structures
- Backward compatible with v1.0 flat structure

---

### ConversationEntry

**Purpose**: Represents a single conversation exchange for logging and dashboard display.

**Structure**:

```python
class ConversationEntry(BaseModel):
    timestamp: str
    user_input: str
    assistant_response: str
    command_type: str
    metadata: Optional[Dict[str, Any]] = None
```

**Fields**:

- **timestamp**: ISO 8601 format (e.g., "2025-10-11T15:30:45.123Z")
- **user_input**: Original user prompt or "Describe viewport"
- **assistant_response**: AI-generated response text
- **command_type**: One of: `execute_command`, `describe_viewport`, `wrap_natural_language`
- **metadata**: Optional data like `{"actors_count": 47, "has_selection": true, "error": false}`

**Usage**:
- Stored in `conversations.jsonl` (JSON Lines format)
- Displayed in web dashboard
- Used for analytics and debugging

---

### ConfigUpdate

**Purpose**: Request model for updating backend configuration via API.

**Structure**:

```python
class ConfigUpdate(BaseModel):
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_context_turns: Optional[int] = None
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    retry_delay: Optional[float] = None
    verbose: Optional[bool] = None
    response_style: Optional[str] = None
```

**Validation Rules**:
- All fields optional (partial updates supported)
- `model`: Must be valid OpenAI model name
- `temperature`: 0.0 - 2.0 (typical: 0.7-1.0)
- `response_style`: Must match key in `RESPONSE_STYLES` dict

**Example Request**:
```json
{
  "response_style": "creative",
  "temperature": 0.9
}
```

---

## Data Flow

1. **UE5 → Backend**: `ViewportContext` received in `/describe_viewport` endpoint
2. **Validation**: Pydantic validates and coerces data types
3. **Filtering**: `services/filtering.py` extracts relevant fields based on response style
4. **AI Processing**: Filtered data sent to OpenAI
5. **Response**: AI output returned as JSON
6. **Logging**: `ConversationEntry` created and persisted

## Type Safety Benefits

- **Compile-time Checks**: Type hints enable IDE autocomplete and static analysis
- **Runtime Validation**: Pydantic validates incoming data
- **Serialization**: Automatic JSON conversion with `.model_dump()`
- **Documentation**: Models self-document API contracts

## Backward Compatibility

The `ViewportContext` model supports both:
- **v2.0**: Nested modular structure (current)
- **v1.0**: Flat structure with `camera_location`, `visible_actors`, etc.

This ensures older UE5 clients continue to work while new clients use the enhanced structure.
