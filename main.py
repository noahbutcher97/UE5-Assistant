import os
from typing import Dict, List, Optional

import openai
from fastapi import FastAPI, Request
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
async def describe_viewport(request: Request):
    """
    Receives viewport info from Unreal. Generates a grounded description of what
    the user currently sees in the editor, not general UE5 advice.
    Supports both direct (ViewportContext) and tokenized dict payloads.
    """
    try:
        raw_data = await request.json()
    except Exception as e:
        print(f"[Error] Failed to parse JSON: {e}")
        return {
            "response": f"Error reading viewport data: {e}",
            "raw_context": {}
        }

    # Try to coerce the incoming data into a proper Pydantic model
    try:
        context = ViewportContext(**raw_data)
    except Exception:
        try:
            context = ViewportContext.model_validate(raw_data)
        except Exception:
            # Fall back to a dummy structure if all else fails
            context = ViewportContext()

    # Build a focused, scene-specific prompt
    prompt = (
        "You are an Unreal Engine 5.6 Editor Assistant. "
        "The JSON below represents the user's current viewport state "
        "(camera, rotation, visible actors, and selected object). "
        "Describe what the user is seeing concisely (3–5 sentences). "
        "Base your description only on this data — do not explain UE5 concepts.\n\n"
        f"Viewport JSON:\n{context.model_dump_json(indent=2)}")

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": prompt
            }],
        )
        summary = (response.choices[0].message.content or "").strip()
    except Exception as e:
        summary = f"Error generating description: {e}"

    # Fallback if GPT produces irrelevant or empty output
    if not summary or "viewport" in summary.lower():
        add_info = context.additional_info or {}
        summary = (f"Camera at {context.camera_location or '?'} "
                   f"facing {context.camera_rotation or '?'} in level "
                   f"{add_info.get('level_name', 'Unknown')} "
                   f"with {add_info.get('total_actors', '?')} actors visible.")

    print("\n[Viewport Summary]")
    print(summary)
    print("\n--- End of Response ---\n")

    return {"response": summary, "raw_context": context.model_dump()}


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

        # ✅ Defensive checks to prevent 'NoneType' errors
        if not response or not getattr(response, "choices", None):
            return {"error": "OpenAI returned no choices."}

        first_choice = response.choices[0]
        message_content = getattr(first_choice.message, "content", None)

        if not message_content:
            return {"error": "OpenAI response was empty or invalid."}

        reply = message_content.strip()
        print(f"[AI Response] {reply}")
        return {"response": reply}

    except Exception as e:
        print(f"[ERROR] {e}")
        return {"error": str(e)}
