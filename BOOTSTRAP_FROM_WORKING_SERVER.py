"""
BOOTSTRAP FROM WORKING SERVER

Download and install the latest UE5 client from the working production server.
This will replace your old client with the correct one.

PASTE THIS INTO UE5 PYTHON CONSOLE:
"""

import requests
import zipfile
import io
from pathlib import Path
import unreal

print("\n" + "=" * 70)
print("📥 DOWNLOADING LATEST CLIENT FROM WORKING SERVER")
print("=" * 70)

# Working production server
server_url = "https://ue5-assistant-noahbutcher97.replit.app"
download_url = f"{server_url}/api/download_client"

print(f"📡 Server: {server_url}")
print(f"⬇️  Downloading from: {download_url}")

try:
    # Download the client ZIP
    response = requests.get(download_url, timeout=30)
    response.raise_for_status()
    
    print(f"✅ Downloaded {len(response.content)} bytes")
    
    # Extract to Content/Python
    project_dir = Path(unreal.Paths.project_dir())
    target_dir = project_dir / "Content" / "Python"
    
    print(f"📂 Extracting to: {target_dir}")
    
    # Extract ZIP
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        zf.extractall(target_dir)
    
    print("✅ Client files extracted successfully!")
    
    # Create config with correct URL
    config_file = target_dir / "AIAssistant" / "core" / "ai_config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    config = {
        "api_base_url": server_url,
        "active_server": "production"
    }
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Config created: {server_url}")
    print("=" * 70)
    print("\n🔄 Restarting UE5 to load new client...")
    print("   (Or manually restart: File > Exit, then reopen UE5)")
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Manual download:")
    print(f"   1. Go to: {download_url}")
    print(f"   2. Save the ZIP file")
    print(f"   3. Extract to: {project_dir / 'Content' / 'Python'}")
