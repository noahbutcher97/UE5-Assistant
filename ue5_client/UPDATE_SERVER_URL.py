"""
UPDATE SERVER URL - Connect to Current Production Server

Your client is connecting to an OLD server. This script switches it to the CURRENT one.
Run this in UE5's Python Console to fix the dashboard connection.
"""

def update_to_current_server():
    """Update client to connect to current production server."""
    try:
        import unreal
        
        print("=" * 70)
        print("🔧 UPDATING TO CURRENT PRODUCTION SERVER")
        print("=" * 70)
        print()
        print("⚠️ Your client was connecting to an OLD server deployment!")
        print("   Old: https://ue5-assistant-noahbutcher97.replit.app")
        print("   Current: https://workspace-noahbutcher97.replit.app")
        print()
        
        # Import config
        from AIAssistant.core.config import get_config
        config = get_config()
        
        # Show current setting
        current_url = config.api_url
        print(f"Current URL: {current_url}")
        print()
        
        # Update to correct production URL
        print("Updating production URL...")
        config.SERVER_PRESETS["production"] = "https://workspace-noahbutcher97.replit.app"
        config.set("api_base_url", "https://workspace-noahbutcher97.replit.app")
        config.set("active_server", "production")
        config.save()
        print(f"✅ Updated to: {config.api_url}")
        print()
        
        # Restart assistant to apply changes
        print("Restarting assistant to reconnect...")
        from AIAssistant.system.auto_update import force_restart_assistant
        force_restart_assistant()
        
        print("=" * 70)
        print("✅ DONE! Your client should now connect to the current server")
        print("   Dashboard will now show your project as connected!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("💡 Manual fix: Set config.set('api_base_url', 'https://workspace-noahbutcher97.replit.app')")


# Auto-run when imported
if __name__ == "__main__":
    update_to_current_server()
else:
    update_to_current_server()
