# UE5 Client Testing Environment

⚠️ **DO NOT COPY THIS FOLDER TO YOUR UNREAL ENGINE PROJECT** ⚠️

## Purpose

This directory contains **Replit-only testing infrastructure** for validating UE5 Python client code without requiring an actual Unreal Engine 5 editor installation.

## Contents

- **`mock_unreal.py`**: Simulates the entire Unreal Engine Python API (unreal module)
- **`test_runner.py`**: Test harness for executing UE5 client modules
- **`mock_project/`**: Simulated UE5 project directory structure with .uproject file
- **`DEBUG_TEST.py`**: Debug utilities and test scripts

## Usage

This testing environment is used **exclusively on Replit** to:
1. Validate UE5 client code changes before deployment
2. Test collector modules (project_metadata_collector.py, file_collector.py, etc.)
3. Verify action execution logic without UE5 editor
4. Debug issues in a controlled environment

## Workflow

**For Development (Replit):**
```bash
cd ue5_client_tests
python test_runner.py
```

**For Production (Your UE5 Project):**
- Only copy the `attached_assets/AIAssistant/` directory to your Unreal project
- **DO NOT** include this `ue5_client_tests` folder

## File Structure

```
Replit Project Root/
├── app/                          # FastAPI backend
├── attached_assets/
│   └── AIAssistant/             # ✅ COPY THIS to UE5 Content/Python/AIAssistant
└── ue5_client_tests/            # ❌ DO NOT COPY - Replit testing only
    ├── mock_unreal.py
    ├── test_runner.py
    └── mock_project/
```

## UE5 Deployment Path

Your correct workflow:
1. Download `attached_assets/AIAssistant/` from Replit
2. Paste to: `D:\UnrealProjects\5.6\UE5_Assistant\Content\Python\AIAssistant`
3. Overwrite previous versions
4. **Skip this ue5_client_tests folder entirely**

---
*This testing infrastructure allows development and validation of UE5 integration code without requiring a live Unreal Engine installation.*
