# How to Connect UE5 Client to Backend Server

## The Problem
Your UE5 client is trying to connect to `localhost:5000` (your local computer), but the backend server is running on Replit at a different address.

## Quick Fix - Option 1: Use the Fix Script

**In UE5's Python Console (Window > Developer Tools > Output Log > Cmd tab):**

```python
import sys
sys.path.insert(0, r'D:/UnrealProjects/5.6/UE5_Assistant/Content/Python')
import QUICK_FIX_SERVER_URL
```

This will automatically switch to the production server and reconnect.

---

## Quick Fix - Option 2: Use the Toolbar Menu

1. In UE5, go to the menu bar: **AI Assistant > Test Connection**
2. This will show you the current connection status
3. Then go to: **AI Assistant > Restart Assistant**
4. The client should reconnect to the production server

---

## Manual Fix - Option 3: Configure Server Manually

**In UE5's Python Console:**

```python
from AIAssistant.core.config import get_config
config = get_config()

# Switch to production server
config.set("active_server", "production")

# Restart the assistant
from AIAssistant.system.auto_update import force_restart_assistant
force_restart_assistant()
```

---

## Verify Connection

After applying the fix, check that you're connected:

```python
from AIAssistant.core.config import get_config
config = get_config()
print(f"Server: {config.api_url}")
# Should show: https://ue5-assistant-noahbutcher97.replit.app
```

---

## Available Servers

You can switch between these servers:

- **production** (recommended): `https://ue5-assistant-noahbutcher97.replit.app`
- **localhost**: `http://localhost:5000` (only if running backend locally)
- **dev**: `https://682ccad5-bbbd-4c0f-9115-453d448b7713-00-3n9ljd21d4w8o.janeway.replit.dev`

To switch servers:
```python
from AIAssistant.core.config import get_config
get_config().switch_server("production")  # or "localhost" or "dev"
```

---

## Troubleshooting

If you're still having issues:

1. **Check the toolbar**: AI Assistant > Launch Troubleshooter
2. **Run diagnostics**: 
   ```python
   import AIAssistant.troubleshoot.troubleshooter as ts
   ts.status()
   ```
3. **Force reconnect**:
   ```python
   import AIAssistant.troubleshoot.troubleshooter as ts
   ts.reconnect()
   ```
