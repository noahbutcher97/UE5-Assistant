# Unreal Engine AI Viewport Assistant

## Overview
This project provides a FastAPI backend service that generates AI-powered technical documentation for Unreal Engine 5 editor viewport contexts. It receives structured viewport data from Unreal Engine's Python environment and uses OpenAI's GPT models to produce precise, factual prose descriptions of 3D scenes and level designs. The system aims to bridge Unreal Engine's scripting capabilities with cloud-based AI services, offering UE5 developers advanced insights and implementation guidance within their workflows. Key capabilities include context-aware implementation advice, Blueprint screenshot analysis, and secure file system interactions within the UE5 project.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
- **Interactive Settings Dashboard**: A web-based GUI `/dashboard` allows real-time configuration of AI model, response style presets, temperature, max context turns, and timeout controls. Settings persist to `config.json`.
- **Dark Theme Dashboard**: Features a sleek cyberpunk aesthetic with a dark navy background, cyan accents, and glass morphism cards.
- **Console Feedback**: Emoji-based status indicators in the Unreal Engine console for clarity.

### Technical Implementations
- **Backend Framework**: FastAPI for its async capabilities, automatic API documentation, and Pydantic-based type validation.
- **AI Integration**: Uses OpenAI GPT models (default: gpt-4o-mini) for technical prose generation, with configurable model selection and output style focused on factual documentation.
- **Data Flow**: Unreal Engine Python scripts collect viewport data and POST it to FastAPI endpoints. Pydantic models validate requests. AI processes data, and descriptions are returned to UE5.
- **UE5 Python Integration**: Automatic installation of dependencies, bi-directional HTTP communication, file-based state management (`Saved/AIConsole`), persistent conversation logging, and tokenized command routing.
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