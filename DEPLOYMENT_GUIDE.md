# 🚀 UE5 AI Assistant - Deployment Guide

## Quick Reference: File Structure

### ✅ What to Deploy to Unreal Engine
**Location:** `attached_assets/AIAssistant/`

Copy this entire folder to your UE5 project:
```
D:\UnrealProjects\5.6\UE5_Assistant\Content\Python\AIAssistant
```

**Contains:**
- All UE5 Python client modules (.py files)
- Configuration files
- Documentation folder
- No testing infrastructure

### ❌ What NOT to Deploy
**Location:** `ue5_client_tests/`

This folder stays on Replit only - it's for development testing:
- Mock Unreal Engine API
- Test runner scripts
- Simulated .uproject files
- **DO NOT copy to your UE5 project**

---

## Deployment Steps

### 1. Download from Replit
- Navigate to `attached_assets/AIAssistant/` in Replit
- Download the entire folder (or use git clone)

### 2. Deploy to Unreal Engine
```
Source: attached_assets/AIAssistant/
Target: D:\UnrealProjects\5.6\UE5_Assistant\Content\Python\AIAssistant
```
- Overwrite previous versions
- Preserve your local config changes if any

### 3. Verify Installation
In UE5 Python console:
```python
import AIAssistant.main as ai_main
ai_main.initialize()
```

---

## File Structure Overview

```
Replit Project/
├── app/                          # Backend (FastAPI server on Replit)
├── attached_assets/
│   └── AIAssistant/             # ✅ DEPLOY THIS to UE5
└── ue5_client_tests/            # ❌ REPLIT ONLY - Testing infrastructure

Your UE5 Project/
└── Content/
    └── Python/
        └── AIAssistant/         # Deployed client files go here
```

---

## Backend Connection

The UE5 client connects to the FastAPI backend at:
```
https://ue5-assistant-noahbutcher97.replit.app
```

Configure in `AIAssistant/config.py` (already set up).

---

## Troubleshooting

**Issue:** Test files (.uproject) appearing in UE5 project  
**Solution:** You copied `ue5_client_tests/` by mistake - delete it from UE5 project

**Issue:** Client can't connect to backend  
**Solution:** Check internet connection and backend URL in config

**Issue:** Missing modules error  
**Solution:** Ensure entire AIAssistant folder was copied, not just individual files

---

## Version Info

- **Backend:** v3.1 (Advanced Context & Testing Infrastructure)
- **UE5 Client:** Compatible with UE5.6+ (Python 3.11.8)
- **Last Updated:** October 2025
