# Unreal Engine AI Viewport Assistant

## Overview
This project provides a FastAPI-based backend service to generate AI-powered technical documentation for Unreal Engine 5 editor viewport contexts. It processes UE5 viewport data using OpenAI's GPT models to create accurate descriptions of 3D scenes and level designs, enhancing developer workflows with advanced insights and implementation guidance. Key capabilities include multi-project management, context-aware AI responses, UE 5.6 compliant utility generation, comprehensive editor orchestration (scene building, camera control, actor manipulation), and a unified control dashboard. The project aims to bridge Unreal Engine's scripting capabilities with cloud-based AI to boost developer productivity and foster innovative game development.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
The system features a **Unified Control Center** (`/dashboard`) with dedicated sections for project management, live feeds, AI intelligence, guidance, tools, settings, and diagnostics. It employs a **Modern Design System** using the Inter font, a refined spacing system, professional aesthetics, subtle animations, and softer shadows. The **Tools Tab** offers AI-powered widget generation with automated class name sanitization. Key UI/UX elements include a browser-based **Project Selector** with real-time connection status, enhanced visuals, quality-of-life features (keyboard shortcuts, tooltips, one-click copy buttons, visual feedback), and a **Responsive** design for mobile and touch devices.

### Technical Implementations
The backend is built with **FastAPI** for async capabilities and Pydantic validation. **AI Integration** leverages OpenAI GPT models (default: gpt-4o-mini) for technical prose generation and multi-modal vision analysis. It includes a **Multi-Project Registry** for managing UE5 projects with browser-based selection and **Auto-Registration**. **Context-Aware Queries** enhance AI responses using active project data. **Editor Orchestration Systems** (SceneOrchestrator, ViewportController, ActorManipulator) facilitate scene building, camera control, and actor manipulation.

A **Fully Automated Widget Generator** creates AI-powered Editor Utility Widgets, generating UE 5.6 Python scripts that the backend queues for local writing in UE5. **Persistent Operation & Event History** is maintained via bounded FIFO lists and displayed in the Live Feed. A **Server Switching System** provides granular control over backend endpoints for connected clients.

**Real-Time Communication** uses a dual-mode system with WebSockets (preferred) and HTTP Polling fallback. A local **Deploy Agent** (localhost:7865) ensures frictionless deployment and auto-import into UE5. The system supports **Blueprint Screenshot Capture** for multi-modal vision analysis. An **Enhanced Action Executor** handles file operations, project info display, and blueprint management, controlled by a **Feature Flag System**. A **UE5 Mock Testing Environment** allows Replit-based testing. A **Flexible Token Extraction System** uses regex patterns to extract action tokens from AI responses. **Production Server Auto-Selection** ensures the UE5 client connects to the production backend by default.

The system features **Multi-Server Detection and Display** to show which server (localhost, production, or custom) each UE5 client is connected to, with color-coded indicators on the dashboard. It incorporates a **Universal Bootstrap System** for seamless client updates (ZIP and TAR.GZ formats) and an **Emergency Fix Update System** with a GUI for non-technical users. **Connection Troubleshooting Tools** are built-in, including console utilities and a **Dashboard Reconnect Button**. A **UE5 Editor Toolbar Menu** provides easy access to troubleshooting tools directly from the editor.

**Cross-Server Federation Monitoring (October 2025):** A new federation mode allows the development dashboard to monitor production server connections in real-time. When enabled via toggle in the Settings tab, the dashboard queries both local and production endpoints, merging project lists with visual server source indicators (purple "Production" badges). The implementation uses a hardcoded production server URL to prevent SSRF attacks, employs async httpx client for non-blocking I/O with 5-second timeout, and persists toggle state in localStorage. This enables developers to work on code locally while monitoring live production connections without switching environments.

### System Design Choices
The system uses a **RESTful API** with JSON payloads, enforcing **Separation of Concerns** between UE viewport data collection and AI processing. It includes **Environment-based Configuration**, robust **Error Handling** with structured logging, and retry logic. A **Thread-Safe Action Queue** integrates with the Unreal Slate ticker. **Automatic Cache Management** is implemented via module version tracking with a **Persistent Client Reference System** that preserves HTTP/WebSocket clients across module reloads. **Security Hardening** ensures path traversal protection and read-only file operations. All UE5 client code adheres to **UE5.6 API Compliance**.

The UE5 client uses a **Modular Client Architecture** with a reorganized folder structure (`core/`, `network/`, `troubleshoot/`, `execution/`, `ui/`, `collection/`, `system/`, `tools/`, `test/`, `documentation/`, `archived/`) for improved maintainability, clear separation of concerns, and correct path resolution. A **Unified Registration System** consolidates HTTP polling clients and the Project Registry into a single source of truth, eliminating dual registration issues and providing consistent `project_id` generation via MD5 hashing and path normalization. It tracks connection health via `last_seen` timestamps and ensures server restart resilience with automatic re-registration.

**Critical Connection Reliability Fixes (October 2025):** Two critical bugs were identified and resolved to ensure absolute connection reliability: (1) Auto-initialization was never triggered on module import - fixed by adding `_auto_init()` call to `__init__.py`, ensuring clients automatically connect when UE5 loads the module. (2) Heartbeat endpoint didn't update the Project Registry - fixed by adding `update_project_last_seen()` call to the heartbeat handler, ensuring dashboard accurately reflects real-time connection status. A comprehensive connection diagnostics suite validates the entire HTTP polling lifecycle with 7 critical touchpoints. All connection tests pass (37/37 including backend API tests), confirming connection reliability is production-ready.

**Server URL Configuration (October 2025):** Production server uses deployment URL (`ue5-assistant-noahbutcher97.replit.app`) which has proper public API routing. Enhanced **UE5 Toolbar Menu** with one-click server management: "Update to Production Server" configures correct URL, "Show Current Server" displays connection info, "Switch to Localhost" enables local development, and dynamic dashboard URL always matches configured server. All server changes include automatic assistant restart. These toolbar options eliminate the need for users to have code fluency or API familiarity. Note: The workspace development URL has routing limitations and is not used for production connections.

## External Dependencies

### AI Services
- **OpenAI API**: For GPT model access (e.g., gpt-4o-mini, gpt-4o) for technical prose generation and multi-modal vision analysis.

### Python Packages (Backend)
- **fastapi**: Core web framework.
- **uvicorn**: ASGI server.
- **websockets**: WebSocket protocol support.
- **pydantic**: Data validation and settings management.
- **openai**: Official OpenAI Python client.
- **requests**: HTTP library.
- **httpx**: Async HTTP client for federation queries.
- **jinja2**: Template engine.

### Unreal Engine Integration
- **UE5.6+ Python API**: Native Python environment for editor interactions.
- **websocket-client**: Python WebSocket client library for UE5.

### Deployment Platform
- **Replit**: Hosting platform for the FastAPI backend.