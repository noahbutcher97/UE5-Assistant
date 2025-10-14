"""
UE5 AI Assistant - Auto-Initialization Script
This script is automatically run by Unreal Engine on startup.
Place this file in: YourProject/Content/Python/init_unreal.py
"""

print("")
print("=" * 60)
print("🤖 UE5 AI Assistant - Auto-initializing...")
print("=" * 60)

# Force production server by default for stability
FORCE_PRODUCTION = True

try:
    # Import and run the startup configuration
    from AIAssistant.system.startup import configure_and_start
    
    # Use production server by default
    configure_and_start(force_production=FORCE_PRODUCTION)
    
except ImportError as e:
    print(f"❌ Failed to load AI Assistant: {e}")
    print("")
    print("📦 Make sure AIAssistant is installed in Content/Python/")
    print("   Run the bootstrap script to install it automatically")
    print("")
except Exception as e:
    print(f"❌ AI Assistant initialization error: {e}")
    import traceback
    traceback.print_exc()