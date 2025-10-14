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

### System Design Choices
The system uses a **RESTful API** with JSON payloads, enforcing **Separation of Concerns** between UE viewport data collection and AI processing. It includes **Environment-based Configuration**, robust **Error Handling** with structured logging, and retry logic. A **Thread-Safe Action Queue** integrates with the Unreal Slate ticker. **Automatic Cache Management** is implemented via module version tracking with a **Persistent Client Reference System** that preserves HTTP/WebSocket clients across module reloads. **Security Hardening** ensures path traversal protection and read-only file operations. All UE5 client code adheres to **UE5.6 API Compliance**.

The UE5 client uses a **Modular Client Architecture** with a reorganized folder structure (`core/`, `network/`, `troubleshoot/`, `execution/`, `ui/`, `collection/`, `system/`, `tools/`, `test/`, `documentation/`, `archived/`) for improved maintainability, clear separation of concerns, and correct path resolution. A **Unified Registration System** consolidates HTTP polling clients and the Project Registry into a single source of truth, eliminating dual registration issues and providing consistent `project_id` generation via MD5 hashing and path normalization. It tracks connection health via `last_seen` timestamps and ensures server restart resilience with automatic re-registration.

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
- **jinja2**: Template engine.

### Unreal Engine Integration
- **UE5.6+ Python API**: Native Python environment for editor interactions.
- **websocket-client**: Python WebSocket client library for UE5.

### Deployment Platform
- **Replit**: Hosting platform for the FastAPI backend.