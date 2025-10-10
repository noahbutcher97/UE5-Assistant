# UE5 AI Assistant - Modular Architecture v2.0

A modular, extensible AI assistant system for Unreal Engine 5.6+ with enhanced context awareness and async API communication.

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

## 🚀 Usage

### From Editor Utility Widget (Recommended - Async):

```python
import AIAssistant

# Async mode (non-blocking, editor stays responsive)
AIAssistant.send_command("what do I see?")
# Returns immediately with "⏳ Processing..."
# Response written to Saved/AIConsole/last_reply.txt when ready
```

### Synchronous Mode (Blocks Editor):

```python
import AIAssistant

# Sync mode (blocks editor until complete, simpler but freezes UI)
response = AIAssistant.send_command(
    "what do I see?", 
    use_async=False
)
print(response)
```

### Direct Python Usage:

```python
from AIAssistant import get_assistant

assistant = get_assistant()

# Async (recommended)
assistant.process_command("describe this scene", use_async=True)

# Sync (simple but blocks)
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

## 🔧 Extending the System

### Add New Actions

```python
from AIAssistant.action_executor import get_executor

def my_custom_action():
    # Your action logic here
    return "Action completed!"

# Register it
executor = get_executor()
executor.register("my_action", my_custom_action)
```

### Custom Context Collection

```python
from AIAssistant.context_collector import get_collector

collector = get_collector()
# Add custom methods to collector class
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

## 🔄 Migration from v1.0

If you were using the old scripts:

1. Replace Blueprint Python calls:
   - OLD: `import ai_command_console; ai_command_console.send_and_store(text)`
   - NEW: `import AIAssistant.main as ai; ai.send_command(text)`

2. The response file location remains the same:
   - `Saved/AIConsole/last_reply.txt`

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
