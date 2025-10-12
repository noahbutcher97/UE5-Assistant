# Unreal Engine AI Viewport Assistant

## Overview
This project provides a FastAPI backend service that generates AI-powered technical documentation for Unreal Engine 5 editor viewport contexts. It receives structured viewport data from Unreal Engine's Python environment and uses OpenAI's GPT models to produce precise, factual prose descriptions of 3D scenes and level designs. The system aims to bridge Unreal Engine's scripting capabilities with cloud-based AI services, offering UE5 developers advanced insights and implementation guidance within their workflows. Key capabilities include **multi-project management** with browser-based project selection, **context-aware AI responses** using active project metadata, **UE 5.6 compliant utility generation**, **comprehensive editor orchestration** (scene building, camera control, actor manipulation), and **unified control dashboard** that serves as the main interface for all operations.

## File Structure & Deployment

### Replit Project Structure
```
Root/
├── main.py                                 # ⚙️ BACKEND: FastAPI entry point
├── app/                                    # ⚙️ BACKEND: FastAPI server modules
│   ├── models.py                           #    (Hosted on Replit cloud)
│   ├── routes.py
│   ├── config.py
│   ├── dashboard.py
│   └── services/
│       ├── openai_service.py
│       ├── conversation_service.py
│       └── filtering_service.py
│
├── attached_assets/
│   └── AIAssistant/                        # 🎮 UE5 CLIENT: Deploy to Unreal
│       ├── main.py                         #    (NOT imported by backend)
│       ├── config.py
│       ├── api_client.py
│       ├── context_collector.py
│       ├── action_executor.py
│       ├── project_metadata_collector.py
│       ├── blueprint_capture.py
│       └── Documentation/
│
└── ue5_client_tests/                       # 🧪 TESTING: Replit-only (DO NOT deploy)
    ├── mock_unreal.py
    ├── test_runner.py
    └── mock_project/
```

### Architecture Boundary Rules
**CRITICAL**: The backend and UE5 client are completely decoupled:
- ✅ **Backend** (`main.py` + `app/`): Never imports from `attached_assets/`
- ✅ **UE5 Client** (`attached_assets/AIAssistant/`): Only imported by UE5 Python environment
- ✅ **Communication**: HTTP API only (client POSTs to backend, receives JSON responses)
- ❌ **No direct module imports** between backend and client code

**Boundary Check**: Run `python3 check_imports.py` to verify backend isolation from UE5 client code

### Deployment Options

#### **🚀 Frictionless Deployment (Recommended)**
**One-time setup:**
1. Run Deploy Agent on your PC:
   - Download: [deploy_agent_installer.bat](https://ue5-assistant-noahbutcher97.replit.app/api/deploy_agent_installer)
   - Double-click to run (enters your UE5 project path)
   - Keep window open while using dashboard

2. Use Dashboard:
   - Go to [Control Center](https://ue5-assistant-noahbutcher97.replit.app/dashboard)
   - Enter project path
   - Click **"⚡ Instant Deploy & Run"**
   - Files deployed + auto-imported in UE5 instantly!

**Features:** Zero manual steps, auto-import in UE5, project registration, instant readiness

#### **Classic Deployment Options**
- **PowerShell Installer:** Download and run [install_ue5_assistant.ps1](https://ue5-assistant-noahbutcher97.replit.app/api/installer_script)
- **Manual ZIP:** Download from [dashboard](https://ue5-assistant-noahbutcher97.replit.app/dashboard), extract to `Content/Python/`
- **UE5 Auto-Update:** Run `import AIAssistant.auto_update; AIAssistant.auto_update.check_and_update()` in UE5 console

**Backend:** FastAPI server runs on Replit at `https://ue5-assistant-noahbutcher97.replit.app`

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
- **Unified Control Center**: The main `/dashboard` now features a unified interface with Project Hub as the primary tab, alongside Conversations, Settings, API Info, and About tabs.
- **Project Selector**: Browser-based dropdown for selecting active UE5 project, with real-time connection status indicator.
- **Dark Theme Dashboard**: Sleek cyberpunk aesthetic with dark navy background, cyan accents, and glass morphism cards.
- **Console Feedback**: Emoji-based status indicators in the Unreal Engine console for clarity.

### Technical Implementations
- **Backend Framework**: FastAPI for its async capabilities, automatic API documentation, and Pydantic-based type validation.
- **AI Integration**: Uses OpenAI GPT models (default: gpt-4o-mini) for technical prose generation, with configurable model selection and output style.
- **Multi-Project Registry**: Backend tracks multiple UE5 projects with metadata, allowing browser-based project selection and context-aware queries.
- **Auto-Registration**: UE5 client automatically registers projects on startup, uploading metadata (blueprints count, modules, file structure) to backend.
- **Context-Aware Queries**: Project queries enriched with active project context for accurate, project-specific AI responses.
- **Editor Orchestration Systems**: Complete scene building via SceneOrchestrator (spawn actors/primitives/blueprints), ViewportController (camera control), and ActorManipulator (align/distribute/arrange).
- **UE 5.6 Compliant Utility Generator**: Generates Editor Utility Widgets with proper @unreal.uclass() decorators, EditorUtilityWidget base class, @unreal.ufunction methods, and full backend API integration.
- **Unified Dashboard**: Main interface at `/dashboard` with Project Hub as primary tab, replacing separate dashboard pages.
- **Deploy Agent**: Local Python service (localhost:7865) bridges browser to UE5, enabling frictionless deployment and auto-import without browser security limitations.
- **Data Flow**: Unreal Engine Python scripts collect viewport data and POST it to FastAPI endpoints. Pydantic models validate requests. AI processes data, and descriptions are returned to UE5.
- **UE5 Python Integration**: Automatic installation of dependencies, bi-directional HTTP communication, file-based state management (`Saved/AIConsole`), persistent conversation logging, and intelligent context-aware command routing with expanded keyword detection.
- **Context-Aware Command Routing**: Backend intelligently detects user intent and routes context-specific queries (project info, blueprint capture, file browsing) to appropriate UE5 data collection actions while maintaining AI-powered responses for general guidance questions.
- **Configuration System**: JSON-based config with GET/POST `/api/config` endpoints. Settings dynamically affect runtime behavior without server restarts.
- **Modular Architecture**: Backend refactored into `app/` package with dedicated modules for models, config, routes, services (OpenAI, filtering, conversation), and dashboard. UE5 client also uses a modular design for API client, context collection, action execution, and UI management.
- **File System Operations**: Secure read-only file browsing using `Path.relative_to()` for path validation. UE5 client uses `unreal.Paths` for project directory navigation and file searching.
- **Project Intelligence Gathering**: `project_metadata_collector.py` extracts comprehensive project data (modules/plugins, asset counts, Blueprint statistics, source code analysis, content folder structure) with caching.
- **Blueprint Screenshot Capture**: Multi-modal vision support; captures Blueprint editor screenshots, uploads base64 images to OpenAI Vision API (gpt-4o), and stores them with metadata.
- **Enhanced Action Executor**: Includes actions for file browsing, reading, searching, project info display, blueprint capture, and listing blueprints, all feature-flag protected.
- **Feature Flag System**: Granular control over features like file operations, guidance requests, and blueprint capture via configuration flags.
- **UE5 Mock Testing Environment**: `mock_unreal.py` simulates UE5 editor for Replit-based testing, ensuring client code validation without an active UE5 instance.
- **Server Selection System**: UE5 config supports switching between production, development, and localhost servers, with selection persisting across sessions.
- **File Communication Protocol**: Standardized file I/O for Blueprint integration, where Python writes to `[Project]/Saved/AIConsole/*.txt` for Blueprint to read.

### System Design Choices
- **RESTful API**: Standard HTTP methods with JSON payloads for client-server communication.
- **Separation of Concerns**: UE viewport collection logic is isolated from the AI processing backend.
- **Environment-based Configuration**: Sensitive data and configurable parameters are externalized via environment variables.
- **Error Handling**: Structured error logging, retry logic, graceful degradation, and console feedback.
- **Thread Safety**: Synchronous mode by default in UE5 integration to avoid "Attempted to access Unreal API from outside the main game thread" errors.
- **Security Hardening**: Path traversal protection and enforcement of read-only file operations.
- **UE5.6 API Compliance**: All UE5 client code verified against Epic Games official documentation.

## External Dependencies

### AI Services
- **OpenAI API** (v1.57.0): Used for GPT model access (e.g., gpt-4o-mini, gpt-4o) for technical prose generation and multi-modal vision analysis. Requires `OPENAI_API_KEY` environment variable.

### Python Packages (Backend)
- **fastapi** (0.112.x): Core web framework.
- **uvicorn** (0.23.2): ASGI server.
- **pydantic** (2.10.3+): Data validation and settings management.
- **openai** (1.57.0): Official OpenAI Python client.
- **requests** (2.32.3): HTTP library.
- **jinja2** (3.1.4): Template engine.

### Unreal Engine Integration
- **UE5.6+ Python API** (3.11.8): Native Python environment for editor interactions, viewport querying, and file system operations (`unreal.Paths`).
- **pip**: Package manager for installing Python dependencies within UE's environment.

### Deployment Platform
- **Replit**: Hosting platform for the FastAPI backend.
  - Base URL: `https://ue5-assistant-noahbutcher97.replit.app`

### Communication Protocol
- **HTTP/HTTPS**: For REST API communication between UE5 client and FastAPI backend.
- **JSON**: Data serialization format.
- **File I/O**: Local file storage within UE project directories for conversation logs and responses.