# UE5 AI Assistant - Modular Architecture v2.0

A modular, extensible AI assistant system for Unreal Engine 5.6+ with enhanced context awareness and robust API communication.

**🎯 Blueprint Integration**: See [BLUEPRINT_INTEGRATION.md](BLUEPRINT_INTEGRATION.md) for complete Editor Utility Widget setup instructions.

## 📁 Installation

1. Copy the entire `AIAssistant` folder to your UE5 project:
   ```
   YourProject/Content/Python/AIAssistant/
   ```

2. The folder structure should look like:
   ```
   Content/Python/AIAssistant/
   ├── __init__.py
   ├── main.py              # Main entry point
   ├── config.py            # Configuration management
   ├── api_client.py        # API communication
   ├── context_collector.py # Enhanced scene data collection
   ├── action_executor.py   # Action system
   ├── ui_manager.py        # UI communication
   └── utils.py             # Utilities
   ```

## 🚀 Quick Start

### From Editor Utility Widget Blueprint (Recommended)

**Update your "Execute Python Command" node to:**

```python
import AIAssistant; AIAssistant.send_command('{0}')
```

**That's it!** Your existing Blueprint logic (text input → format → execute → read response file) works unchanged.

📘 **[Complete Blueprint Integration Guide →](BLUEPRINT_INTEGRATION.md)**

### From Python Console

```python
import AIAssistant

# Send a command
AIAssistant.send_command("what do I see?")

# Response written to: Saved/AIConsole/last_reply.txt
```

### Advanced Usage

```python
from AIAssistant import get_assistant

assistant = get_assistant()

# Process command (default: non-blocking async)
assistant.process_command("describe this scene")

# Force synchronous (blocks until complete)
response = assistant.process_command(
    "describe this scene", 
    use_async=False
)
```

## ⚙️ Configuration

Configuration is stored in `Saved/AIConsole/config.json`:

```json
{
  "api_base_url": "https://ue5-assistant-noahbutcher97.replit.app",
  "model": "gpt-4o-mini",
  "max_retries": 3,
  "retry_delay": 2.5,
  "timeout": 25,
  "enable_context_caching": true,
  "cache_duration": 30,
  "verbose_logging": false,
  "enable_confirmations": true,
  "max_context_turns": 6
}
```

Modify settings programmatically:

```python
from AIAssistant.config import get_config

config = get_config()
config.set("verbose_logging", True)
config.set("timeout", 30)
```

## 🧠 Enhanced Context Collection

The system now collects:

### Camera Data
- Position coordinates
- Rotation (pitch, yaw, roll)

### Actor Data
- Complete actor list with types
- Actor categorization by class
- Level/world information

### Lighting Setup
- Directional lights (position, rotation, intensity)
- Point lights
- Spot lights
- Sky atmosphere

### Environment
- Fog systems
- Post-process volumes
- Landscape information

### Selection Data
- Selected actors with details
- Material assignments
- Location data

## 🏗️ Architecture

### Design Principles

The modular architecture ensures robustness and extensibility:

1. **Separation of Concerns**: Each module has a single, clear responsibility
2. **Singleton Pattern**: Global instances prevent duplication and state conflicts
3. **File-Based Communication**: Blueprint ↔ Python via response files (robust, simple)
4. **Configuration Management**: JSON-based config with runtime modification support
5. **Error Resilience**: Retry logic, timeout handling, graceful degradation
6. **Extensibility**: Plugin-style action registry and context collectors

### Module Responsibilities

| Module | Purpose | Blueprint Compatible |
|--------|---------|---------------------|
| `main.py` | Orchestration & command routing | ✅ Primary entry point |
| `config.py` | Settings management | ✅ Can modify from Blueprint |
| `api_client.py` | Synchronous HTTP client | ✅ Used internally |
| `async_client.py` | Threaded async HTTP client | ✅ Used internally |
| `context_collector.py` | Scene data collection | ✅ Auto-invoked |
| `action_executor.py` | Command registry & execution | ✅ Extensible from Blueprint |
| `ui_manager.py` | File I/O for widget communication | ✅ Blueprint reads files |
| `utils.py` | Logging & utilities | ✅ Shared infrastructure |

### Blueprint Integration Architecture

```
[Blueprint UI] → [Execute Python] → [AIAssistant.send_command()]
                                            ↓
                                    [Route to action or AI]
                                            ↓
                                    [Collect context if needed]
                                            ↓
                                    [Process & generate response]
                                            ↓
                                    [Write to last_reply.txt]
                                            ↑
[Blueprint UI] ← [Read File] ← [Saved/AIConsole/last_reply.txt]
```

This file-based communication ensures:
- **Thread safety**: File writes are atomic
- **Blueprint simplicity**: Just read a text file
- **Async compatibility**: Works with both sync and async modes
- **Persistence**: Responses saved for debugging

## 🔧 Extending the System

### Add Custom Actions (From Blueprint or Python)

**From Python:**
```python
from AIAssistant import get_executor

def my_custom_action():
    import unreal
    # Your action logic here
    unreal.log("Custom action!")
    return "Action completed!"

# Register it
executor = get_executor()
executor.register("my_action", my_custom_action)
```

**From Blueprint (Execute Python Command):**
```python
import AIAssistant; exec('''
def my_action():
    import unreal
    unreal.log("Blueprint-defined action!")
    return "Done!"

AIAssistant.get_executor().register("my_action", my_action)
''')
```

### Add Custom Context Collectors

```python
from AIAssistant.context_collector import get_collector

collector = get_collector()

# Add a new method to the collector
def collect_custom_data(self):
    import unreal
    # Collect your custom scene data
    return {"custom_metric": 42}

# Monkey-patch it
collector.collect_custom_data = collect_custom_data.__get__(
    collector, type(collector)
)
```

### Modify Configuration at Runtime

**From Blueprint:**
```python
import AIAssistant; c = AIAssistant.get_config(); c.set('timeout', 60); c.set('verbose_logging', True)
```

**From Python:**
```python
from AIAssistant import get_config

config = get_config()
config.set('max_retries', 5)
config.set('retry_delay', 3.0)
```

## 📊 Logging

Enable verbose logging for debugging:

```python
from AIAssistant.config import get_config

config = get_config()
config.set("verbose_logging", True)
```

Logs are written to:
- Unreal Engine Output Log
- Console (print statements)
- `Saved/AIConsole/conversation_log.txt` (conversation history)

## 🎯 Built-in Actions

- `describe_viewport` - Comprehensive scene description
- `list_actors` - List all actors in level
- `get_selected_info` - Details about selected actors

## ⚠️ Execution Mode: Sync (Thread-Safe)

**Important:** The system uses **synchronous execution by default** for thread safety.

### Default Behavior (Recommended)
```python
AIAssistant.send_command(text)  # Sync mode (safe, reliable)
```

- ✅ **Thread-safe**: All UE API calls on main game thread
- ✅ **Reliable**: Complete context collection (camera, actors, lighting)
- ✅ **No errors**: No thread safety warnings
- ⚠️ **Blocks briefly**: 15-20 seconds during API call (acceptable for editor tools)
- ✅ **Blueprint compatible**: File-based communication works perfectly

### Why Sync Mode?

Unreal Engine requires all API calls to run on the main thread. Async mode attempts to execute UE APIs from background threads, causing:
```
❌ "Attempted to access Unreal API from outside the main game thread"
❌ Failed context collection (no camera, actors, or lighting data)
❌ File write errors
```

**Sync mode is the only reliable option until proper UE async implementation is added.**

### Async Mode (Experimental - Not Recommended)
```python
AIAssistant.send_command(text, use_async=True)  # Has thread errors
```

- ❌ **Thread errors**: UE API calls fail on worker threads  
- ❌ **Incomplete data**: Context collection fails
- ✅ **Non-blocking**: Network request doesn't freeze editor
- ❌ **Not reliable**: Use sync mode instead

See `THREAD_SAFETY.md` for technical details and future implementation options.

## 🔄 Migration from v1.0

### Blueprint Update Required

**Change your Format Text node from:**
```python
import ai_command_console; ai_command_console.send_and_store('{0}')
```

**To:**
```python
import AIAssistant; AIAssistant.send_command('{0}')
```

### What Stays the Same

- ✅ Response file: `Saved/AIConsole/last_reply.txt`
- ✅ Conversation log: `Saved/AIConsole/conversation_log.txt`
- ✅ File reading Blueprint logic
- ✅ Widget UI layout
- ✅ All file paths and locations

### What You Get for Free

- 🧠 **Enhanced context**: Lighting, materials, environment automatically collected
- 🔧 **Extensible actions**: Add custom commands from Blueprint or Python
- ⚙️ **Configuration**: Runtime settings via JSON or code
- 🔄 **Retry logic**: Automatic retry on network failures
- 📊 **Better logging**: Verbose mode for debugging
- 🎯 **Smarter descriptions**: Technical prose with complete scene coverage

## 🐛 Troubleshooting

### "requests library not available"
Run in UE Python console:
```python
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
```

### Timeout Errors
Increase timeout in config:
```python
from AIAssistant.config import get_config
get_config().set("timeout", 60)
```

### No Response
Check:
1. API server is running
2. Network connectivity
3. Verbose logging for detailed errors

## 📝 Version History

### v2.0.0 (October 2025)
- Modular architecture with separate components
- Enhanced context collection (lighting, materials, environment)
- Async API client with retry logic
- Configuration system
- Command registry pattern
- Better error handling and logging

### v1.0.0 (October 2025)
- Initial release
- Basic viewport description
- Token-based action routing
