# Blueprint Integration Guide - Server Selection

Quick reference for adding server selection to your Editor Utility Widget.

## 📁 Files Included

- `blueprint_helpers.py` - File-based communication functions for Blueprint
- All helper functions write output to `[Project]/Saved/AIConsole/*.txt` files

## 🎯 Quick Setup - ComboBox Server Selector

### 1. Add UI Elements

In your **Editor Utility Widget Designer**:

| Element Type | Name | Settings |
|-------------|------|----------|
| Text | - | Text: "Server:" |
| ComboBox (String) | `ServerComboBox` | Default: empty |
| Text Block | `ServerStatusText` | Text: "" (optional) |

### 2. Initialize ComboBox (Event Construct)

```
Event Construct
  ↓
Clear Options (ServerComboBox)
  ↓
Add Option (ServerComboBox) - "production"
  ↓
Add Option (ServerComboBox) - "dev"  
  ↓
Add Option (ServerComboBox) - "localhost"
  ↓
Execute Python Script:
────────────────────────────────────────────────
from AIAssistant import blueprint_helpers
blueprint_helpers.get_active_server()
────────────────────────────────────────────────
  ↓
Delay (0.1 seconds)
  ↓
Load File to String
  - Filename: "[YourProject]/Saved/AIConsole/server_status.txt"
  ↓
Set Selected Option (ServerComboBox) - [Result]
```

### 3. Handle Selection Change

```
On Selection Changed (ServerComboBox)
  ↓
Get Selected Option → [Selected Server]
  ↓
Format String: "{0}" with [Selected Server]
  ↓
Execute Python Script:
────────────────────────────────────────────────
from AIAssistant import blueprint_helpers
blueprint_helpers.switch_server('{0}')
────────────────────────────────────────────────
  ↓
Delay (0.1 seconds)
  ↓
Load File to String
  - Filename: "[YourProject]/Saved/AIConsole/server_switch_result.txt"
  ↓
Split String (by delimiter "|") → [Status, URL]
  ↓
Branch (Status == "success"):
  TRUE → Set Text (ServerStatusText) to "✅ Connected: [URL]"
  FALSE → Set Text (ServerStatusText) to "❌ [URL]"
```

## 📋 Copy-Paste Python Scripts

### Get Active Server
```python
from AIAssistant import blueprint_helpers
blueprint_helpers.get_active_server()
```
**Read from:** `server_status.txt`  
**Output:** `"production"` | `"dev"` | `"localhost"`

---

### Switch Server (use with String Format)
```python
from AIAssistant import blueprint_helpers
blueprint_helpers.switch_server('{0}')
```
**Inject:** Server name via String Format into `{0}`  
**Read from:** `server_switch_result.txt`  
**Output:** `"success|https://..."` or `"error|Invalid server"`  
**Parse:** Split by `"|"` to get `[status, message]`

---

### Get Server Display
```python
from AIAssistant import blueprint_helpers
blueprint_helpers.get_server_display()
```
**Read from:** `server_display.txt`  
**Output:** `"production → https://..."`

---

### List All Servers
```python
from AIAssistant import blueprint_helpers
blueprint_helpers.list_servers()
```
**Read from:** `server_list.txt`  
**Output:** `"production,dev,localhost"`  
**Parse:** Split by `","` to get array

## 🔄 Alternative: Direct Inline Scripts

If you prefer not to import `blueprint_helpers`, use these standalone scripts:

<details>
<summary>Click to expand inline scripts</summary>

### Get Active Server (Inline)
```python
from AIAssistant import config
import unreal
from pathlib import Path

cfg = config.get_config()
active = cfg.get_active_server()

output_path = Path(unreal.Paths.project_saved_dir()) / "AIConsole" / "server_status.txt"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(active, encoding='utf-8')
```

### Switch Server (Inline)
```python
from AIAssistant import config
import unreal
from pathlib import Path

selected = '{0}'  # Inject via String Format
cfg = config.get_config()
success = cfg.switch_server(selected)

output_path = Path(unreal.Paths.project_saved_dir()) / "AIConsole" / "server_switch_result.txt"
output_path.parent.mkdir(parents=True, exist_ok=True)

if success:
    result = f"success|{cfg.api_url}"
else:
    result = f"error|Invalid server: {selected}"

output_path.write_text(result, encoding='utf-8')
```

### Get Server Display (Inline)
```python
from AIAssistant import config
import unreal
from pathlib import Path

cfg = config.get_config()
active = cfg.get_active_server()
url = cfg.api_url
status = f"{active} → {url}"

output_path = Path(unreal.Paths.project_saved_dir()) / "AIConsole" / "server_display.txt"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(status, encoding='utf-8')
```

</details>

## 📍 Available Servers

| Server | URL | Use Case |
|--------|-----|----------|
| **production** | `https://ue5-assistant-noahbutcher97.replit.app` | Stable deployed version |
| **dev** | `https://...-janeway.replit.dev` | Latest development changes |
| **localhost** | `http://localhost:5000` | Local testing |

## 💡 Tips

- **Server setting persists** across UE5 sessions (saved to config.json)
- **Always add 0.1s Delay** between Python execution and file reading
- **File paths** use forward slashes: `[Project]/Saved/AIConsole/filename.txt`
- **Test**: Switch to `dev` server, then check the dashboard to see conversations appear!

## 🐛 Troubleshooting

**ComboBox shows wrong server?**
- Make sure Delay node is between Python execution and file reading
- Check that file path is correct for your project

**Server switch doesn't work?**
- Verify String Format node correctly injects server name into `{0}`
- Check Python Output Log for errors

**Can't see conversations in dashboard?**
- Confirm you're viewing the correct server's dashboard
- `production` → `replit.app` URL
- `dev` → `janeway.replit.dev` URL
