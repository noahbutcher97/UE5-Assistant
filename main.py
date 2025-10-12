"""
UE5 AI Assistant Backend - Main Application Entry Point

A modular FastAPI application for Unreal Engine 5.6 viewport analysis and AI-powered assistance.
This file serves as the application factory, wiring together all components.
"""
import os
import openai
from fastapi import FastAPI

from app.config import load_config, save_config
from app.services import conversation
from app.routes import register_routes

# Initialize configuration
app_config = load_config()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create FastAPI app
app = FastAPI(
    title="Unreal Engine Viewport Describer",
    description=(
        "Receives Unreal viewport context and returns "
        "a natural-language description. "
        "Part of the UE5 AI Assistant Integration by Noah Butcher."
    ),
    version="3.0",
)

# Load conversation history from file
conversation.load_conversations()

# Register all routes
register_routes(app, app_config, save_config)

# Startup message
@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("🚀 UE5 AI Assistant Backend v3.0 (Modular Architecture)")
    print("=" * 60)
    print(f"✅ Configuration loaded")
    print(f"✅ Model: {app_config.get('model', 'gpt-4o-mini')}")
    print(f"✅ Response Style: {app_config.get('response_style', 'descriptive')}")
    print(f"✅ Conversation history: {len(conversation.conversation_history)} entries")
    print(f"✅ OpenAI API: {'configured' if os.getenv('OPENAI_API_KEY') else 'NOT configured'}")
    print("=" * 60)
    
    # Trigger auto-update for connected UE5 clients (after startup delay)
    import asyncio
    asyncio.create_task(trigger_auto_update_after_startup())
    
    # Start cleanup task for inactive HTTP polling clients
    asyncio.create_task(cleanup_inactive_clients_loop())

async def trigger_auto_update_after_startup():
    """Trigger auto-update for all connected UE5 clients after backend startup."""
    import asyncio
    # Wait for websocket connections to establish
    await asyncio.sleep(3)
    
    try:
        from app.websocket_manager import get_manager
        manager = get_manager()
        
        if len(manager.ue5_clients) > 0:
            print(f"\n📢 Triggering auto-update for {len(manager.ue5_clients)} connected UE5 client(s)...")
            await manager.broadcast_update_to_ue5_clients()
        else:
            print("\nℹ️ No UE5 clients connected for auto-update")
    except Exception as e:
        print(f"⚠️ Auto-update trigger failed: {e}")

async def cleanup_inactive_clients_loop():
    """Background task to cleanup inactive HTTP polling clients every 5 seconds."""
    import asyncio
    from app.websocket_manager import get_manager
    
    # Wait a bit before starting cleanup
    await asyncio.sleep(5)
    
    while True:
        try:
            manager = get_manager()
            await manager.cleanup_inactive_clients()
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
        
        # Check every 5 seconds
        await asyncio.sleep(5)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
