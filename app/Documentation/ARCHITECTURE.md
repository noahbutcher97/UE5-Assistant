# Backend Architecture - UE5 AI Assistant v3.0

## Overview

The UE5 AI Assistant backend is a modular FastAPI application designed to receive viewport context from Unreal Engine 5.6 and generate AI-powered technical descriptions using OpenAI's GPT models.

## Architecture Pattern

**Layered Architecture with Dependency Injection**

```
main.py (Application Factory)
    │
    ├── app/config.py (Configuration Layer)
    ├── app/models.py (Data Layer)
    ├── app/routes.py (Presentation Layer)
    └── app/services/ (Business Logic Layer)
        ├── openai_client.py
        ├── filtering.py
        └── conversation.py
```

## Core Principles

### 1. Separation of Concerns
- **Configuration**: Isolated in `config.py` with file persistence
- **Data Models**: Pydantic models in `models.py` for type safety
- **Business Logic**: Services layer handles AI integration and data processing
- **API Layer**: Routes define HTTP endpoints and orchestrate services

### 2. Modular Design
Each module has a single, well-defined responsibility:
- `config.py` - Configuration management
- `models.py` - Data validation and serialization
- `routes.py` - HTTP request handling
- `services/openai_client.py` - OpenAI API integration
- `services/filtering.py` - Intelligent data filtering
- `services/conversation.py` - Conversation history management

### 3. Scalability
- Stateless design (except conversation history for single-user UE integration)
- Async-capable with FastAPI's native support
- Easy to add new response styles or filtering modes
- Extensible services layer for new AI providers

## Request Flow

```
UE5 Client
    ↓
FastAPI Routes (routes.py)
    ↓
Data Validation (models.py)
    ↓
Intelligent Filtering (services/filtering.py)
    ↓
AI Processing (services/openai_client.py)
    ↓
Response + Logging (services/conversation.py)
    ↓
JSON Response to UE5
```

## Key Features

### Intelligent Data Filtering
Backend applies style-aware filtering before AI processing:
- **Minimal** (concise): Camera + selected objects only
- **Highlights** (natural): Notable elements only
- **Balanced**: Key elements with summaries
- **Standard** (descriptive/creative): Good detail without overwhelming
- **Technical**: Detailed but organized
- **Complete** (detailed): Everything included

### Response Style System
7 distinct response styles with unique:
- Prompt modifiers
- Token limits (150-800)
- Temperature overrides (creative uses 0.9)
- Data filter modes
- Focus areas

### Conversation Persistence
- In-memory ring buffer (100 entries)
- JSON Lines file persistence (`conversations.jsonl`)
- Automatic loading on startup
- Real-time append for durability

## File Structure

```
app/
├── __init__.py
├── config.py              # Configuration with 7 response styles
├── models.py              # Pydantic data models
├── routes.py              # FastAPI endpoints
├── dashboard.py           # Web dashboard HTML generation
├── services/
│   ├── __init__.py
│   ├── openai_client.py   # OpenAI API integration
│   ├── filtering.py       # Style-aware data filtering
│   └── conversation.py    # Conversation history
└── Documentation/
    ├── ARCHITECTURE.md    # This file
    ├── MODELS.md          # Data models documentation
    ├── ROUTES.md          # API endpoints documentation
    ├── SERVICES.md        # Services layer documentation
    ├── FILTERING.md       # Filtering system documentation
    └── CONFIGURATION.md   # Configuration documentation
```

## Technology Stack

- **FastAPI** - Modern async web framework
- **Pydantic v2** - Data validation and serialization
- **OpenAI API** - GPT models for text generation
- **Uvicorn** - ASGI server
- **Python 3.11** - Matches UE5.6 Python environment

## Design Patterns Used

1. **Factory Pattern** - `main.py` acts as application factory
2. **Dependency Injection** - Services passed to routes
3. **Strategy Pattern** - Different filtering strategies per response style
4. **Repository Pattern** - Conversation persistence abstraction
5. **Singleton Pattern** - Global app configuration

## Extension Points

### Adding New Response Styles
1. Add style config to `RESPONSE_STYLES` in `config.py`
2. Update UE5 `config.py` to match
3. No code changes needed - filtering is data-driven

### Adding New Filtering Modes
1. Add filter mode to `filter_viewport_data()` in `services/filtering.py`
2. Reference in response style config

### Adding New AI Providers
1. Create new service module in `services/`
2. Implement same interface as `openai_client.py`
3. Update routes to use new service

## Performance Considerations

- **Token Optimization**: Filtering reduces AI tokens by 30-70% depending on style
- **Caching**: Response styles cached in memory
- **Async Operations**: Non-blocking I/O for concurrent requests
- **Minimal Dependencies**: Lightweight footprint

## Security

- API keys managed via environment variables
- No secrets in code or logs
- Input validation via Pydantic models
- CORS configured for UE5 client access
