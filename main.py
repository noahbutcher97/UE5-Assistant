import os
from typing import Any, Dict, List, Optional, cast

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
# EXECUTE COMMAND (Context memory + Natural language wrapping)
# ============================================================

session_messages: List[Dict[str, str]] = [{
    "role":
    "system",
    "content":
    "You are an Unreal Engine 5.6 Editor assistant."
}]


@app.post("/execute_command")
async def execute_command(request: dict):
    """
    Handles user prompts from Unreal's AI Command Console.
    Maintains short-term conversation context across turns.
    Adds natural-language rephrasing for tokenized UE actions.
    """
    user_input = request.get("prompt", "")
    if not user_input:
        return {"error": "No prompt provided."}

    try:
        lower = user_input.lower()

        # --------------------------------------------------------
        # 1️⃣ Tokenized command routing
        # --------------------------------------------------------
        if any(k in lower for k in
               ["what do i see", "viewport", "describe viewport", "scene"]):
            return {"response": "[UE_REQUEST] describe_viewport"}
        if "list actors" in lower or "list of actors" in lower:
            return {"response": "[UE_REQUEST] list_actors"}
        if "selected" in lower and ("info" in lower or "details" in lower):
            return {"response": "[UE_REQUEST] get_selected_info"}

        # --------------------------------------------------------
        # 2️⃣ Update memory
        # --------------------------------------------------------
        session_messages.append({"role": "user", "content": user_input})
        max_context_turns = 6
        user_assistant_msgs = [
            m for m in session_messages if m["role"] != "system"
        ]
        if len(user_assistant_msgs) > max_context_turns * 2:
            session_messages[:] = session_messages[:1] + user_assistant_msgs[-(
                max_context_turns * 2):]

        # --------------------------------------------------------
        # 3️⃣ Build typed payload for OpenAI
        # --------------------------------------------------------
        messages_payload = [{
            "role": m["role"],
            "content": m["content"]
        } for m in session_messages if "role" in m and "content" in m]

        # --------------------------------------------------------
        # 4️⃣ Send initial user prompt to OpenAI
        # --------------------------------------------------------
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=cast(List[Any], messages_payload),
        )

        reply = (response.choices[0].message.content or "").strip()
        print(f"[AI Response] {reply}")

        # --------------------------------------------------------
        # 5️⃣ Handle UE-request tokens (rephrase factual responses)
        # --------------------------------------------------------
        if reply.startswith("[UE_REQUEST]"):
            token = reply.replace("[UE_REQUEST]", "").strip()
            print(f"[AIConsole] Detected UE token: {token}")
            # Return token for Unreal to execute (it will send data back)
            return {"response": f"[UE_REQUEST] {token}"}

        # --------------------------------------------------------
        # 6️⃣ Append assistant reply to memory and return
        # --------------------------------------------------------
        session_messages.append({"role": "assistant", "content": reply})
        return {"response": reply}

    except Exception as e:
        print(f"[ERROR] {e}")
        return {"error": str(e)}


# ============================================================
#  ADDITIONAL ENDPOINT: POST-TOKEN NATURAL-LANGUAGE WRAPPER
# ============================================================


@app.post("/wrap_natural_language")
async def wrap_natural_language(request: dict):
    """
    Takes a factual string from UE (like a viewport summary)
    and rewrites it conversationally for the user.
    """
    summary_text = request.get("summary", "")
    if not summary_text:
        return {"error": "No summary text provided."}

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role":
                    "system",
                    "content":
                    ("You are an Unreal Editor assistant speaking directly to the user. "
                     "Rephrase the following factual scene summary into natural, conversational language. "
                     "Preserve accuracy but make it feel like you’re describing the scene casually."
                     ),
                },
                {
                    "role": "user",
                    "content": summary_text
                },
            ],
        )
        wrapped = response.choices[0].message.content.strip()
        print(f"[Natural Wrapper] {wrapped}")
        return {"response": wrapped}
    except Exception as e:
        print(f"[ERROR in wrap_natural_language]: {e}")
        return {"response": summary_text}


# ============================================================
# DESCRIBE VIEWPORT (Improved + Stable)
# ============================================================


@app.post("/describe_viewport")
async def describe_viewport(request: Request):
    """
    Receives viewport info from Unreal and generates a grounded,
    scene-specific description of what the user is actually seeing
    (not generic UE5 advice).
    Supports both Pydantic model and plain dict payloads.
    """
    # ------------------------------------------------------------
    # 1️⃣ Parse the incoming JSON from Unreal
    # ------------------------------------------------------------
    try:
        raw_data = await request.json()
    except Exception as e:
        print(f"[Error] Failed to parse JSON: {e}")
        return {
            "response": f"Error reading viewport data: {e}",
            "raw_context": {}
        }

    # ------------------------------------------------------------
    # 2️⃣ Attempt to coerce into Pydantic ViewportContext
    # ------------------------------------------------------------
    try:
        context = ViewportContext(**raw_data)
    except Exception:
        try:
            context = ViewportContext.model_validate(raw_data)
        except Exception:
            context = ViewportContext()

    # ------------------------------------------------------------
    # 3️⃣ Build the summarization prompt
    # ------------------------------------------------------------
    prompt = (
        "You are an Unreal Engine 5.6 Editor Assistant. "
        "The following JSON represents the current viewport state — "
        "camera position, rotation, visible actors, and level info. "
        "Describe what the user is seeing in 3–5 concise sentences. "
        "Focus on what the scene looks like, not the technical parameters. "
        "Base your answer only on the data. Do NOT give UE5 tutorials or advice.\n\n"
        f"Viewport JSON:\n{context.model_dump_json(indent=2)}")

    # ------------------------------------------------------------
    # 4️⃣ Send to OpenAI to generate the natural description
    # ------------------------------------------------------------
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role":
                    "system",
                    "content":
                    ("You are an Unreal Engine scene interpreter. "
                     "Summarize viewport context into natural, descriptive language. "
                     "Do not use technical jargon unless directly relevant. "
                     "Do not output JSON or give editing advice."),
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
        )
        summary = (response.choices[0].message.content or "").strip()
    except Exception as e:
        summary = f"Error generating description: {e}"

    # ------------------------------------------------------------
    # 5️⃣ Fallback logic — only trigger when summary is missing or invalid
    # ------------------------------------------------------------
    if not summary or summary.lower().strip() in [
            "", "none", "n/a", "no data"
    ]:
        add_info = context.additional_info or {}
        summary = (f"Camera at {context.camera_location or '?'} "
                   f"facing {context.camera_rotation or '?'} in level "
                   f"{add_info.get('level_name', 'Unknown')} "
                   f"with {add_info.get('total_actors', '?')} visible actors.")

    # ------------------------------------------------------------
    # 6️⃣ Logging and response
    # ------------------------------------------------------------
    print("\n[Viewport Summary]")
    print(summary)
    print("\n--- End of Response ---\n")

    return {"response": summary, "raw_context": context.model_dump()}


# ============================================================
# END OF FILE
# ============================================================
