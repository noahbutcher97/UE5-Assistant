# Configuration System

## Overview

The configuration system provides flexible, runtime-modifiable settings for the UE5 AI Assistant backend. Settings are stored in `config.json` and can be updated via API without server restart.

## Configuration Files

### config.py

**Location**: `app/config.py`

**Purpose**: Define response styles, defaults, and configuration logic

**Key Components**:

1. **RESPONSE_STYLES** - Dictionary of 7 response style presets
2. **DEFAULT_CONFIG** - Fallback configuration values
3. **load_config()** - Load from file or use defaults
4. **save_config()** - Persist configuration to disk

---

### config.json

**Location**: Root directory `config.json`

**Purpose**: Persistent storage of user preferences

**Format**:
```json
{
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_context_turns": 6,
  "timeout": 25,
  "max_retries": 3,
  "retry_delay": 2.5,
  "verbose": false,
  "response_style": "descriptive"
}
```

**Behavior**:
- Created automatically if missing
- Updated when settings change via API
- Merged with `DEFAULT_CONFIG` on load

---

## Response Styles

### Style Configuration Structure

Each response style defines:

```python
{
    "name": str,              # Display name
    "prompt_modifier": str,   # AI system prompt addition
    "max_tokens": int,        # Output token limit
    "data_filter": str,       # Filter mode to apply
    "temperature_override": float,  # Optional temp override
    "focus": str              # Focus area description
}
```

### Available Styles

#### 1. Descriptive (Default)
```python
"descriptive": {
    "name": "Descriptive (Default)",
    "prompt_modifier": "Provide clear, descriptive technical prose that explains what you see in the viewport. Be factual and specific.",
    "max_tokens": 400,
    "data_filter": "standard",
    "focus": "balanced_overview"
}
```
**Use Case**: Default general-purpose technical descriptions

---

#### 2. Technical
```python
"technical": {
    "name": "Technical/Precise",
    "prompt_modifier": "Use precise technical terminology with exact coordinates, transforms, and specifications. Structure as technical documentation with subsections.",
    "max_tokens": 500,
    "data_filter": "technical",
    "focus": "precision_and_specs"
}
```
**Use Case**: API documentation, technical specs, detailed analysis

---

#### 3. Natural
```python
"natural": {
    "name": "Natural/Conversational",
    "prompt_modifier": "Respond conversationally as if describing the scene to a colleague. Focus on what's interesting or notable. Skip mundane details.",
    "max_tokens": 300,
    "data_filter": "highlights",
    "focus": "notable_elements"
}
```
**Use Case**: Chat interfaces, casual descriptions, voice assistants

---

#### 4. Balanced
```python
"balanced": {
    "name": "Balanced",
    "prompt_modifier": "Balance technical accuracy with readability. Mention key actors and layout, skip repetitive details.",
    "max_tokens": 350,
    "data_filter": "balanced",
    "focus": "key_elements_summary"
}
```
**Use Case**: Mixed technical/non-technical audiences

---

#### 5. Concise
```python
"concise": {
    "name": "Concise/Brief",
    "prompt_modifier": "Be extremely brief. One short paragraph maximum. Only essential information: camera position, selected objects, major scene elements.",
    "max_tokens": 150,
    "data_filter": "minimal",
    "focus": "essentials_only"
}
```
**Use Case**: Quick status checks, mobile UIs, summaries

---

#### 6. Detailed
```python
"detailed": {
    "name": "Detailed/Verbose",
    "prompt_modifier": "Provide comprehensive, exhaustive analysis of all viewport elements. Include all actors, lighting setup, environment config, and spatial relationships.",
    "max_tokens": 800,
    "data_filter": "complete",
    "focus": "comprehensive_analysis"
}
```
**Use Case**: Debugging, comprehensive reports, documentation

---

#### 7. Creative
```python
"creative": {
    "name": "Creative/Imaginative",
    "prompt_modifier": "Paint a vivid picture using creative language and imagery. Help visualize the scene with descriptive metaphors, sensory details, and spatial storytelling. Structure as flowing narrative paragraphs that bring the viewport to life.",
    "max_tokens": 450,
    "temperature_override": 0.9,
    "data_filter": "standard",
    "focus": "visual_narrative"
}
```
**Use Case**: Marketing materials, visual storytelling, presentations

---

## Configuration Parameters

### Core Settings

#### model
- **Type**: string
- **Default**: `"gpt-4o-mini"`
- **Options**: `"gpt-4o-mini"`, `"gpt-4o"`, `"gpt-4-turbo"`, `"gpt-3.5-turbo"`
- **Purpose**: OpenAI model for text generation
- **Cost Impact**: gpt-4o more expensive but higher quality

---

#### temperature
- **Type**: float
- **Range**: 0.0 - 2.0
- **Default**: `0.7`
- **Purpose**: Controls AI creativity/randomness
- **Guidelines**:
  - `0.0-0.3`: Deterministic, factual
  - `0.4-0.7`: Balanced (recommended)
  - `0.8-1.0`: Creative, varied
  - `1.1-2.0`: Highly creative (experimental)

**Note**: `temperature_override` in response style takes precedence

---

#### response_style
- **Type**: string
- **Default**: `"descriptive"`
- **Options**: `"descriptive"`, `"technical"`, `"natural"`, `"balanced"`, `"concise"`, `"detailed"`, `"creative"`
- **Purpose**: Controls output format and filtering
- **Impact**: Changes prompt, token limit, and data filtering

---

#### max_context_turns
- **Type**: integer
- **Default**: `6`
- **Purpose**: Number of conversation turns to keep in memory
- **Behavior**: Keeps last N user/assistant pairs (2N total messages)
- **Memory Impact**: Higher values = more context = more tokens

---

#### timeout
- **Type**: integer (seconds)
- **Default**: `25`
- **Purpose**: OpenAI API request timeout
- **Recommended**: 20-30 seconds for reliable operation

---

#### max_retries
- **Type**: integer
- **Default**: `3`
- **Purpose**: Number of retry attempts on API failure
- **Behavior**: Exponential backoff with `retry_delay`

---

#### retry_delay
- **Type**: float (seconds)
- **Default**: `2.5`
- **Purpose**: Delay between retry attempts
- **Behavior**: Waits this long before retrying failed requests

---

#### verbose
- **Type**: boolean
- **Default**: `false`
- **Purpose**: Enable detailed console logging
- **Use Case**: Development and debugging

---

## API Configuration Endpoints

### GET /api/config

**Purpose**: Retrieve current configuration

**Response**:
```json
{
  "config": {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "response_style": "descriptive",
    ...
  },
  "defaults": {...},
  "response_styles": {...},
  "available_models": [...]
}
```

### POST /api/config

**Purpose**: Update configuration

**Request**:
```json
{
  "response_style": "creative",
  "temperature": 0.9
}
```

**Response**:
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "config": {...}
}
```

**Behavior**:
- Accepts partial updates (only specified fields)
- Validates values before applying
- Persists to `config.json`
- Updates system message if `response_style` changed
- Changes apply immediately (no restart needed)

---

## UE5 Client Synchronization

### UE5 Config Structure

**Location**: `attached_assets/AIAssistant/config.py`

**Purpose**: Mirror backend configuration in UE5 client

**RESPONSE_STYLES** must match backend exactly:
```python
RESPONSE_STYLES = {
    "descriptive": {
        "name": "Descriptive (Default)",
        "description": "...",
        "max_tokens": 400,
        "data_filter": "standard",
        "focus": "balanced_overview"
    },
    # ... must match backend
}
```

**Synchronization Process**:
1. Backend changes response style config
2. Manually update UE5 `config.py` to match
3. Both sides now use same filtering and prompts

**Critical**: Keep `max_tokens`, `data_filter`, `focus`, and `temperature_override` synchronized

---

## Environment Variables

### Required

#### OPENAI_API_KEY
- **Purpose**: OpenAI API authentication
- **Source**: Replit Secrets or environment
- **Validation**: Checked on startup and `/ping_openai`

### Optional

#### OPENAI_MODEL
- **Purpose**: Override default model
- **Default**: `"gpt-4o-mini"`
- **Behavior**: If set, overrides config.json model

---

## Configuration Best Practices

### Development
```json
{
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "response_style": "descriptive",
  "verbose": true,
  "timeout": 30
}
```

### Production
```json
{
  "model": "gpt-4o",
  "temperature": 0.6,
  "response_style": "technical",
  "verbose": false,
  "timeout": 20,
  "max_retries": 5
}
```

### Cost Optimization
```json
{
  "model": "gpt-4o-mini",
  "temperature": 0.5,
  "response_style": "concise",
  "max_context_turns": 3
}
```

### Creative Mode
```json
{
  "model": "gpt-4o",
  "temperature": 0.9,
  "response_style": "creative"
}
```

---

## Adding Custom Styles

1. **Add to backend** `app/config.py`:
```python
"my_custom_style": {
    "name": "My Custom Style",
    "prompt_modifier": "Custom instructions here...",
    "max_tokens": 350,
    "data_filter": "balanced",
    "focus": "custom_focus"
}
```

2. **Add to UE5** `attached_assets/AIAssistant/config.py`:
```python
"my_custom_style": {
    "name": "My Custom Style",
    "description": "User-facing description",
    "max_tokens": 350,
    "data_filter": "balanced",
    "focus": "custom_focus"
}
```

3. **Test via dashboard** or API:
```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"response_style": "my_custom_style"}'
```

---

## Configuration Validation

### Type Validation
- `temperature`: Must be float 0.0-2.0
- `max_context_turns`: Must be positive integer
- `response_style`: Must exist in RESPONSE_STYLES
- `model`: Must be valid OpenAI model

### Error Handling
```python
try:
    config = load_config()
except Exception:
    config = DEFAULT_CONFIG.copy()
    print("Using default configuration")
```

---

## Troubleshooting

### Config Not Loading
- Check `config.json` syntax (valid JSON)
- Verify file permissions (readable/writable)
- Check console for error messages
- Fallback: DELETE `config.json` to regenerate

### Changes Not Applied
- Restart server if `config.json` manually edited
- Use API endpoints for live updates
- Check response: `"success": true`

### Style Not Working
- Verify style exists in `RESPONSE_STYLES`
- Check UE5 config matches backend
- Confirm `data_filter` mode implemented
