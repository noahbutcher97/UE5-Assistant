"""
QUICK FIX: Switch UE5 Client to CURRENT Production Server

This fixes the issue where your client connects to an old server deployment.
Run this in UE5's Python console to connect to the CORRECT backend server.

Current Production Server: https://workspace-noahbutcher97.replit.app
"""

def fix_server_connection():
    """Switch client to production server and reconnect."""
    try:
        import unreal
        
        print("=" * 60)
        print("🔧 Fixing Server Connection...")
        print("=" * 60)
        
        # Import config
        from AIAssistant.core.config import get_config
        config = get_config()
        
        # Show current server
        current = config.get("active_server", "unknown")
        current_url = config.api_url
        print(f"Current Server: {current}")
        print(f"Current URL: {current_url}")
        print()
        
        # Switch to production
        print("Switching to production server...")
        config.set("active_server", "production")
        print(f"✅ Set to production: {config.api_url}")
        print()
        
        # Restart the assistant to apply changes
        print("Restarting assistant with new server...")
        from AIAssistant.system.auto_update import force_restart_assistant
        force_restart_assistant()
        
        print("=" * 60)
        print("✅ Done! Client should now connect to production server")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


# Auto-run when imported
if __name__ == "__main__":
    fix_server_connection()
else:
    # Also run when imported (for convenience)
    fix_server_connection()
