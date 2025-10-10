import os
from typing import Dict, List, Optional

import openai
from fastapi import FastAPI
from pydantic import BaseModel

# ============================================================
# CONFIGURATION
# ============================================================

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI(
    title="Unreal Engine Viewport Describer",
    description=
    ("Receives Unreal viewport context and returns a natural-language description. "
     "Part of the UE5 AI Assistant Integration Project by Noah Butcher."),
    version="0.1.1",
)

# ============================================================
# DATA MODEL
# ============================================================


class ViewportContext(BaseModel):
    """
    Data model describing the Unreal Engine editor viewport context.
    """
    camera_location: Optional[List[float]] = None
    camera_rotation: Optional[List[float]] = None
    visible_actors: Optional[List[str]] = None
    selected_actor: Optional[str] = None
    additional_info: Optional[Dict] = None


# ============================================================
# MAIN ENDPOINT
# ============================================================


@app.post("/describe_viewport")
async def describe_viewport(context: ViewportContext):
    """
    Receives viewport info from Unreal. Uses OpenAI to describe what the user
    is likely seeing or debugging in the editor.
    """

    prompt = (
        "You are an Unreal Engine 5.6 Editor assistant. "
        "Given the following viewport data, describe in plain, natural language "
        "what the user is likely seeing — focusing on level layout, camera position, "
        "and notable actor context. Use concise, professional phrasing suitable for "
        "debugging or level design documentation.\n\n"
        f"{context.model_dump_json(indent=2)}")

    print("\n[Viewport Received]")
    print(context.model_dump_json(indent=2))

    # Default response in case of error
    summary = "No description generated."

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": prompt
            }],
        )

        # Extract description text safely
        summary = (response.choices[0].message.content or "").strip()

    except Exception as e:
        summary = f"Error generating description: {e}"

    print("\n[Generated Description]")
    print(summary)
    print("\n--- End of Response ---\n")

    # Convert context to dict before returning to avoid Pydantic serialization issues
    return {"description": summary, "raw_context": context.model_dump()}


# ============================================================
# SIMPLE HOMEPAGE
# ============================================================


@app.get("/")
async def home():
    """
    Simple heartbeat route to verify the API is online.
    """
    return {"status": "online", "message": "UE5 AI Assistant running!"}


# ============================================================
# OPTIONAL DEBUG / TEST ROUTES
# ============================================================


@app.get("/test")
async def test_endpoint():
    """
    Quick test route to verify server connectivity.
    """
    return {"status": "ok", "message": "FastAPI test route reachable."}


@app.get("/ping_openai")
async def ping_openai():
    """
    Optional test route to verify OpenAI connectivity.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": "Say 'pong'"
            }],
        )
        return {
            "openai_status": "connected",
            "response": response.choices[0].message.content
        }
    except Exception as e:
        return {"openai_status": "error", "details": str(e)}


# ============================================================
# EXECUTE COMMAND
# ============================================================
@app.post("/execute_command")
async def execute_command(request: dict):
    user_input = request.get("prompt", "")
    if not user_input:
        return {"error": "No prompt provided."}

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an Unreal Engine 5 assistant."
                },
                {
                    "role": "user",
                    "content": user_input
                },
            ],
        )
        reply = response.choices[0].message.content.strip()
        return {"response": reply}
    except Exception as e:
        return {"error": str(e)}
