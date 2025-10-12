# 🚀 UE5 Client Deployment Instructions

## Issue Diagnosis
Your UE5 installation is running **outdated code** from before the context-aware routing updates. The Replit backend has been updated, but your UE5 Python client needs to be refreshed.

## Backend ↔ UE5 Token Verification ✅

### Backend Sends These Tokens:
- `[UE_REQUEST] browse_files`
- `[UE_REQUEST] capture_blueprint`  
- `[UE_REQUEST] describe_viewport`
- `[UE_REQUEST] get_project_info` ← **NEW (missing in your UE5)**
- `[UE_REQUEST] get_selected_info`
- `[UE_REQUEST] list_actors`
- `[UE_REQUEST] list_blueprints`

### UE5 Client Has These Actions (Updated):
All backend tokens are registered ✅

---

## Deployment Steps

### Step 1: Download Updated Code
1. In Replit, navigate to `attached_assets/AIAssistant/`
2. Download the **entire folder** (all `.py` files)

### Step 2: Clean Old Installation
1. Navigate to: `D:\UnrealProjects\5.6\UE5_Assistant\Content\Python\AIAssistant\`
2. **Delete the entire `__pycache__` folder** and all `__pycache__` subfolders
3. **Delete all old `.py` files** in the AIAssistant directory

### Step 3: Deploy New Code
1. Copy/paste the downloaded `AIAssistant/` folder to:
   ```
   D:\UnrealProjects\5.6\UE5_Assistant\Content\Python\AIAssistant\
   ```
2. Overwrite all existing files

### Step 4: Restart UE5
1. **Completely close** Unreal Engine 5 editor
2. Reopen your project
3. Python will recompile with the new code

### Step 5: Test Updated Functionality
Try these commands in your AI console:

**Should trigger real data collection:**
- "what is my project called" → `get_project_info`
- "give me a breakdown of my project" → `get_project_info`
- "capture my blueprint" → `capture_blueprint`
- "show project files" → `browse_files`
- "list blueprints" → `list_blueprints`

**Should return AI guidance (no token):**
- "how do i create a c++ file" → AI response
- "what is blueprint visual scripting" → AI response

---

## Files to Deploy (From Replit)

```
attached_assets/AIAssistant/
├── __init__.py
├── main.py
├── config.py
├── api_client.py
├── context_collector.py
├── action_executor.py ← **UPDATED with get_project_info**
├── project_metadata_collector.py
├── blueprint_capture.py
├── file_collector.py
├── ui_manager.py
├── blueprint_helpers.py
└── utils.py
```

---

## Verification

After deployment, you should see in UE5 logs:
```
[ActionExecutor] ℹ️ Executing: get_project_info
[ActionExecutor] ✅ Action completed: get_project_info
```

Instead of:
```
[ActionExecutor] ❌ [UE_ERROR] Unknown action: get_project_info
```

---

## Troubleshooting

**If you still see errors:**
1. Verify `__pycache__` is completely deleted
2. Check file timestamps to ensure new files were copied
3. Try running: `import importlib; importlib.reload(AIAssistant.main)` in UE5 Python console
4. As last resort: rename old AIAssistant folder to AIAssistant_OLD, then copy fresh code

**If browse_files shows wrong paths:**
- This means old code is still loaded
- Follow Step 2 (clean old installation) more thoroughly
