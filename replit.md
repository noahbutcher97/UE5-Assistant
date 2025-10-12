# Unreal Engine AI Viewport Assistant

## Overview
This project provides a FastAPI backend service for generating AI-powered technical documentation of Unreal Engine 5 editor viewport contexts. It processes structured viewport data from Unreal Engine's Python environment to produce precise, factual descriptions of 3D scenes and level designs using OpenAI's GPT models. The system aims to enhance UE5 developers' workflows by offering advanced insights and implementation guidance. Key capabilities include multi-project management, context-aware AI responses, UE 5.6 compliant utility generation, comprehensive editor orchestration (scene building, camera control, actor manipulation), and a unified control dashboard. The project seeks to bridge Unreal Engine's scripting capabilities with cloud-based AI services, ultimately enhancing developer productivity and fostering innovative game development.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
The system features a **Unified Control Center** (`/dashboard`) with a Project Hub, Conversations, Settings, API Info, and About sections. It employs a **Modern Design System** with an Inter font, cyberpunk aesthetic, animated gradients, glassmorphism effects, and smooth CSS transitions. Key UI/UX elements include a browser-based **Project Selector** with real-time connection status, enhanced visuals (glowing text, animated backgrounds, hover micro-interactions), and quality-of-life features like keyboard shortcuts, tooltips, one-click copy buttons, and visual feedback. The architecture is **Responsive**, providing mobile-friendly layouts and touch-optimized controls.

### Technical Implementations
The backend is built with **FastAPI** for async capabilities and Pydantic-based validation. **AI Integration** leverages OpenAI GPT models (default: gpt-4o-mini) for technical prose generation and multi-modal vision analysis. It features a **Multi-Project Registry** for managing UE5 projects, enabling browser-based selection and **Auto-Registration** of projects. **Context-Aware Queries** enhance AI responses with active project data. **Editor Orchestration Systems** (SceneOrchestrator, ViewportController, ActorManipulator) provide scene building, camera control, and actor manipulation. A **UE 5.6 Compliant Utility Generator** creates Editor Utility Widgets. **Real-Time Communication** is handled via a dual-mode system using WebSockets (preferred) with an HTTP Polling fallback. A local **Deploy Agent** (localhost:7865) facilitates frictionless deployment and auto-import into UE5. The system supports **Blueprint Screenshot Capture**, uploading base64 images to OpenAI Vision API (gpt-4o). An **Enhanced Action Executor** provides file operations, project info display, and blueprint management, controlled by a **Feature Flag System**. A **UE5 Mock Testing Environment** (`mock_unreal.py`) allows Replit-based testing without an active UE5 instance.

### System Design Choices
The system uses a **RESTful API** with JSON payloads and enforces **Separation of Concerns** between UE viewport data collection and AI processing. **Environment-based Configuration** manages sensitive data. It includes robust **Error Handling** with structured logging and retry logic. A **Thread-Safe Action Queue** integrates with Unreal Slate ticker for safe main thread execution. **Automatic Cache Management** is implemented via module version tracking. **Security Hardening** ensures path traversal protection and read-only file operations. All UE5 client code adheres to **UE5.6 API Compliance**.

## External Dependencies

### AI Services
- **OpenAI API** (v1.57.0): For GPT model access (e.g., gpt-4o-mini, gpt-4o) for technical prose generation and multi-modal vision analysis. Requires `OPENAI_API_KEY`.

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
- **Replit**: Hosting platform for the FastAPI backend, with a base URL `https://ue5-assistant-noahbutcher97.replit.app`.