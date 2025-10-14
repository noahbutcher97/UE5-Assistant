# UE5 AI Assistant - Comprehensive Testing Guide

## 📋 Overview

This testing suite provides **complete validation** of the UE5 AI Assistant system without requiring Unreal Engine. Every UI element, backend endpoint, and client module is systematically tested.

## 🎯 Test Coverage

### ✅ Dashboard UI Elements (`tests/ui/`)
Tests every interactive element on the web dashboard:

**Project Selector:**
- Project dropdown functionality
- Set/get active project endpoints
- Connection status indicators
- Project metadata display

**Live Feed Section:**
- Event history retrieval
- Operation logs display
- Real-time update mechanisms

**AI Chat Interface:**
- Chat input/output
- Context-aware AI queries
- Message history
- AI command execution

**Tools Tab:**
- Widget generator inputs
- Generate utility endpoint
- Action plan generation
- Code output display

**Settings Tab:**
- Configuration retrieval
- Settings persistence
- Update configuration

**Quick Actions:**
- All quick action buttons
- Describe Viewport
- List Blueprints
- Project Info
- Trigger Auto-Update

### ✅ Backend Routes (`tests/backend/`)
Tests every API endpoint comprehensively:

**HTTP Polling Routes:**
- `/api/ue5/register_http` - Client registration
- `/api/ue5/poll` - Command polling
- `/api/ue5/response` - Response submission
- `/api/ue5/heartbeat` - Keep-alive

**WebSocket Routes:**
- `/ws/{project_id}` - WebSocket connections

**Project Management:**
- `/api/register_project` - Register projects
- `/api/projects` - List all projects
- `/api/active_project` - Get active project
- `/api/set_active_project` - Set active project

**Command Routing:**
- `/send_command_to_ue5` - Send commands
- `/execute_command` - AI command execution

**AI Integration:**
- `/describe_viewport` - Viewport AI description
- `/answer_with_context` - Context-aware AI

**Utility Generation:**
- `/api/generate_utility` - Widget generation
- `/api/generate_action_plan` - Action planning

**Auto-Update:**
- `/api/trigger_auto_update` - Trigger updates
- `/api/download_client` - Download package

**Configuration:**
- `/api/config` (GET/POST) - Settings management

**Diagnostics:**
- `/api/events` - Event history
- `/api/operations` - Operation logs
- `/api/server_switch` - Server switching
- `/api/reconnect` - Reconnection

### ✅ UE5 Client Modules (`tests/ue5_client/`)
Tests all client-side modules using mock Unreal API:

**Core Module:**
- `AIAssistant` class initialization
- Main module imports

**Network Modules:**
- `HTTPPollingClient` - HTTP communication
- `WSClient` - WebSocket communication

**Execution Modules:**
- `ActionQueue` - Thread-safe queue
- `ActionExecutor` - Action execution
- Action registration and dispatch

**Collection Modules:**
- `ViewportCollector` - Viewport data
- `FileCollector` - File system
- `ProjectMetadataCollector` - Metadata

**Tools Modules:**
- `SceneOrchestrator` - Scene building
- `ViewportController` - Camera control
- `ActorManipulator` - Actor manipulation
- `BlueprintCapture` - Screenshot capture
- `EditorUtilityGenerator` - Widget generation

**System Modules:**
- `AutoUpdate` - Update mechanism
- `CleanupLegacy` - Cleanup utilities
- Version tracking
- Update lock mechanism

**UI Modules:**
- `ToolbarMenu` - Editor toolbar
- `UIManager` - UI management

**Troubleshoot Modules:**
- `Troubleshooter` - Diagnostics
- `ConnectionTroubleshooter` - Connection fixes

### ✅ Integration Tests (`tests/integration/`)
Tests complete end-to-end workflows:

**User Workflows:**
- Dashboard → Command → UE5 → Response
- AI widget generation flow
- AI chat with context flow
- Project switching workflow
- Auto-update workflow

**Error Recovery:**
- Disconnection recovery
- Invalid command handling
- Graceful error handling

**Concurrency:**
- Multiple projects simultaneously
- Command isolation per project
- Concurrent user operations

**Data Persistence:**
- Project data persistence
- Operation history
- Configuration persistence

## 🚀 Running Tests

### Quick Start

Run all tests with comprehensive reporting:
```bash
python tests/test_suite_runner.py
```

Or use the simple runner:
```bash
python run_all_tests.py
```

### Run Specific Test Categories

**UI Tests Only:**
```bash
pytest tests/ui/ -v
```

**Backend Tests Only:**
```bash
pytest tests/backend/ -v
```

**UE5 Client Tests Only:**
```bash
pytest tests/ue5_client/ -v
```

**Integration Tests Only:**
```bash
pytest tests/integration/ -v
```

### Run Individual Test Files

```bash
pytest tests/ui/test_dashboard_elements.py -v
pytest tests/backend/test_routes_comprehensive.py -v
pytest tests/ue5_client/test_client_modules.py -v
pytest tests/integration/test_end_to_end_workflows.py -v
```

### Run Specific Test Classes

```bash
pytest tests/ui/test_dashboard_elements.py::TestProjectSelector -v
pytest tests/backend/test_routes_comprehensive.py::TestHTTPPollingRoutes -v
```

### Run Specific Test Methods

```bash
pytest tests/ui/test_dashboard_elements.py::TestProjectSelector::test_project_selector_exists -v
```

## 📊 Test Reports

### Detailed Report

The comprehensive test runner (`tests/test_suite_runner.py`) provides:

- **Category Summaries**: Results grouped by UI, Backend, Client, Integration
- **Individual Test Stats**: Pass/fail counts, duration, test counts
- **Coverage Analysis**: Which components are tested
- **Failed Test Details**: Specific failures with context
- **Overall Metrics**: Total tests, duration, timestamps

### Example Output

```
==================================================================================================
  UE5 AI ASSISTANT - COMPREHENSIVE TEST SUITE
==================================================================================================

--------------------------------------------------------------------------------------------------
  Dashboard UI Tests
--------------------------------------------------------------------------------------------------
  ✅ PASSED      Dashboard UI Elements                              (25/25 tests, 2.34s)

--------------------------------------------------------------------------------------------------
  Backend Tests
--------------------------------------------------------------------------------------------------
  ✅ PASSED      Backend API Endpoints                             (45/45 tests, 3.21s)
  ✅ PASSED      Backend Routes Comprehensive                      (38/38 tests, 2.87s)

==================================================================================================
  OVERALL SUMMARY
==================================================================================================

  Test Suites:      9/9 passed
  Individual Tests: 245/245 passed
  Total Duration:   18.45s

🎉 ALL TESTS PASSED!
🚀 The UE5 AI Assistant is production-ready!
```

## 🔧 Test Infrastructure

### Mock Unreal API (`tests/ue5_client/mock_unreal.py`)

Simulates the entire Unreal Engine Python API:
- `unreal.Paths` - Project paths
- `unreal.AssetRegistry` - Asset queries
- `unreal.EditorAssetLibrary` - Asset operations
- `unreal.EditorActorSubsystem` - Actor management
- `unreal.ToolMenus` - Editor menus

### Mock Fixtures (`tests/fixtures/`)

Pre-defined test data:
- `mock_viewport_data.py` - Viewport snapshots
- `mock_openai_responses.py` - AI responses

### Test Client (`fastapi.testclient.TestClient`)

- Makes real HTTP requests to FastAPI app
- No server startup required
- Full request/response cycle testing

## 🎯 Adding New Tests

### UI Element Test Template

```python
class TestNewUIElement:
    """Test new UI component."""
    
    def test_element_exists(self):
        """Test element is present in dashboard."""
        response = client.get("/dashboard")
        assert "element_id" in response.text
    
    def test_element_endpoint(self):
        """Test element's backend endpoint."""
        response = client.post("/api/new_endpoint", json={
            "data": "test"
        })
        assert response.status_code == 200
```

### Backend Route Test Template

```python
class TestNewRoute:
    """Test new API route."""
    
    def test_route_success(self):
        """Test successful route execution."""
        response = client.post("/api/new_route", json={
            "param": "value"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_route_validation(self):
        """Test route validates input."""
        response = client.post("/api/new_route", json={})
        assert response.status_code in [200, 400, 422]
```

### UE5 Client Module Test Template

```python
class TestNewModule:
    """Test new client module."""
    
    def test_module_import(self):
        """Test module imports successfully."""
        from AIAssistant.new_module import NewClass
        assert NewClass is not None
    
    def test_module_functionality(self):
        """Test module core functionality."""
        from AIAssistant.new_module import NewClass
        instance = NewClass()
        result = instance.method()
        assert result is not None
```

### Integration Workflow Test Template

```python
class TestNewWorkflow:
    """Test new user workflow."""
    
    def test_complete_workflow(self):
        """Test: User action → Backend → UE5 → Response."""
        # Step 1: User initiates
        response1 = client.post("/api/action", json={})
        assert response1.status_code == 200
        
        # Step 2: Command queued
        response2 = client.post("/api/ue5/poll", json={
            "project_id": "test"
        })
        assert len(response2.json()["commands"]) > 0
        
        # Step 3: Response received
        response3 = client.post("/api/ue5/response", json={
            "project_id": "test",
            "response": {"success": True}
        })
        assert response3.json()["success"] is True
```

## 📝 Best Practices

1. **Test Isolation**: Each test is independent
2. **Setup/Teardown**: Use `setup_method()` for test data
3. **Mock External APIs**: Use `@patch` for OpenAI, etc.
4. **Descriptive Names**: Test names describe what they test
5. **Assertions**: Clear, specific assertions
6. **Error Cases**: Test both success and failure paths
7. **Documentation**: Docstrings explain test purpose

## ✅ Validation Checklist

Before marking a feature complete, ensure:

- [ ] UI elements have tests
- [ ] Backend endpoints have tests  
- [ ] Client modules have tests
- [ ] End-to-end workflow tested
- [ ] Error cases handled
- [ ] All tests pass
- [ ] Coverage report reviewed

## 🚦 CI/CD Integration

To integrate with CI/CD:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: python tests/test_suite_runner.py
  
- name: Check Coverage
  run: pytest --cov=app --cov=ue5_client tests/
```

## 📚 Additional Resources

- **Test README**: `tests/README.md`
- **Mock Unreal Docs**: `tests/ue5_client/README.md`
- **Test Results**: `tests/TEST_RESULTS.md`
