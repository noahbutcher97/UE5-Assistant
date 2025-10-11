# Services Layer Documentation

## Overview

The services layer contains business logic separated from HTTP concerns. Each service module has a focused responsibility and can be tested independently.

## Service Modules

### openai_client.py

**Purpose**: OpenAI API integration for AI-powered viewport descriptions

#### Key Functions

##### `generate_viewport_description()`
```python
def generate_viewport_description(
    filtered_data: Dict[str, Any],
    response_style: str,
    style_config: Dict[str, Any],
    model: str,
    temperature: float
) -> str
```

**Purpose**: Generate AI description from filtered viewport data

**Parameters**:
- `filtered_data`: Viewport data after intelligent filtering
- `response_style`: Current style name (e.g., "creative")
- `style_config`: Style configuration with prompt_modifier, max_tokens, etc.
- `model`: OpenAI model name (e.g., "gpt-4o-mini")
- `temperature`: 0.0-2.0 (or style's temperature_override)

**Process**:
1. Build system prompt with style's `prompt_modifier`
2. Format filtered data as JSON string for context
3. Apply temperature override if style specifies it
4. Call OpenAI API with token limit from `max_tokens`
5. Return generated text or fallback message

**Example**:
```python
filtered = {"camera": {"location": [100, 200, 300]}, ...}
style_config = RESPONSE_STYLES["creative"]
description = generate_viewport_description(
    filtered, "creative", style_config, "gpt-4o-mini", 0.7
)
# Returns: "In the digital realm, the camera soars at..."
```

---

##### `test_openai_connection()`
```python
def test_openai_connection(model: str) -> Dict[str, Any]
```

**Purpose**: Verify OpenAI API connectivity

**Returns**:
```python
{"status": "success", "model": "gpt-4o-mini", "message": "..."}
# Or
{"status": "error", "error": "API key not configured"}
```

**Use Case**: `/ping_openai` endpoint for health checks

---

### filtering.py

**Purpose**: Intelligent data filtering based on response styles

#### Key Functions

##### `filter_viewport_data()`
```python
def filter_viewport_data(
    context: ViewportContext,
    filter_mode: str
) -> Dict[str, Any]
```

**Purpose**: Extract relevant viewport data based on filter mode

**Filter Modes**:

1. **minimal** (concise style)
   ```python
   {
       "camera": {"location": [...], "rotation": [...]},
       "selection": {"count": 1, "actors": [...]},
       "actors_summary": {"total": 47, "has_more": true}
   }
   ```
   - Camera always included
   - Selected objects (max 3)
   - Actor count only

2. **highlights** (natural style)
   ```python
   {
       "camera": {...},
       "selection": {...},
       "actors": {
           "total": 47,
           "notable": [...],  // selected + first 5 actors
           "types_summary": {"StaticMesh": 12, ...}
       },
       "lighting_summary": "present"  // if lights exist
   }
   ```
   - Notable elements only
   - Type summaries
   - Lighting presence indicator

3. **balanced** (balanced style)
   ```python
   {
       "camera": {...},
       "selection": {...},
       "actors": {
           "total": 47,
           "types": {"StaticMesh": 12, ...},
           "sample_names": [...]  // first 10
       },
       "lighting": {
           "directional_count": 2,
           "point_count": 5,
           "spot_count": 1
       },
       "environment": {
           "has_fog": true,
           "has_landscape": false
       }
   }
   ```
   - Key elements with summaries
   - Light counts instead of full details
   - Environment presence flags

4. **standard** (descriptive/creative styles)
   ```python
   {
       "camera": {...},
       "selection": {...},
       "actors": {
           "total": 47,
           "names": [...],  // first 15
           "types": {...}
       },
       "lighting": {...},  // full lighting data
       "environment": {
           "fog": [...],  // first 2
           "landscape": {...}
       }
   }
   ```
   - Good detail without overwhelming
   - Limited actor names
   - Full lighting details

5. **technical** (technical style)
   ```python
   {
       "camera": {...},
       "selection": {...},
       "actors": {...},  // all actors
       "lighting": {...},  // all lights
       "environment": {...},
       "metadata": {
           "actor_count": 47,
           "selected_count": 2,
           "lighting_count": 8
       }
   }
   ```
   - All data organized
   - Additional metadata section
   - Structured for technical docs

6. **complete** (detailed style)
   ```python
   {
       "camera": {...},
       "actors": {...},
       "selection": {...},
       "lighting": {...},
       "environment": {...},
       "additional_info": {...},  // if present
       "project_metadata": {...}  // if present
   }
   ```
   - Everything included
   - No filtering applied

**Performance Impact**:
- **minimal**: ~70% token reduction
- **highlights**: ~60% token reduction
- **balanced**: ~50% token reduction
- **standard**: ~30% token reduction
- **technical**: ~20% token reduction
- **complete**: 0% reduction (all data)

---

### conversation.py

**Purpose**: Conversation history management with file persistence

#### Key Functions

##### `add_to_history()`
```python
def add_to_history(
    user_input: str,
    response: str,
    command_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None
```

**Purpose**: Log conversation entry to memory and file

**Process**:
1. Create `ConversationEntry` with timestamp
2. Add to in-memory ring buffer (max 100 entries)
3. Append to `conversations.jsonl` in JSON Lines format
4. Handle file I/O errors gracefully

**Example**:
```python
add_to_history(
    "Describe viewport",
    "The camera is positioned at...",
    "describe_viewport",
    {"actors_count": 47, "has_selection": true}
)
```

---

##### `get_history()`
```python
def get_history(limit: int = 50) -> List[Dict[str, Any]]
```

**Purpose**: Retrieve recent conversation history

**Returns**: List of conversation dicts (most recent first)

---

##### `load_conversations()`
```python
def load_conversations() -> None
```

**Purpose**: Load conversation history from file on startup

**Process**:
1. Read `conversations.jsonl` line by line
2. Parse each JSON line
3. Add to in-memory buffer (last 100 entries)
4. Log count on success

**Called**: Automatically in `main.py` startup

---

##### `clear_history()`
```python
def clear_history() -> None
```

**Purpose**: Clear all conversation history

**Process**:
1. Clear in-memory ring buffer
2. Delete `conversations.jsonl` file
3. Raise exception on failure

---

#### Data Structure

**In-Memory**: Ring buffer (deque) with max 100 entries
```python
conversation_history = deque(maxlen=100)
```

**File Format**: JSON Lines (`.jsonl`)
```
{"timestamp": "...", "user_input": "...", "assistant_response": "...", "command_type": "...", "metadata": {...}}
{"timestamp": "...", "user_input": "...", "assistant_response": "...", "command_type": "...", "metadata": {...}}
```

**Benefits**:
- Append-only writes (fast)
- Line-by-line reading (memory efficient)
- Easy to parse and backup
- Survives server restarts

---

## Service Integration

### Dependency Flow

```
routes.py
    ↓
services/filtering.py → ViewportContext (models.py)
    ↓
services/openai_client.py → RESPONSE_STYLES (config.py)
    ↓
services/conversation.py → ConversationEntry (models.py)
```

### Error Handling

All services use try-except blocks with:
- Graceful degradation (fallback responses)
- Error logging to console
- Error metadata in conversation logs
- No crashes from service failures

### Testing Services

Services are designed for unit testing:
```python
# Example test
from app.services.filtering import filter_viewport_data
from app.models import ViewportContext

context = ViewportContext(
    camera={"location": [100, 200, 300]},
    actors={"total": 47, "names": ["Actor1"]}
)
filtered = filter_viewport_data(context, "minimal")
assert "camera" in filtered
assert "selection" in filtered
```

---

## Future Extensions

### Potential New Services

1. **caching.py** - Redis/in-memory response caching
2. **analytics.py** - Usage statistics and metrics
3. **validation.py** - Advanced input validation
4. **export.py** - Export conversations to PDF/CSV
5. **providers/anthropic.py** - Alternative AI provider support
