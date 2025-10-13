# Unreal Engine AI Viewport Assistant

## Overview
This project delivers a FastAPI-based backend service designed to generate AI-powered technical documentation for Unreal Engine 5 editor viewport contexts. It processes structured viewport data from Unreal Engine's Python environment to create accurate, factual descriptions of 3D scenes and level designs using OpenAI's GPT models. The primary goal is to enhance UE5 developers' workflows by providing advanced insights and implementation guidance. Key features include multi-project management, context-aware AI responses, UE 5.6 compliant utility generation, comprehensive editor orchestration (scene building, camera control, actor manipulation), and a unified control dashboard. The project aims to bridge Unreal Engine's scripting capabilities with cloud-based AI, thereby boosting developer productivity and fostering innovative game development.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
The system features a **Unified Control Center** (`/dashboard`) with a Project Hub, Live Feed, Project Intelligence, Guidance, Tools, Settings, Diagnostics, and About sections. It employs a **Modern Design System** characterized by the Inter font, a refined spacing system (max-width 1400px dashboard container), professional aesthetics, subtle animations, and softer shadows. The **Tools Tab** provides AI-powered widget generation with automated class name sanitization. Key UI/UX elements include a browser-based **Project Selector** with real-time connection status, enhanced visuals (glowing text, micro-interactions), and quality-of-life features such as keyboard shortcuts, tooltips, one-click copy buttons, and visual feedback. The architecture is **Responsive**, offering mobile-friendly layouts and touch-optimized controls.

### Technical Implementations
The backend is built with **FastAPI** for async capabilities and Pydantic-based validation. **AI Integration** leverages OpenAI GPT models (default: gpt-4o-mini) for technical prose generation and multi-modal vision analysis. It includes a **Multi-Project Registry** for managing UE5 projects, enabling browser-based selection and **Auto-Registration**. **Context-Aware Queries** enhance AI responses using active project data. **Editor Orchestration Systems** (SceneOrchestrator, ViewportController, ActorManipulator) facilitate scene building, camera control, and actor manipulation.

A **Fully Automated Widget Generator** within the Tools tab provides AI-powered Editor Utility Widget generation. Users input widget details, and OpenAI generates a complete UE 5.6 Python script, which the backend queues for the UE5 client to write locally. A **File Drop Tool** allows developers to test end-to-end file writing capabilities. **Persistent Operation & Event History** is maintained via bounded FIFO lists (max 100 entries) for operations and system events, displayed in the Live Feed. A **Server Switching System** allows granular control over backend endpoints for connected clients.

**Real-Time Communication** uses a dual-mode system with WebSockets (preferred) and HTTP Polling fallback. A local **Deploy Agent** (localhost:7865) ensures frictionless deployment and auto-import into UE5. The system supports **Blueprint Screenshot Capture** for multi-modal vision analysis. An **Enhanced Action Executor** handles file operations, project info display, and blueprint management, controlled by a **Feature Flag System**. A **UE5 Mock Testing Environment** allows Replit-based testing without an active UE5 instance. The **Flexible Token Extraction System** uses regex patterns to extract action tokens from AI responses, allowing natural language alongside commands. **Production Server Auto-Selection** ensures the UE5 client connects to the production backend by default.

The system incorporates a **Universal Bootstrap System** for seamless client updates, handling both ZIP and TAR.GZ formats. It also includes an **Emergency Fix Update System** with a GUI-based solution for non-technical users to resolve thread safety crashes without manual restarts. **Connection Troubleshooting Tools** are built-in, providing console-based utilities (e.g., reconnect, test server) for easy recovery. A **Dashboard Reconnect Button** offers a GUI-based recovery path for dropped connections.

### System Design Choices
The system uses a **RESTful API** with JSON payloads and enforces **Separation of Concerns** between UE viewport data collection and AI processing. **Environment-based Configuration** manages sensitive data. It includes robust **Error Handling** with structured logging and retry logic. A **Thread-Safe Action Queue** integrates with the Unreal Slate ticker for safe main thread execution. **Automatic Cache Management** is implemented via module version tracking. **Security Hardening** ensures path traversal protection and read-only file operations. All UE5 client code adheres to **UE5.6 API Compliance**.

## External Dependencies

### AI Services
- **OpenAI API** (v1.57.0): For GPT model access (e.g., gpt-4o-mini, gpt-4o) for technical prose generation and multi-modal vision analysis.

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

### Deployment Platform
- **Replit**: Hosting platform for the FastAPI backend.