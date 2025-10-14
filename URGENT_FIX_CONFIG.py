"""
URGENT FIX: Manually Update UE5 Client to Working Server

Your client is stuck trying to connect to a broken URL. 
This script manually updates your config to the working server.

COPY AND PASTE THIS ENTIRE CODE INTO UE5 PYTHON CONSOLE:
"""

# === START: Copy everything below this line ===

import json
from pathlib import Path

# Get the config file location
config_dir = Path(__file__).parent / "AIAssistant" / "core"
config_file = config_dir / "ai_config.json"

print("\n" + "=" * 70)
print("🔧 EMERGENCY CONFIG FIX")
print("=" * 70)

# Load current config
if config_file.exists():
    with open(config_file, 'r') as f:
        config = json.load(f)
    print(f"📄 Current URL: {config.get('api_base_url', 'Not set')}")
else:
    config = {}
    print("📄 No config file found, creating new one")

# Update to working production server
config['api_base_url'] = 'https://ue5-assistant-noahbutcher97.replit.app'
config['active_server'] = 'production'

# Ensure SERVER_PRESETS exists and is correct (for future reference)
if 'SERVER_PRESETS' not in config:
    config['SERVER_PRESETS'] = {}
    
config['SERVER_PRESETS']['production'] = 'https://ue5-assistant-noahbutcher97.replit.app'
config['SERVER_PRESETS']['localhost'] = 'http://localhost:5000'

# Save updated config
config_dir.mkdir(parents=True, exist_ok=True)
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ Updated URL to: {config['api_base_url']}")
print("=" * 70)
print("\n🔄 Now restart the assistant:")
print("   from AIAssistant.system.auto_update import force_restart_assistant")
print("   force_restart_assistant()")
print("\n" + "=" * 70)

# === END: Copy everything above this line ===
