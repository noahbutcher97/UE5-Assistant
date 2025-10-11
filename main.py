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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
