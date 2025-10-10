import os
from typing import Any, Dict, List, Optional

import openai
from fastapi import FastAPI, Request
from pydantic import BaseModel

# ============================================================
# CONFIGURATION
# ============================================================

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(
    title="Unreal Engine Viewport Describer",
    description=
    ("Receives Unreal viewport context and returns a natural-language "
     "description. Part of the UE5 AI Assistant Integration Project by Noah Butcher."
     ),
    version="0.2.0",
)

# ============================================================
# DATA MODEL
# ============================================================


class ViewportContext(BaseModel):
    """
    Describes the Unreal Engine editor viewport context.
    Compatible with both direct UE calls and tokenized routing.
    """
    camera_location: Optional[List[float]] = None
    camera_rotation: Optional[List[float]] = None
    visible_actors: Optional[List[str]] = None
    selected_actor: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


# ============================================================
# CORE ROUTES
# ============================================================


@app.get("/")
async def home():
    """Heartbeat route to verify API is online."""
    return {"status": "online", "message": "UE5 AI Assistant running!"}


@app.get("/test")
async def test_endpoint():
    """Quick test route."""
    return {"status": "ok", "message": "FastAPI test route reachable."}


@app.get("/ping_openai")
async def ping_openai():
    """Verifies OpenAI connectivity."""
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
            "response": response.choices[0].message.content,
        }
    except Exception as e:
        return {"openai_status": "error", "details": str(e)}


# ============================================================
# EXECUTE COMMAND
# ============================================================


@app.post("/execute_command")
async def execute_command(request: dict):
    """
    Handles general user prompts from Unreal's AI Command Console.
    This endpoint can return plain text or control tokens like
    [UE_REQUEST] describe_viewport, list_actors, get_selected_info.
    """
    user_input = request.get("prompt", "")
    if not user_input:
        return {"error": "No prompt provided."}

    try:
        # Simple keyword routing for UE actions
        lower = user_input.lower()
        if any(k in lower for k in
               ["what do i see", "viewport", "describe viewport", "scene"]):
            return {"response": "[UE_REQUEST] describe_viewport"}
        if "list actors" in lower or "list of actors" in lower:
            return {"response": "[UE_REQUEST] list_actors"}
        if "selected" in lower and ("info" in lower or "details" in lower):
            return {"response": "[UE_REQUEST] get_selected_info"}

        # Otherwise send to OpenAI for general response
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


# ============================================================
# DESCRIBE VIEWPORT (Improved)
# ============================================================


@app.post("/describe_viewport")
async def describe_viewport(request: Request):
    """
    Receives viewport info from Unreal and generates a grounded,
    scene-specific description of what the user is actually seeing
    (not generic UE5 advice).
    Supports both Pydantic model and plain dict payloads.
    """
    try:
        raw_data = await request.json()
    except Exception as e:
        print(f"[Error] Failed to parse JSON: {e}")
        return {
            "response": f"Error reading viewport data: {e}",
            "raw_context": {}
        }

    # Try to coerce dict into a Pydantic model
    try:
        context = ViewportContext(**raw_data)
    except Exception:
        try:
            context = ViewportContext.model_validate(raw_data)
        except Exception:
            context = ViewportContext()

    # Build scene-specific prompt
    prompt = (
        "You are an Unreal Engine 5.6 Editor Assistant. "
        "The following JSON represents the current viewport state — "
        "camera position, rotation, visible actors, and level info. "
        "Describe what the user is seeing in 3–5 concise sentences. "
        "Base your answer only on the data. Do NOT give UE5 tutorials or advice.\n\n"
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

    # Deterministic fallback if GPT output is too generic or empty
    if not summary or "viewport" in summary.lower():
        add_info = context.additional_info or {}
        summary = (f"Camera at {context.camera_location or '?'} "
                   f"facing {context.camera_rotation or '?'} in level "
                   f"{add_info.get('level_name', 'Unknown')} "
                   f"with {add_info.get('total_actors', '?')} visible actors.")

    print("\n[Viewport Summary]")
    print(summary)
    print("\n--- End of Response ---\n")

    return {"response": summary, "raw_context": context.model_dump()}


# ============================================================
# END OF FILE
# ============================================================
