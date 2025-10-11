# Backend Documentation

Welcome to the UE5 AI Assistant Backend documentation. This directory contains comprehensive technical documentation for all backend systems.

## Documentation Files

### 📐 [ARCHITECTURE.md](./ARCHITECTURE.md)
**Overview of the backend architecture and design patterns**

- Layered architecture with dependency injection
- Modular design principles
- Request flow diagrams
- File structure overview
- Technology stack
- Extension points

**Start here** to understand the overall system design.

---

### 📦 [MODELS.md](./MODELS.md)
**Data models and validation schemas**

- `ViewportContext` - UE5 viewport data structure
- `ConversationEntry` - Conversation logging model
- `ConfigUpdate` - Configuration update requests
- v2.0 vs v1.0 structure comparison
- Type safety and validation

**Read this** to understand data structures and API contracts.

---

### 🔌 [ROUTES.md](./ROUTES.md)
**API endpoints documentation**

- Core routes (`/health`, `/test`, `/ping_openai`)
- AI processing routes (`/execute_command`, `/describe_viewport`)
- Configuration routes (`/api/config`)
- Conversation routes (`/api/conversations`)
- Dashboard route (`/dashboard`)
- Request/response examples

**Use this** as API reference documentation.

---

### ⚙️ [SERVICES.md](./SERVICES.md)
**Business logic layer documentation**

- `openai_client.py` - OpenAI API integration
- `filtering.py` - Intelligent data filtering
- `conversation.py` - History management
- Service integration patterns
- Error handling strategies

**Explore this** to understand core business logic.

---

### 🎯 [FILTERING.md](./FILTERING.md)
**Intelligent filtering system deep dive**

- 6 filter modes (minimal → complete)
- Filter mode matrix with token reduction metrics
- Performance impact analysis
- Use case recommendations
- Cost optimization strategies

**Study this** to optimize token usage and costs.

---

### ⚙️ [CONFIGURATION.md](./CONFIGURATION.md)
**Configuration system guide**

- 7 response style presets
- Configuration parameters
- API configuration endpoints
- UE5 client synchronization
- Environment variables
- Best practices

**Reference this** for configuration and customization.

---

## Quick Start

1. **New to the project?** Start with [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Building API integrations?** Check [ROUTES.md](./ROUTES.md)
3. **Optimizing costs?** Read [FILTERING.md](./FILTERING.md)
4. **Customizing responses?** See [CONFIGURATION.md](./CONFIGURATION.md)
5. **Debugging data issues?** Consult [MODELS.md](./MODELS.md)
6. **Understanding services?** Review [SERVICES.md](./SERVICES.md)

## Architecture Diagram

```
UE5 Client (Python 3.11)
    ↓ HTTPS
FastAPI Backend (routes.py)
    ↓
Pydantic Models (models.py)
    ↓
Intelligent Filtering (services/filtering.py)
    ↓
OpenAI API (services/openai_client.py)
    ↓
Conversation Logging (services/conversation.py)
    ↓
Response to UE5
```

## Key Features

### 🎨 7 Response Styles
- **Descriptive** - Clear technical prose (default)
- **Technical** - Precise specs with coordinates
- **Natural** - Conversational descriptions
- **Balanced** - Technical + readability
- **Concise** - Extremely brief summaries
- **Detailed** - Comprehensive analysis
- **Creative** - Vivid narrative storytelling

### 🔍 Intelligent Filtering
- **30-70% token reduction** based on response style
- **6 filter modes** from minimal to complete
- **Automatic optimization** - no manual configuration

### 💾 Conversation Persistence
- **In-memory ring buffer** (100 entries)
- **JSON Lines file persistence** (`conversations.jsonl`)
- **Survives server restarts**

### 🌐 Web Dashboard
- Real-time conversation monitoring
- Configuration settings panel
- Response style selector
- API documentation viewer

## File Structure

```
app/
├── __init__.py
├── config.py              # Configuration & response styles
├── models.py              # Pydantic data models
├── routes.py              # FastAPI endpoints
├── dashboard.py           # Web dashboard HTML
├── services/
│   ├── __init__.py
│   ├── openai_client.py   # OpenAI integration
│   ├── filtering.py       # Data filtering
│   └── conversation.py    # History management
└── Documentation/         # This directory
    ├── README.md          # This file
    ├── ARCHITECTURE.md
    ├── MODELS.md
    ├── ROUTES.md
    ├── SERVICES.md
    ├── FILTERING.md
    └── CONFIGURATION.md
```

## Technology Stack

- **FastAPI** - Modern async web framework
- **Pydantic v2** - Data validation
- **OpenAI API** - GPT models
- **Python 3.11** - Matches UE5.6
- **Uvicorn** - ASGI server

## Contributing

When adding new features:

1. **Document in appropriate .md file**
2. **Update this README if structure changes**
3. **Include code examples**
4. **Add to architecture diagram if needed**

## Related Documentation

- **UE5 Client Docs**: `../attached_assets/AIAssistant/Documentation/`
- **Main README**: `../../replit.md`
- **API Endpoints**: http://localhost:5000/docs (FastAPI auto-docs)

---

*Last Updated: October 11, 2025 - v3.0 Modular Architecture*
