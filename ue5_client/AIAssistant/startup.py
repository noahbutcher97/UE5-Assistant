"""
UE5 AI Assistant - Auto-Startup Script
Automatically configures and initializes the assistant after installation.
"""

def configure_and_start(backend_url=None):
    """Configure backend URL and start the assistant."""
    import sys
    import importlib
    
    try:
        # Step 1: Configure backend URL if provided
        if backend_url:
            print(f"🔧 Configuring backend URL: {backend_url}")
            from AIAssistant.config import get_config
            config = get_config()
            
            # Check if URL matches a known preset
            matched_preset = None
            for preset_name, preset_url in config.SERVER_PRESETS.items():
                if backend_url.strip().rstrip('/') == preset_url.strip().rstrip('/'):
                    matched_preset = preset_name
                    break
            
            if matched_preset:
                # Use preset if exact match found
                config.set("active_server", matched_preset)
                print(f"✅ Configured for {matched_preset} server")
            else:
                # Use custom URL directly
                config.set("api_base_url", backend_url)
                config.set("active_server", "custom")
                print(f"✅ Configured for custom server")
            
            print(f"✅ Backend URL: {config.api_url}")
        
        # Step 2: Reload all AIAssistant modules to pick up new config
        print("🔄 Reloading AIAssistant modules...")
        modules_to_reload = [mod for mod in list(sys.modules.keys()) if mod.startswith('AIAssistant')]
        for mod in modules_to_reload:
            del sys.modules[mod]
        
        # Step 3: Import and initialize main module
        print("🚀 Initializing AI Assistant...")
        import AIAssistant.main
        
        print("")
        print("=" * 60)
        print("✅ AI Assistant is ready!")
        print("=" * 60)
        print("💡 Usage: AIAssistant.main.send_command('your question')")
        print("🌐 Dashboard: https://ue5-assistant-noahbutcher97.replit.app/dashboard")
        print("")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()


# Auto-run if executed directly
if __name__ == "__main__":
    configure_and_start()
