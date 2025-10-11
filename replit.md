# Unreal Engine AI Viewport Assistant

## Overview

This is a FastAPI backend service that provides AI-powered technical documentation of Unreal Engine 5 editor viewport contexts. The system receives structured viewport data (camera position, rotation, visible actors, selected objects) from the Unreal Engine Python environment and uses OpenAI's GPT models to generate technical prose descriptions. This enables UE5 developers to get precise, factual feedback about their 3D scenes and level designs in structured technical documentation format.

The project is part of the UE5 AI Assistant Integration by Noah Butcher and is designed to bridge Unreal Engine's Python scripting capabilities with cloud-based AI services.

## Recent Changes

### October 11, 2025: File-Based Persistence & Dark Theme UI
- **File-Based Conversation Persistence**: Conversations now persist to `conversations.jsonl` using JSON Lines format. System automatically loads last 100 entries on startup (verified in logs: "[Startup] Loaded N conversations from file"). Each conversation appends to file in real-time, surviving server restarts
- **Clear History Feature**: New DELETE /api/conversations endpoint clears both in-memory history and persistent file. Settings tab includes "Clear All Conversations" button with confirmation dialog to prevent accidental data loss
- **Dark Theme Dashboard**: Complete UI transformation to sleek, technical cyberpunk aesthetic:
  - Dark navy background (#0a0e27) with subtle cyan grid pattern overlay for technical feel
  - Cyan accent color (#00f5ff) for all headers, highlights, borders with glowing shadows
  - Glass morphism design: translucent cards with backdrop-filter blur effects
  - All text colors optimized for dark theme readability (grays #94a3b8, #cbd5e1)
  - Monospace fonts for technical elements (timestamps, command types)
  - Interactive hover states with glowing effects on buttons and cards
  - Error/success states using dark-compatible colors (green #10b981, red #ef4444)
- **Enhanced API Documentation**: Updated API Info tab to include DELETE endpoint and improved formatting with color-coded syntax

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