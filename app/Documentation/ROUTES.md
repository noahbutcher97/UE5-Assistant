# API Routes Documentation

## Overview

All routes are defined in `app/routes.py` and registered with the FastAPI application. The API supports Unreal Engine 5.6 integration with AI-powered viewport descriptions.

## Endpoints

### Core Routes

#### `GET /`
**Purpose**: Redirect to dashboard  
**Response**: 307 redirect to `/dashboard`

---

#### `GET /health`
**Purpose**: Health check for monitoring  
**Response**:
```json
{
  "status": "online",
  "message": "UE5 AI Assistant running!",
  "version": "3.0"
}
```

---

#### `GET /test`
**Purpose**: Quick connectivity test  
**Response**:
```json
{
  "status": "ok",
  "message": "FastAPI test route reachable."
}
```

---

#### `GET /ping_openai`
**Purpose**: Verify OpenAI API connectivity  
**Response**:
```json
{
  "status": "success",
  "model": "gpt-4o-mini",
  "message": "OpenAI connection successful"
}
```
Or on error:
```json
{
  "status": "error",
  "error": "API key not configured"
}
```

---

### AI Processing Routes

#### `POST /execute_command`
**Purpose**: Handle general user commands with conversation context

**Request**:
```json
{
  "prompt": "What actors are in the scene?"
}
```

**Response**:
```json
{
  "response": "AI-generated response text"
}
```
Or:
```json
{
  "response": "[UE_REQUEST] describe_viewport"
}
```

**Behavior**:
- Maintains conversation history (max 6 turns)
- Recognizes tokenized commands: "viewport", "list actors", "selected"
- Returns `[UE_REQUEST] token` for UE-specific actions
- Logs to conversation history

**Recognized Patterns**:
- "what do i see", "viewport", "describe viewport" → `[UE_REQUEST] describe_viewport`
- "list actors", "list of actors" → `[UE_REQUEST] list_actors`
- "selected" + "info"/"details" → `[UE_REQUEST] get_selected_info`

---

#### `POST /describe_viewport`
**Purpose**: Generate technical description of UE5 viewport with intelligent filtering

**Request** (v2.0 structure):
```json
{
  "camera": {
    "location": [1200, -500, 450],
    "rotation": [15, 90, 0]
  },
  "actors": {
    "total": 47,
    "names": ["PlayerStart", "Cube_1", ...],
    "types": {"StaticMeshActor": 12, "PointLight": 3},
    "level": "TestLevel"
  },
  "lighting": {...},
  "environment": {...},
  "selection": {...},
  "project_metadata": {...}  // optional
}
```

**Response**:
```json
{
  "response": "AI-generated viewport description",
  "raw_context": {...}  // echoed input for debugging
}
```

**Processing Steps**:
1. Parse JSON into `ViewportContext` model
2. Get current `response_style` from config
3. Apply intelligent filtering based on style's `data_filter` mode
4. Generate AI description with style-specific prompt
5. Log to conversation history
6. Return description

**Filtering Modes** (based on response style):
- `minimal` (concise): Camera + selected only
- `highlights` (natural): Notable elements only
- `balanced`: Key elements with summaries
- `standard` (descriptive/creative): Good detail
- `technical`: Detailed but organized
- `complete` (detailed): Everything included

---

#### `POST /wrap_natural_language`
**Purpose**: Convert factual technical data into structured prose

**Request**:
```json
{
  "summary": "Camera: [100,200,300]. Actors: 47. Selected: Cube_1."
}
```

**Response**:
```json
{
  "response": "The viewport camera is positioned at coordinates (100, 200, 300). The scene contains 47 actors with Cube_1 currently selected."
}
```

**Use Case**: When UE5 has pre-formatted data that needs prose conversion

---

### Configuration Routes

#### `GET /api/config`
**Purpose**: Retrieve current configuration and available options

**Response**:
```json
{
  "config": {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "response_style": "descriptive",
    "max_context_turns": 6,
    ...
  },
  "defaults": {...},
  "response_styles": {
    "descriptive": {...},
    "technical": {...},
    ...
  },
  "available_models": [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-3.5-turbo"
  ]
}
```

---

#### `POST /api/config`
**Purpose**: Update configuration settings

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
- Accepts partial updates (only provided fields changed)
- Updates system message if `response_style` changed
- Persists to `config.json`
- Changes apply immediately

---

### Conversation Routes

#### `GET /api/conversations`
**Purpose**: Retrieve conversation history for dashboard

**Query Parameters**:
- `limit` (optional, default: 50): Number of recent conversations

**Response**:
```json
{
  "conversations": [
    {
      "timestamp": "2025-10-11T15:30:45.123Z",
      "user_input": "Describe viewport",
      "assistant_response": "The viewport shows...",
      "command_type": "describe_viewport",
      "metadata": {"actors_count": 47, "has_selection": true}
    },
    ...
  ],
  "total": 100,
  "max_size": 100
}
```

---

#### `DELETE /api/conversations`
**Purpose**: Clear all conversation history

**Response**:
```json
{
  "success": true,
  "message": "Conversation history cleared successfully"
}
```

**Behavior**:
- Clears in-memory ring buffer
- Deletes `conversations.jsonl` file
- Irreversible operation

---

#### `POST /api/log_conversation`
**Purpose**: Manually log a conversation entry (for UE5 client)

**Request**:
```json
{
  "timestamp": "2025-10-11T15:30:45.123Z",
  "user_input": "Test input",
  "assistant_response": "Test response",
  "command_type": "execute_command",
  "metadata": {"custom": "data"}
}
```

**Response**:
```json
{
  "status": "logged",
  "total_entries": 101
}
```

---

### Dashboard Route

#### `GET /dashboard`
**Purpose**: Serve interactive web dashboard

**Response**: HTML page with:
- Real-time conversation monitoring (auto-refresh every 3s)
- Configuration settings panel
- Response style selector
- Stats display
- API documentation tab

---

## Error Handling

All routes return errors in consistent format:

```json
{
  "error": "Error message description"
}
```

HTTP status codes:
- `200` - Success
- `307` - Redirect
- `400` - Bad request (invalid input)
- `500` - Server error (AI API failure, etc.)

## Authentication

Currently no authentication (single-user UE integration). For production deployment:
- Add API key authentication
- Implement rate limiting
- Add CORS restrictions
