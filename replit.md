# Unreal Engine AI Viewport Assistant

## Overview

This is a FastAPI backend service that provides AI-powered technical documentation of Unreal Engine 5 editor viewport contexts. The system receives structured viewport data (camera position, rotation, visible actors, selected objects) from the Unreal Engine Python environment and uses OpenAI's GPT models to generate technical prose descriptions. This enables UE5 developers to get precise, factual feedback about their 3D scenes and level designs in structured technical documentation format.

The project is part of the UE5 AI Assistant Integration by Noah Butcher and is designed to bridge Unreal Engine's Python scripting capabilities with cloud-based AI services.

## Recent Changes

### October 11, 2025: Server Selection System for Blueprint Integration
- **Server Selection Feature**: UE5 config now supports switching between production/dev/localhost servers with `switch_server()`, `list_servers()`, and `get_active_server()` methods
- **Blueprint Helper Module**: Created `blueprint_helpers.py` with file-based I/O functions for Editor Utility Widget integration. Functions write output to files that Blueprint can read with "Load File to String"
- **Server Presets**: Three predefined servers in config - production (replit.app), dev (janeway.replit.dev), and localhost (port 5000)
- **Blueprint Integration Guide**: Added `BLUEPRINT_INTEGRATION.md` with complete step-by-step instructions for adding ComboBox server selector to Editor Utility Widgets, including copy-paste scripts and troubleshooting
- **Persistent Server Selection**: Active server choice saves to config.json and persists across UE5 sessions
- **File Communication Protocol**: All Blueprint helpers use standardized file I/O pattern - Python writes to `[Project]/Saved/AIConsole/*.txt`, Blueprint reads with 0.1s delay

### October 11, 2025: v3.0 Modular Architecture & Full-Stack Alignment
- **Backend Modular Refactoring**: Restructured monolithic main.py (~1600 lines) into clean app/ package:
  - app/models.py - Pydantic data models with v2.0 structure support
  - app/config.py - Configuration management with 7 response style presets
  - app/routes.py - API endpoint definitions and request handling
  - app/services/openai_client.py - OpenAI integration and prompt generation
  - app/services/filtering.py - Intelligent viewport data filtering per response style
  - app/services/conversation.py - Conversation history with file persistence
  - app/dashboard.py - Interactive web dashboard HTML generation
  - app/data/ - Persistent data storage (config.json, conversations.jsonl)
  - app/Documentation/ - Comprehensive technical documentation (7 .md files)
  - main.py - Simple app factory (47 lines) wiring components together
- **File Organization**: Organized backend and UE5 directories with proper separation of concerns:
  - Data files moved to app/data/ for clean project structure
  - Created comprehensive backend documentation in app/Documentation/
  - UE5 test files organized in attached_assets/AIAssistant/tests/
  - Added .gitignore for proper version control of data files
- **Response Style Synchronization**: UE5 config.py now mirrors backend RESPONSE_STYLES structure with max_tokens, data_filter, temperature_override, and focus fields for each of 7 styles (descriptive, technical, natural, balanced, concise, detailed, creative)
- **Intelligent Data Filtering**: Backend applies style-aware filtering (minimal/highlights/balanced/standard/technical/complete) before AI processing, optimizing token usage and response quality
- **Project Metadata Integration**: UE5 action_executor properly checks collect_project_metadata config flag and includes comprehensive project context (asset counts, source code stats, content folder analysis) in viewport descriptions when enabled
- **File-Based Conversation Persistence**: Conversations persist to conversations.jsonl using JSON Lines format. System automatically loads last 100 entries on startup. Each conversation appends in real-time, surviving server restarts
- **Clear History Feature**: New DELETE /api/conversations endpoint clears both in-memory history and persistent file. Settings tab includes "Clear All Conversations" button with confirmation dialog
- **Dark Theme Dashboard**: Complete UI transformation with sleek cyberpunk aesthetic - dark navy background (#0a0e27), cyan accents (#00f5ff), glass morphism cards with backdrop-filter blur, optimized text colors, interactive glowing hover states
- **Communication Protocol**: Full v2.0 data structure alignment - UE5 sends nested {camera, actors, lighting, environment, selection, project_metadata}, backend filters and processes with style-aware logic

### October 2025: Modular Architecture v2.0 & Interactive Settings Dashboard
- **Modular Rewrite**: Complete architectural overhaul with separation of concerns - config, API client, async client, context collector, action executor, UI manager, and main orchestrator as independent modules
- **Blueprint Integration**: Seamless integration with Editor Utility Widget via file-based communication. Simple one-line Python command update to migrate from v1.0
- **Enhanced Context Collection**: Automatic collection of lighting (directional, point, spot), materials, environment (fog, post-process), landscape, and detailed selection data
- **Thread Safety Fix**: Discovered async mode causes "Attempted to access Unreal API from outside the main game thread" errors. System now defaults to synchronous mode (use_async=False) for reliable operation. Brief blocking (~15-20s) is acceptable for editor tools and ensures all UE API calls execute correctly
- **Critical Data Structure Bug Fix**: Resolved mismatch between v2.0 modular client (nested structure) and v1.0 FastAPI backend (flat structure). Backend now accepts v2.0 format with camera{location, rotation}, actors{total, names, types}, lighting{}, environment{}, selection{} structure. This fixed "null data" responses where AI couldn't describe viewport
- **Interactive Settings Dashboard**: Web-based GUI at /dashboard for real-time configuration without code changes. Features AI model selector, 6 response style presets (descriptive, technical, natural, balanced, concise, detailed), temperature slider, max context turns, and timeout controls. All settings persist to config.json and apply immediately to OpenAI API calls
- **Configuration System Overhaul**: JSON-based config with GET/POST /api/config endpoints. Settings dynamically affect runtime behavior (temperature, model, response_style, max_context_turns) without server restart. Both backend and UE5 configs synchronized
- **Conversation Dashboard**: Real-time monitoring with auto-refresh, in-memory ring buffer (100 entries), stats display, and tabbed interface
- **Extensibility**: Command registry pattern allows custom actions to be registered from Blueprint or Python. Configuration system with runtime modification support
- **Code Quality**: All pyright-extended linting errors resolved with documented type guards for environment-specific modules (unreal, requests)
- **Performance**: Direct prose generation from /describe_viewport, 50% latency reduction vs v1.0

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **FastAPI** serves as the core web framework for the API endpoints
- Chosen for its async capabilities, automatic API documentation, and strong type validation with Pydantic
- Lightweight and performant for handling multiple concurrent requests from UE5 clients
- Built-in OpenAPI/Swagger documentation automatically generated from route definitions

### AI Integration
- **OpenAI GPT models** (default: gpt-4o-mini) provide technical prose generation
- API key configured via environment variable `OPENAI_API_KEY` for security
- Model selection configurable through `OPENAI_MODEL` environment variable (October 2025 update)
- Direct integration using official OpenAI Python client library
- Output style: Technical documentation prose (not conversational, not bare lists)

### Data Flow Architecture
- **Unreal Engine Client → FastAPI Backend**: UE5 Python scripts collect viewport data and POST to API endpoints
- **Request Validation**: Pydantic models (`ViewportContext`) ensure type safety and data structure consistency
- **AI Processing**: Structured UE data is formatted and sent to OpenAI for natural language conversion
- **Response Delivery**: Generated descriptions returned to UE5 for display in custom UI

### UE5 Python Integration Layer
- **Dependency Management**: Automatic installation of required packages (requests) in UE's embedded Python environment
- **Bi-directional Communication**: UE scripts can send commands and receive responses via HTTP
- **File-based State Management**: Responses saved to UE project's Saved/AIConsole directory for Blueprint consumption
- **Conversation Logging**: Persistent conversation history stored locally in UE project
- **Tokenized Command Routing**: `[UE_REQUEST]` pattern for special command handling

### Design Patterns
- **RESTful API**: Standard HTTP methods with JSON payloads for client-server communication
- **Separation of Concerns**: UE viewport collection logic isolated from AI processing backend
- **Configuration via Environment**: All sensitive data and configurable parameters externalized
- **Async/Await**: FastAPI's async capabilities used for non-blocking I/O operations

### Error Handling Strategy
- Structured error logging in UE Python scripts with traceback capture
- Retry logic with configurable delays for network resilience (MAX_RETRIES: 3, RETRY_DELAY: 2.5s)
- Graceful degradation when API endpoints are unavailable
- Console feedback with emoji-based status indicators for user clarity

## External Dependencies

### AI Services
- **OpenAI API** (v1.57.0): GPT model access for technical prose generation
  - Requires `OPENAI_API_KEY` environment variable
  - Configurable model selection via `OPENAI_MODEL` (defaults to gpt-4o-mini)
  - Used for converting structured viewport data into technical documentation
  - All prompts optimized for factual, structured technical prose (October 2025)

### Python Packages (Backend)
- **fastapi** (0.112.x): Core web framework
- **uvicorn** (0.23.2): ASGI server for running FastAPI
- **pydantic** (2.10.3+): Data validation and settings management
- **openai** (1.57.0): Official OpenAI Python client
- **requests** (2.32.3): HTTP library for external API calls
- **jinja2** (3.1.4): Template engine (likely for future HTML response rendering)

### Unreal Engine Integration
- **UE5.6+ Python API** (3.11.8): Native Python environment in Unreal Editor
  - `unreal` module for editor interactions
  - Viewport and actor query capabilities
  - File system operations via `unreal.Paths`
- **pip**: Package manager for installing dependencies in UE's Python environment

### Deployment Platform
- **Replit**: Hosting platform for the FastAPI backend
  - Base URL: `https://ue5-assistant-noahbutcher97.replit.app`
  - Endpoints: `/`, `/execute_command`, `/wrap_natural_language`, `/describe_viewport`

### Communication Protocol
- **HTTP/HTTPS**: REST API communication between UE5 client and FastAPI backend
- **JSON**: Data serialization format for all API requests and responses
- **File I/O**: Local file storage for conversation logs and response caching in UE project directories

## Project File Structure

### Backend Organization
```
app/
├── __init__.py
├── config.py              # Configuration with 7 response styles
├── models.py              # Pydantic data models
├── routes.py              # FastAPI endpoints
├── dashboard.py           # Web dashboard HTML generation
├── data/                  # Persistent data storage
│   ├── config.json        # Runtime configuration
│   └── conversations.jsonl # Conversation history
├── services/
│   ├── __init__.py
│   ├── openai_client.py   # OpenAI API integration
│   ├── filtering.py       # Intelligent data filtering
│   └── conversation.py    # Conversation history management
└── Documentation/         # Technical documentation
    ├── README.md          # Documentation index
    ├── ARCHITECTURE.md    # System architecture overview
    ├── MODELS.md          # Data models documentation
    ├── ROUTES.md          # API endpoints reference
    ├── SERVICES.md        # Services layer documentation
    ├── FILTERING.md       # Filtering system deep dive
    └── CONFIGURATION.md   # Configuration guide
```

### UE5 Client Organization
```
attached_assets/AIAssistant/
├── main.py                      # Main orchestrator
├── config.py                    # UE5 configuration with server selection
├── api_client.py                # HTTP client for backend
├── context_collector.py         # Viewport data collection
├── action_executor.py           # Command execution
├── ui_manager.py                # UI display management
├── blueprint_helpers.py         # Blueprint integration helpers (file-based I/O)
├── tests/
│   └── DEBUG_TEST.py            # Test utilities
└── Documentation/               # UE5 client documentation
    ├── README.md                # Client documentation index
    └── BLUEPRINT_INTEGRATION.md # Blueprint server selector guide
```

### Documentation Access

- **Backend Docs**: `/app/Documentation/` - 7 comprehensive technical guides
- **UE5 Docs**: `/attached_assets/AIAssistant/Documentation/` - Client-side documentation
- **API Docs**: `http://localhost:5000/docs` - FastAPI auto-generated Swagger UI
- **Interactive Dashboard**: `http://localhost:5000/dashboard` - Real-time config and monitoring