import os
from typing import Any, Dict, List, Optional, cast

import openai
from fastapi import FastAPI, Request
from pydantic import BaseModel

# ============================================================
# CONFIGURATION
# ============================================================

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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
    Compatible with modular AIAssistant v2.0 structure.
    """
    # New v2.0 structure (modular)
    camera: Optional[Dict[str, Any]] = None
    actors: Optional[Dict[str, Any]] = None
    lighting: Optional[Dict[str, Any]] = None
    environment: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None
    
    # Legacy v1.0 fields (backward compatibility)
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
            model=MODEL_NAME,
            messages=[{
                "role": "user",
                "content": "Say 'pong'"
            }],
        )
        return {
            "openai_status": "connected",
            "response": response.choices[0].message.content or "pong",
        }
    except Exception as e:
        return {"openai_status": "error", "details": str(e)}


# ============================================================
# EXECUTE COMMAND (Context memory + Natural language wrapping)
# ============================================================

# NOTE: session_messages is shared global state for single-user UE integration
# For multi-user deployments, consider session management per user/connection
session_messages: List[Dict[str, str]] = [{
    "role":
    "system",
    "content": (
        "You are a technical documentation system for Unreal Engine 5.6. "
        "Generate structured technical prose describing editor state and scene contents. "
        "Use precise terminology, include specific names and values, connect information logically. "
        "Write in third-person declarative style. Avoid conversational phrasing, questions, or subjective language. "
        "Format output as coherent technical paragraphs, not chat responses."
    )
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
            model=MODEL_NAME,
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
    and converts it to structured technical prose.
    """
    summary_text = request.get("summary", "")
    if not summary_text:
        return {"error": "No summary text provided."}

    try:
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role":
                    "system",
                    "content":
                    ("Convert the following technical data into structured technical prose. "
                     "Organize information into logical groups (spatial layout, actors by type, lighting setup). "
                     "Use precise terminology and include specific names and values. "
                     "Connect statements with technical transitions. "
                     "Write as technical documentation, not conversational text. "
                     "No questions, no helpful tone, no subjective descriptions."
                     ),
                },
                {
                    "role": "user",
                    "content": summary_text
                },
            ],
        )
        wrapped = (response.choices[0].message.content or "").strip()
        print(f"[Natural Wrapper] {wrapped}")
        return {"response": wrapped}
    except Exception as e:
        print(f"[ERROR in wrap_natural_language]: {e}")
        return {"response": summary_text}


# ============================================================
# DESCRIBE VIEWPORT (PEP8-Compliant + Pyright-Safe)
# ============================================================


@app.post("/describe_viewport")
async def describe_viewport(request: Request):
    """
    Receives viewport info from Unreal and generates a grounded,
    scene-specific description of what the user is actually seeing.
    Supports style = "technical" or "natural".
    Includes offline fallbacks that remain informative and readable.
    """
    # ------------------------------------------------------------
    # 1️⃣ Parse incoming JSON
    # ------------------------------------------------------------
    try:
        raw_data: dict[str, Any] = await request.json()
    except Exception as e:
        print(f"[Error] Failed to parse JSON: {e}")
        return {
            "response": f"Error reading viewport data: {e}",
            "raw_context": {},
        }

    style = str(raw_data.get("style", "technical")).lower()

    # ------------------------------------------------------------
    # 2️⃣ Coerce into ViewportContext
    # ------------------------------------------------------------
    try:
        context = ViewportContext(**raw_data)
    except Exception:
        try:
            context = ViewportContext.model_validate(raw_data)
        except Exception:
            context = ViewportContext()

    # ------------------------------------------------------------
    # 3️⃣ Build summarization prompt
    # ------------------------------------------------------------
    if style == "technical":
        prompt_intro = (
            "Analyze the viewport JSON data and generate a comprehensive technical description. "
            "The data structure includes:\n"
            "- camera: {location: [x,y,z], rotation: [pitch,yaw,roll]} for viewport position\n"
            "- actors: {total, names[], types{}} for scene contents\n"
            "- lighting: {directional_lights[], point_lights[], spot_lights[]} for illumination\n"
            "- environment: {fog[], post_process_volumes[], landscape} for atmospheric elements\n"
            "- selection: {count, actors[]} for currently selected objects\n\n"
            "Structure the response as flowing prose paragraphs that systematically cover:\n"
            "1. Camera spatial configuration (position coordinates from location, rotation angles, viewing direction)\n"
            "2. Complete scene inventory (actor counts, types, and specific names from actors data)\n"
            "3. Lighting configuration (directional, point, and spot lights with their properties)\n"
            "4. Environmental systems (fog, post-process volumes, landscape elements)\n"
            "5. Selection state (selected actors with their details)\n\n"
            "Use complete sentences that connect related information. Include all specific names, "
            "coordinate values, class types, and quantitative data. Describe relationships between "
            "elements. Write as detailed technical documentation that thoroughly explains the scene "
            "composition. Avoid bullet points or fragmented lists - synthesize information into "
            "coherent explanatory paragraphs. Maintain factual, objective tone without subjective "
            "qualifiers or casual language."
        )
    else:
        prompt_intro = (
            "Analyze the viewport JSON data and generate a detailed technical description. "
            "The data includes camera (location/rotation), actors (counts/types/names), "
            "lighting (directional/point/spot lights), environment (fog/post-process/landscape), "
            "and selection state. Write complete sentences that systematically describe all elements. "
            "Include specific names, values, and technical classifications. Connect related information "
            "into flowing prose paragraphs. Provide comprehensive coverage of all scene elements. "
            "Maintain objective, informative tone using precise terminology. "
            "Avoid conversational phrasing, subjective descriptors, and fragmented lists."
        )

    prompt = (f"{prompt_intro}\n\nViewport JSON:\n"
              f"{context.model_dump_json(indent=2)}")

    # ------------------------------------------------------------
    # 4️⃣ System message (matches style)
    # ------------------------------------------------------------
    if style == "technical":
        system_msg = (
            "You are a technical documentation system for Unreal Engine 5.6. "
            "Generate comprehensive descriptions using flowing prose paragraphs, not lists or bullet points. "
            "Systematically analyze and describe all scene elements: camera configuration, actor inventory, "
            "spatial relationships, environmental systems, and selection state. Include every specific name, "
            "coordinate value, class type, and quantitative measurement. Connect related information into "
            "coherent explanatory sentences. Write as detailed technical documentation that thoroughly "
            "explains scene composition. Use precise terminology and factual statements. Never use "
            "conversational tone, subjective qualifiers, casual language, or interpretive descriptions. "
            "If data is missing, state it explicitly as a technical observation."
        )
    else:
        system_msg = (
            "You are a technical documentation system for Unreal Engine 5.6. "
            "Generate detailed descriptions using complete sentences and flowing prose, not fragmented lists. "
            "Describe all scene elements comprehensively: camera state, visible actors, spatial organization, "
            "environmental components. Include specific names, values, and technical classifications. "
            "Connect information into coherent paragraphs. Maintain objective, informative tone with precise "
            "terminology. Avoid conversational phrasing, subjective descriptors, and casual language."
        )

    # ------------------------------------------------------------
    # 5️⃣ Send to OpenAI
    # ------------------------------------------------------------
    try:
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_msg
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
        )
        msg_content = response.choices[0].message.content
        summary: str = msg_content.strip() if msg_content else ""
    except Exception as e:
        print(f"[Error] OpenAI call failed: {e}")
        summary = ""

    # ------------------------------------------------------------
    # 6️⃣ Multi-tier fallback logic (supports v2.0 structure)
    # ------------------------------------------------------------
    if not summary or len(summary.split()) < 4:
        # Try v2.0 structure first
        camera_data = context.camera or {}
        actors_data = context.actors or {}
        lighting_data = context.lighting or {}
        env_data = context.environment or {}
        selection_data = context.selection or {}
        
        # Extract values with fallbacks
        cam_loc = camera_data.get("location", context.camera_location or [0,0,0])
        cam_rot = camera_data.get("rotation", context.camera_rotation or [0,0,0])
        total = actors_data.get("total", len(context.visible_actors or []))
        lvl = actors_data.get("level", "Unknown")
        
        # Tier 1 – minimal technical fallback
        summary = (f"Camera at {cam_loc} facing {cam_rot} "
                   f"in level '{lvl}' with approximately "
                   f"{total} visible actors.")
        print("[Fallback] Basic camera-level summary used.")

        # Tier 2 – offline natural rephrase using v2.0 data
        try:
            actor_names = actors_data.get("names", context.visible_actors or [])
            selected_actors = selection_data.get("actors", [])
            
            has_landscape = env_data.get("landscape") is not None
            has_lights = (
                len(lighting_data.get("directional_lights", [])) > 0 or
                len(lighting_data.get("point_lights", [])) > 0 or
                len(lighting_data.get("spot_lights", [])) > 0
            )
            has_fog = len(env_data.get("fog", [])) > 0

            natural_parts: list[str] = []
            if has_landscape:
                natural_parts.append("a landscape environment")
            if has_lights:
                num_lights = (
                    len(lighting_data.get("directional_lights", [])) +
                    len(lighting_data.get("point_lights", [])) +
                    len(lighting_data.get("spot_lights", []))
                )
                natural_parts.append(f"{num_lights} light sources")
            if has_fog:
                natural_parts.append("fog or atmospheric effects")

            scene_desc = (", ".join(natural_parts)
                          if natural_parts else "various actors")

            readable = (
                f"The camera is positioned at {cam_loc}, looking toward "
                f"{cam_rot}, viewing {scene_desc} within level '{lvl}'. "
                f"There are {total} visible actors in the scene.")
            
            if selected_actors:
                selected_names = [a.get("name", "Unknown") for a in selected_actors[:3]]
                if len(selected_names) == 1:
                    readable += f" Currently selected: {selected_names[0]}."
                else:
                    readable += f" Currently selected: {', '.join(selected_names)}."

            summary = readable
            print("[Offline Fallback] Generated descriptive summary offline (v2.0 data).")
        except Exception as e:
            print(f"[Offline fallback failed]: {e}")

    # ------------------------------------------------------------
    # 7️⃣ Logging and response
    # ------------------------------------------------------------
    print("\n[Viewport Summary]")
    print(summary)
    print("\n--- End of Response ---\n")

    return {"response": summary, "raw_context": context.model_dump()}


# ============================================================
# END OF FILE
# ============================================================
