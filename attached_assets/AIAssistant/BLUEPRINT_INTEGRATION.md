# Blueprint Integration Guide

## Overview

This guide shows how to integrate the modular AIAssistant v2.0 with your Editor Utility Widget Blueprint.

## Current Blueprint Setup (From Images)

Your current Blueprint executes:
```python
import ai_command_console
ai_command_console.send_and_store('{user_input}')
```

## Updated Blueprint Configuration

### Option 1: Simple Update (Recommended)

**Change your Python command format to:**
```python
import AIAssistant; AIAssistant.send_command('{0}')
```

**Blueprint Node Configuration:**
1. **Format Text Node**: `import AIAssistant; AIAssistant.send_command('{0}')`
2. **Text Box**: Connect to `{0}` parameter
3. **Execute Python Command (Animated)**: 
   - Command: Result from Format Text
   - Execution Mode: `ExecuteFile`
   - File Execution Scope: `Project`

### Option 2: With Async Control

If you want to control sync/async behavior from Blueprint:

```python
import AIAssistant; AIAssistant.send_command('{0}', use_async=True)
```

- `use_async=True`: Non-blocking (default, recommended)
- `use_async=False`: Blocks until complete (simpler, but freezes UI)

## Blueprint Visual Update

### Before (Old System):
```
[Button Clicked] → [Format: "import ai_command_console..."] → [Execute Python]
```

### After (New System):
```
[Button Clicked] → [Format: "import AIAssistant..."] → [Execute Python]
```

**The rest of your Blueprint remains exactly the same!**

## Reading the Response

Your existing "Find Body Text Ref" logic works unchanged:
- Response file: `Saved/AIConsole/last_reply.txt`
- Read this file and display in your text box

## Complete Blueprint Flow

1. **User types** in text box → Stored in variable
2. **Click "Send Prompt To AI"** button
3. **Format Text**: `import AIAssistant; AIAssistant.send_command('{user_input}')`
4. **Execute Python Command (Animated)**: Runs the formatted command
5. **Python writes** response to `Saved/AIConsole/last_reply.txt`
6. **Find Body Text Ref**: Reads the response file
7. **Display** response in output text box

## Configuration Options

### From Blueprint (Optional)

Add a configuration step before sending commands:

```python
import AIAssistant; AIAssistant.get_config().set('verbose_logging', True)
```

### Configuration File

Edit `Saved/AIConsole/config.json` to customize:

```json
{
  "api_base_url": "https://ue5-assistant-noahbutcher97.replit.app",
  "model": "gpt-4o-mini",
  "timeout": 25,
  "verbose_logging": false,
  "max_context_turns": 6
}
```

## Enhanced Features Available

### Smart Context Detection

The system now automatically collects:
- Camera position and rotation
- All actors in scene with types
- Lighting setup (directional, point, spot lights)
- Selected actors with details
- Materials and components
- Environment settings

**No Blueprint changes needed** - just use the new Python import!

### Action Commands

These work automatically:
- "what do I see?" → Viewport description
- "describe scene" → Full scene analysis  
- "list actors" → Actor inventory
- "selected" → Selection details

### Conversation Memory

The system remembers context across commands:
```python
# First command
AIAssistant.send_command("what lights are in the scene?")

# Follow-up command (remembers context)
AIAssistant.send_command("make them brighter")
```

## Troubleshooting

### "Module 'AIAssistant' not found"

Ensure the folder structure is correct:
```
YourProject/Content/Python/AIAssistant/
├── __init__.py
├── main.py
├── config.py
└── ... (other files)
```

### Response not appearing

1. Check the Python Output Log for errors
2. Verify `Saved/AIConsole/last_reply.txt` exists
3. Enable verbose logging:
   ```python
   import AIAssistant
   AIAssistant.get_config().set('verbose_logging', True)
   ```

### Timeout errors

Increase timeout in Blueprint:
```python
import AIAssistant; c = AIAssistant.get_config(); c.set('timeout', 60); AIAssistant.send_command('{0}')
```

Or edit `Saved/AIConsole/config.json`:
```json
{
  "timeout": 60
}
```

## Advanced: Multi-Step Blueprint Commands

### Example: Configure then Execute

**Node 1** - Configure:
```python
import AIAssistant; AIAssistant.get_config().set('verbose_logging', True)
```

**Node 2** - Send Command:
```python
import AIAssistant; AIAssistant.send_command('{0}')
```

### Example: Custom Actions

Register custom actions from Blueprint:

```python
import AIAssistant; exec('''
def my_action():
    import unreal
    unreal.log("Custom action executed!")
    return "Action complete"

AIAssistant.get_executor().register("my_action", my_action)
''')
```

## Migration Checklist

- [ ] Copy `AIAssistant` folder to `Content/Python/`
- [ ] Update Blueprint Format Text node
- [ ] Test with a simple command ("what do I see?")
- [ ] Verify response appears in text box
- [ ] Configure settings in `config.json` if needed
- [ ] Enable verbose logging for debugging if needed

## Quick Reference

| Old Command | New Command |
|-------------|-------------|
| `import ai_command_console` | `import AIAssistant` |
| `ai_command_console.send_and_store(text)` | `AIAssistant.send_command(text)` |
| Response file: Same location | `Saved/AIConsole/last_reply.txt` |
| Conversation log: Same location | `Saved/AIConsole/conversation_log.txt` |
