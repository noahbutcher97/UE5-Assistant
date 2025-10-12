# Unreal Engine AI Viewport Assistant

## Overview
This project delivers a FastAPI backend service for generating AI-powered technical documentation of Unreal Engine 5 editor viewport contexts. It processes structured viewport data from Unreal Engine's Python environment to produce precise, factual descriptions of 3D scenes and level designs using OpenAI's GPT models. The system aims to enhance UE5 developers' workflows by offering advanced insights and implementation guidance. Key features include multi-project management, context-aware AI responses, UE 5.6 compliant utility generation, comprehensive editor orchestration (scene building, camera control, actor manipulation), and a unified control dashboard. The project seeks to bridge Unreal Engine's scripting capabilities with cloud-based AI services.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
- **Unified Control Center**: A single `/dashboard` interface with Project Hub as the primary tab, alongside Conversations, Settings, API Info, and About.
- **Project Selector**: Browser-based dropdown for active UE5 project selection with real-time connection status.
- **Dark Theme Dashboard**: A cyberpunk aesthetic featuring a dark navy background, cyan accents, and glass morphism cards.
- **Console Feedback**: Emoji-based status indicators in the Unreal Engine console for clarity.

### Technical Implementations
- **Backend Framework**: FastAPI is used for its async capabilities, automatic API documentation, and Pydantic-based type validation.
- **AI Integration**: Utilizes OpenAI GPT models (default: gpt-4o-mini) for technical prose generation and multi-modal vision analysis, with configurable model selection.
- **Multi-Project Registry**: The backend manages multiple UE5 projects and their metadata, enabling browser-based project selection and context-aware queries.
- **Auto-Registration**: The UE5 client automatically registers projects upon startup, uploading metadata such as blueprint counts, modules, and file structure.
- **Context-Aware Queries**: Project-specific queries are enriched with active project context for accurate AI responses.
- **Editor Orchestration Systems**: Includes SceneOrchestrator for scene building (actors, primitives, blueprints), ViewportController for camera control, and ActorManipulator for object alignment and arrangement.
- **UE 5.6 Compliant Utility Generator**: Generates Editor Utility Widgets with appropriate decorators and API integration.
- **Real-Time WebSocket Communication**: A bidirectional WebSocket system allows the dashboard to trigger UE5 actions directly and collect live data, featuring automatic reconnection and robust error handling.
- **Deploy Agent**: A local Python service (localhost:7865) facilitates frictionless deployment and auto-import into UE5.
- **Data Flow**: UE Python scripts collect viewport data and POST it to FastAPI endpoints for AI processing, with results returned to UE5.
- **Context-Aware Command Routing**: The backend intelligently routes user intent for context-specific queries (e.g., project info, blueprint capture) to appropriate UE5 data collection actions, complementing AI-powered general guidance.
- **Configuration System**: JSON-based configuration with dynamic runtime effects via GET/POST `/api/config` endpoints.
- **Modular Architecture**: Backend is organized into an `app/` package, and the UE5 client also follows a modular design.
- **File System Operations**: Secure, read-only file browsing using `Path.relative_to()` for validation, and `unreal.Paths` for UE project navigation.
- **Project Intelligence Gathering**: `project_metadata_collector.py` collects comprehensive project data, including modules, plugins, asset counts, Blueprint statistics, and source code analysis, with caching.
- **Blueprint Screenshot Capture**: Supports capturing Blueprint editor screenshots, uploading base64 images to OpenAI Vision API (gpt-4o), and storing them with metadata.
- **Enhanced Action Executor**: Provides actions for file browsing, reading, searching, project info display, blueprint capture, and listing blueprints, all protected by feature flags.
- **Feature Flag System**: Granular control over features like file operations, guidance requests, and blueprint capture.
- **UE5 Mock Testing Environment**: `mock_unreal.py` allows Replit-based testing of client code without an active UE5 instance.
- **Server Selection System**: UE5 configuration supports switching between production, development, and localhost servers.
- **File Communication Protocol**: Standardized file I/O for Blueprint integration via `[Project]/Saved/AIConsole/*.txt`.

### System Design Choices
- **RESTful API**: Standard HTTP methods with JSON payloads for client-server communication.
- **Separation of Concerns**: UE viewport collection logic is isolated from the AI processing backend.
- **Environment-based Configuration**: Sensitive data and configurable parameters are managed via environment variables.
- **Error Handling**: Includes structured logging, retry logic, graceful degradation, and console feedback.
- **Thread Safety**: UE5 integration operates in synchronous mode to prevent threading issues.
- **Security Hardening**: Path traversal protection and enforcement of read-only file operations.
- **UE5.6 API Compliance**: All UE5 client code adheres to Epic Games' official documentation.

## External Dependencies

### AI Services
- **OpenAI API** (v1.57.0): Used for GPT model access (e.g., gpt-4o-mini, gpt-4o) for technical prose generation and multi-modal vision analysis. Requires `OPENAI_API_KEY`.

### Python Packages (Backend)
- **fastapi** (0.112.x): Core web framework.
- **uvicorn** (0.23.2): ASGI server.
- **websockets** (15.0.1): WebSocket protocol support.
- **pydantic** (2.10.3+): Data validation and settings management.
- **openai** (1.57.0): Official OpenAI Python client.
- **requests** (2.32.3): HTTP library.
- **jinja2** (3.1.4): Template engine.

### Unreal Engine Integration
- **UE5.6+ Python API** (3.11.8): Native Python environment for editor interactions.
- **websocket-client**: Python WebSocket client library for UE5.
- **pip**: Package manager for installing Python dependencies within UE's environment.

### Deployment Platform
- **Replit**: Hosting platform for the FastAPI backend.
  - Base URL: `https://ue5-assistant-noahbutcher97.replit.app`

### Communication Protocol
- **HTTP/HTTPS**: For REST API communication.
- **JSON**: Data serialization format.
- **File I/O**: Local file storage within UE project directories for conversation logs and responses.

## Testing & Quality Assurance

### One-Click Update System
- **Dashboard Feature**: "🔄 Update All Clients" button provides one-click deployment to all connected UE5 projects
- **WebSocket-Based**: Sends auto-update commands via WebSocket to bypass Replit CDN caching
- **CDN-Proof**: Uses POST `/api/download_client_bundle` endpoint which never gets cached
- **Real-Time Feedback**: Visual button states (⏳ Updating, ✅ Updated, ❌ Failed) and success/error alerts
- **Auto-Reload**: UE5 clients automatically reload AIAssistant module after update

### Automated Test Suite
- **Test File**: `test_auto_update.py` - Comprehensive testing without requiring UE5
- **Test Coverage**:
  - ✅ Module import validation
  - ✅ Backend URL configuration
  - ✅ Safe logging in non-UE5 environment  
  - ✅ Version checking
  - ✅ Update prevention (safety check)
  - ✅ Download endpoint verification (localhost)
  - ✅ ZIP integrity and contents validation
- **Results**: 5/7 core tests pass (Replit proxy limitation prevents POST testing on deployed URL, but localhost confirms functionality)
- **Usage**: `python test_auto_update.py`

### Documentation
- **User Guide**: `HOW_TO_USE_UPDATE_BUTTON.md` - Complete instructions for using the update feature
- **Technical Details**: Architecture, WebSocket message format, security features, troubleshooting