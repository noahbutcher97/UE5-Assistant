import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import openai
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

# ============================================================
# CONFIGURATION MANAGEMENT
# ============================================================

# Config file path
CONFIG_FILE = Path("config.json")

# Response style presets
RESPONSE_STYLES = {
    "descriptive": {
        "name": "Descriptive (Default)",
        "prompt_modifier": "Provide clear, descriptive technical prose that explains what you see in the viewport. Be factual and specific."
    },
    "technical": {
        "name": "Technical/Precise",
        "prompt_modifier": "Use precise technical terminology and structured documentation format. Include exact values, object types, and technical specifications."
    },
    "natural": {
        "name": "Natural/Conversational",
        "prompt_modifier": "Respond in a natural, conversational tone as if explaining to a colleague. Be friendly but informative."
    },
    "balanced": {
        "name": "Balanced",
        "prompt_modifier": "Balance technical accuracy with readability. Use clear language while maintaining precision."
    },
    "concise": {
        "name": "Concise/Brief",
        "prompt_modifier": "Be brief and to-the-point. Summarize key information without unnecessary detail."
    },
    "detailed": {
        "name": "Detailed/Verbose",
        "prompt_modifier": "Provide comprehensive, detailed analysis of all aspects. Include context, implications, and suggestions."
    }
}

# Default configuration
DEFAULT_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_context_turns": 6,
    "timeout": 25,
    "max_retries": 3,
    "retry_delay": 2.5,
    "verbose": False,
    "response_style": "descriptive"
}

# Global config (loaded from file or defaults)
app_config: Dict[str, Any] = {}


def load_config() -> Dict[str, Any]:
    """Load configuration from file or use defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                return {**DEFAULT_CONFIG, **config}
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")


# Load initial config
app_config = load_config()

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = app_config.get("model", "gpt-4o-mini")

app = FastAPI(
    title="Unreal Engine Viewport Describer",
    description=(
        "Receives Unreal viewport context and returns "
        "a natural-language description. "
        "Part of the UE5 AI Assistant Integration by Noah Butcher."
    ),
    version="2.0",
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


class ConversationEntry(BaseModel):
    """A single conversation exchange."""
    timestamp: str
    user_input: str
    assistant_response: str
    command_type: str  # "execute_command", "describe_viewport", etc.
    metadata: Optional[Dict[str, Any]] = None


class ConfigUpdate(BaseModel):
    """Configuration update model."""
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_context_turns: Optional[int] = None
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    retry_delay: Optional[float] = None
    verbose: Optional[bool] = None
    response_style: Optional[str] = None


# ============================================================
# CONVERSATION HISTORY STORAGE
# ============================================================

# In-memory conversation history (last 100 entries)
conversation_history: List[Dict[str, Any]] = []
MAX_HISTORY_SIZE = 100


def add_to_history(
    user_input: str,
    response: str,
    cmd_type: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """Add a conversation entry to history."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_input": user_input,
        "assistant_response": response,
        "command_type": cmd_type,
        "metadata": metadata or {}
    }
    conversation_history.append(entry)
    
    # Keep only last MAX_HISTORY_SIZE entries
    if len(conversation_history) > MAX_HISTORY_SIZE:
        conversation_history.pop(0)


# ============================================================
# CORE ROUTES
# ============================================================


@app.get("/")
async def home():
    """Redirect to dashboard."""
    return RedirectResponse(url="/dashboard", status_code=307)


@app.get("/health")
async def health_check():
    """Health check endpoint for API monitoring."""
    return {"status": "online", "message": "UE5 AI Assistant running!", "version": "2.0"}


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

def get_system_message() -> str:
    """Generate system message with current response style."""
    current_style = app_config.get("response_style", "descriptive")
    style_modifier = RESPONSE_STYLES.get(current_style, RESPONSE_STYLES["descriptive"])["prompt_modifier"]
    
    base_msg = (
        "You are an AI assistant for Unreal Engine 5.6. "
        "Generate structured prose describing editor state and scene contents. "
        "Use terminology appropriate for UE5, include specific names and values. "
    )
    return base_msg + style_modifier

session_messages: List[Dict[str, str]] = [{
    "role": "system",
    "content": get_system_message()
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
        max_context_turns = app_config.get("max_context_turns", 6)
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
            temperature=app_config.get("temperature", 0.7),
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
        
        # Log to conversation history
        add_to_history(user_input, reply, "execute_command")
        
        return {"response": reply}

    except Exception as e:
        print(f"[ERROR] {e}")
        error_msg = str(e)
        add_to_history(user_input, f"ERROR: {error_msg}", "execute_command", {"error": True})
        return {"error": error_msg}


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
            temperature=app_config.get("temperature", 0.7),
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
    # 4️⃣ System message with configurable response style
    # ------------------------------------------------------------
    # Get response style from config
    current_style = app_config.get("response_style", "descriptive")
    style_modifier = RESPONSE_STYLES.get(current_style, RESPONSE_STYLES["descriptive"])["prompt_modifier"]
    
    # Base system message
    base_system_msg = (
        "You are an AI assistant for Unreal Engine 5.6. "
        "Generate descriptions using complete sentences and flowing prose, not fragmented lists. "
        "Describe scene elements: camera state, visible actors, spatial organization, "
        "environmental components. Include specific names, values, and technical classifications. "
    )
    
    # Combine with style modifier
    system_msg = base_system_msg + style_modifier

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
            temperature=app_config.get("temperature", 0.7),
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
    
    # Log to conversation history
    user_prompt = "Describe viewport"
    # Extract metadata from context (already parsed above)
    actors_count = (
        context.actors.get("total", 0) if context.actors else 0
    )
    has_selection = (
        context.selection.get("count", 0) > 0
        if context.selection else False
    )
    metadata = {
        "actors_count": actors_count,
        "has_selection": has_selection
    }
    add_to_history(
        user_prompt, summary, "describe_viewport", metadata
    )

    return {"response": summary, "raw_context": context.model_dump()}


# ============================================================
# CONVERSATION DASHBOARD API
# ============================================================

@app.get("/api/conversations")
async def get_conversations(limit: int = 50):
    """Get recent conversation history for dashboard."""
    # Return most recent entries first
    recent = conversation_history[-limit:] if len(conversation_history) > limit else conversation_history
    return {
        "conversations": list(reversed(recent)),
        "total": len(conversation_history),
        "max_size": MAX_HISTORY_SIZE
    }


@app.get("/api/config")
async def get_config():
    """Get current configuration."""
    return {
        "config": app_config,
        "defaults": DEFAULT_CONFIG,
        "response_styles": RESPONSE_STYLES,
        "available_models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    }


@app.post("/api/config")
async def update_config(updates: ConfigUpdate):
    """Update configuration settings."""
    global app_config, MODEL_NAME, session_messages
    
    # Update config with provided values
    update_dict = updates.model_dump(exclude_none=True)
    
    for key, value in update_dict.items():
        app_config[key] = value
    
    # Update MODEL_NAME if model changed (CRITICAL: must update global)
    if "model" in update_dict:
        MODEL_NAME = app_config["model"]
    
    # Update system message if response_style changed
    if "response_style" in update_dict:
        session_messages[0]["content"] = get_system_message()
    
    # Save to file
    save_config(app_config)
    
    return {
        "success": True,
        "message": "Configuration updated successfully",
        "config": app_config
    }


@app.post("/api/log_conversation")
async def log_conversation(entry: ConversationEntry):
    """Manually log a conversation (for UE5 client if needed)."""
    add_to_history(
        entry.user_input,
        entry.assistant_response,
        entry.command_type,
        entry.metadata
    )
    return {"status": "logged", "total_entries": len(conversation_history)}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the conversation dashboard HTML."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UE5 AI Assistant - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
        }
        
        .stats {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat-card {
            flex: 1;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-card .number {
            font-size: 2em;
            font-weight: bold;
        }
        
        .stat-card .label {
            opacity: 0.9;
            font-size: 0.9em;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .tab {
            background: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .tab:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        }
        
        .tab-content {
            display: none;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .tab-content.active {
            display: block;
        }
        
        .conversation-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .conversation-item {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s;
        }
        
        .conversation-item:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #667eea;
        }
        
        .conversation-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .timestamp {
            color: #999;
            font-size: 0.85em;
        }
        
        .command-type {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
        }
        
        .user-input {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 12px;
            border-left: 3px solid #667eea;
        }
        
        .user-input strong {
            color: #667eea;
        }
        
        .assistant-response {
            background: #f9f9f9;
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #764ba2;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .assistant-response strong {
            color: #764ba2;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        
        .empty-state svg {
            width: 80px;
            height: 80px;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: transform 0.2s;
        }
        
        .refresh-btn:hover {
            transform: scale(1.05);
        }
        
        .auto-refresh {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #666;
            font-size: 14px;
        }
        
        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .setting-group {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        .setting-label {
            display: flex;
            flex-direction: column;
            gap: 5px;
            margin-bottom: 12px;
        }
        
        .setting-description {
            font-size: 13px;
            color: #666;
            font-weight: normal;
        }
        
        .setting-input, .setting-slider {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .setting-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .setting-slider {
            padding: 0;
            height: 8px;
            cursor: pointer;
        }
        
        .save-btn, .reset-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .save-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            flex: 1;
        }
        
        .save-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        .reset-btn {
            background: #f0f0f0;
            color: #666;
            flex: 1;
        }
        
        .reset-btn:hover {
            background: #e0e0e0;
        }
        
        .save-status {
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .save-status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .save-status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 UE5 AI Assistant Dashboard</h1>
            <p>Real-time conversation monitoring and analytics</p>
            <div class="stats">
                <div class="stat-card">
                    <div class="number" id="total-conversations">0</div>
                    <div class="label">Total Conversations</div>
                </div>
                <div class="stat-card">
                    <div class="number" id="recent-conversations">0</div>
                    <div class="label">Recent (Last 50)</div>
                </div>
                <div class="stat-card">
                    <div class="number" id="max-storage">100</div>
                    <div class="label">Max Storage</div>
                </div>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('dashboard')">📊 Dashboard</button>
            <button class="tab" onclick="showTab('settings')">⚙️ Settings</button>
            <button class="tab" onclick="showTab('api')">🔧 API Info</button>
            <button class="tab" onclick="showTab('about')">ℹ️ About</button>
        </div>
        
        <div id="dashboard" class="tab-content active">
            <div class="controls">
                <h2>Recent Conversations</h2>
                <div style="display: flex; gap: 15px; align-items: center;">
                    <label class="auto-refresh">
                        <input type="checkbox" id="auto-refresh" checked>
                        Auto-refresh (5s)
                    </label>
                    <button class="refresh-btn" onclick="loadConversations()">
                        <span>🔄</span> Refresh Now
                    </button>
                </div>
            </div>
            <div id="conversation-list" class="conversation-list">
                <div class="empty-state">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                    </svg>
                    <p>No conversations yet. Start using the AI Assistant in Unreal Engine!</p>
                </div>
            </div>
        </div>
        
        <div id="settings" class="tab-content">
            <h2>⚙️ Configuration Settings</h2>
            <p style="margin: 15px 0; color: #666;">
                Configure AI behavior and response style in real-time without code changes
            </p>
            
            <div style="display: grid; gap: 25px; margin-top: 30px;">
                <!-- AI Model Selection -->
                <div class="setting-group">
                    <label class="setting-label">
                        <strong>🤖 AI Model</strong>
                        <span class="setting-description">Choose the GPT model for responses</span>
                    </label>
                    <select id="model" class="setting-input">
                        <option value="gpt-4o-mini">GPT-4o Mini (Fast & Efficient)</option>
                        <option value="gpt-4o">GPT-4o (Balanced)</option>
                        <option value="gpt-4-turbo">GPT-4 Turbo (Powerful)</option>
                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Legacy)</option>
                    </select>
                </div>
                
                <!-- Response Style -->
                <div class="setting-group">
                    <label class="setting-label">
                        <strong>📝 Response Style</strong>
                        <span class="setting-description">Adjust how the AI communicates</span>
                    </label>
                    <select id="response_style" class="setting-input">
                        <option value="descriptive">Descriptive (Default) - Clear and factual</option>
                        <option value="technical">Technical/Precise - Highly technical with exact specs</option>
                        <option value="natural">Natural/Conversational - Friendly and approachable</option>
                        <option value="balanced">Balanced - Mix of technical and readable</option>
                        <option value="concise">Concise/Brief - Short and to the point</option>
                        <option value="detailed">Detailed/Verbose - Comprehensive analysis</option>
                    </select>
                </div>
                
                <!-- Temperature -->
                <div class="setting-group">
                    <label class="setting-label">
                        <strong>🌡️ Temperature: <span id="temp-value">0.7</span></strong>
                        <span class="setting-description">Higher = more creative, Lower = more focused</span>
                    </label>
                    <input type="range" id="temperature" class="setting-slider" min="0" max="1" step="0.1" value="0.7" 
                           oninput="document.getElementById('temp-value').textContent = this.value">
                </div>
                
                <!-- Max Context Turns -->
                <div class="setting-group">
                    <label class="setting-label">
                        <strong>💬 Max Context Turns: <span id="turns-value">6</span></strong>
                        <span class="setting-description">Number of previous conversation turns to remember</span>
                    </label>
                    <input type="range" id="max_context_turns" class="setting-slider" min="2" max="20" step="1" value="6"
                           oninput="document.getElementById('turns-value').textContent = this.value">
                </div>
                
                <!-- Timeout -->
                <div class="setting-group">
                    <label class="setting-label">
                        <strong>⏱️ Request Timeout: <span id="timeout-value">25</span>s</strong>
                        <span class="setting-description">Maximum time to wait for API response</span>
                    </label>
                    <input type="range" id="timeout" class="setting-slider" min="10" max="60" step="5" value="25"
                           oninput="document.getElementById('timeout-value').textContent = this.value">
                </div>
                
                <!-- Save Button -->
                <div style="display: flex; gap: 15px; margin-top: 10px;">
                    <button onclick="saveSettings()" class="save-btn">
                        💾 Save Settings
                    </button>
                    <button onclick="resetSettings()" class="reset-btn">
                        🔄 Reset to Defaults
                    </button>
                </div>
                
                <div id="save-status" class="save-status"></div>
            </div>
        </div>
        
        <div id="api" class="tab-content">
            <h2>API Endpoints</h2>
            <p style="margin: 15px 0;">Available API endpoints for the UE5 AI Assistant:</p>
            <ul style="list-style: none; line-height: 2;">
                <li><strong>GET /</strong> - Health check</li>
                <li><strong>POST /execute_command</strong> - Execute AI commands</li>
                <li><strong>POST /describe_viewport</strong> - Generate viewport descriptions</li>
                <li><strong>GET /api/conversations</strong> - Retrieve conversation history</li>
                <li><strong>POST /api/log_conversation</strong> - Manually log a conversation</li>
                <li><strong>GET /dashboard</strong> - This dashboard</li>
            </ul>
        </div>
        
        <div id="about" class="tab-content">
            <h2>About UE5 AI Assistant</h2>
            <p style="margin: 15px 0; line-height: 1.6;">
                This is a FastAPI backend service that provides AI-powered technical documentation 
                of Unreal Engine 5 editor viewport contexts. The system receives structured viewport 
                data from the Unreal Engine Python environment and uses OpenAI's GPT models to generate 
                technical prose descriptions.
            </p>
            <p style="margin: 15px 0; line-height: 1.6;">
                <strong>Version:</strong> 2.0 (Modular Architecture)<br>
                <strong>Model:</strong> GPT-4o-mini<br>
                <strong>Project by:</strong> Noah Butcher
            </p>
        </div>
    </div>
    
    <script>
        let autoRefreshInterval = null;
        
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        function formatTimestamp(isoString) {
            const date = new Date(isoString);
            return date.toLocaleString();
        }
        
        function truncateText(text, maxLength = 300) {
            if (text.length <= maxLength) return text;
            return text.substring(0, maxLength) + '...';
        }
        
        async function loadConversations() {
            try {
                const response = await fetch('/api/conversations?limit=50');
                const data = await response.json();
                
                // Update stats
                document.getElementById('total-conversations').textContent = data.total;
                document.getElementById('recent-conversations').textContent = data.conversations.length;
                document.getElementById('max-storage').textContent = data.max_size;
                
                // Render conversations
                const listElement = document.getElementById('conversation-list');
                
                if (data.conversations.length === 0) {
                    listElement.innerHTML = `
                        <div class="empty-state">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                            </svg>
                            <p>No conversations yet. Start using the AI Assistant in Unreal Engine!</p>
                        </div>
                    `;
                    return;
                }
                
                listElement.innerHTML = data.conversations.map(conv => `
                    <div class="conversation-item">
                        <div class="conversation-header">
                            <span class="command-type">${conv.command_type}</span>
                            <span class="timestamp">${formatTimestamp(conv.timestamp)}</span>
                        </div>
                        <div class="user-input">
                            <strong>User:</strong> ${conv.user_input}
                        </div>
                        <div class="assistant-response">
                            <strong>Assistant:</strong> ${truncateText(conv.assistant_response)}
                        </div>
                    </div>
                `).join('');
                
            } catch (error) {
                console.error('Failed to load conversations:', error);
            }
        }
        
        // Auto-refresh toggle
        document.getElementById('auto-refresh').addEventListener('change', function(e) {
            if (e.target.checked) {
                autoRefreshInterval = setInterval(loadConversations, 5000);
            } else {
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                }
            }
        });
        
        // Initial load
        loadConversations();
        
        // Start auto-refresh
        autoRefreshInterval = setInterval(loadConversations, 5000);
        
        // ============================================================
        // SETTINGS FUNCTIONS
        // ============================================================
        
        async function loadSettings() {
            try {
                const response = await fetch('/api/config');
                const data = await response.json();
                const config = data.config;
                
                // Populate form fields
                document.getElementById('model').value = config.model || 'gpt-4o-mini';
                document.getElementById('response_style').value = config.response_style || 'descriptive';
                document.getElementById('temperature').value = config.temperature || 0.7;
                document.getElementById('temp-value').textContent = config.temperature || 0.7;
                document.getElementById('max_context_turns').value = config.max_context_turns || 6;
                document.getElementById('turns-value').textContent = config.max_context_turns || 6;
                document.getElementById('timeout').value = config.timeout || 25;
                document.getElementById('timeout-value').textContent = config.timeout || 25;
                
                console.log('Settings loaded:', config);
            } catch (error) {
                console.error('Failed to load settings:', error);
                showStatus('Failed to load settings', 'error');
            }
        }
        
        async function saveSettings() {
            const statusEl = document.getElementById('save-status');
            
            try {
                const settings = {
                    model: document.getElementById('model').value,
                    response_style: document.getElementById('response_style').value,
                    temperature: parseFloat(document.getElementById('temperature').value),
                    max_context_turns: parseInt(document.getElementById('max_context_turns').value),
                    timeout: parseInt(document.getElementById('timeout').value)
                };
                
                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settings)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus('✅ Settings saved successfully!', 'success');
                } else {
                    showStatus('❌ Failed to save settings', 'error');
                }
            } catch (error) {
                console.error('Failed to save settings:', error);
                showStatus('❌ Error: ' + error.message, 'error');
            }
        }
        
        async function resetSettings() {
            if (!confirm('Reset all settings to defaults?')) return;
            
            try {
                const response = await fetch('/api/config');
                const data = await response.json();
                const defaults = data.defaults;
                
                // Reset to defaults
                const settings = {
                    model: defaults.model,
                    response_style: defaults.response_style,
                    temperature: defaults.temperature,
                    max_context_turns: defaults.max_context_turns,
                    timeout: defaults.timeout
                };
                
                const saveResponse = await fetch('/api/config', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settings)
                });
                
                if (saveResponse.ok) {
                    loadSettings(); // Reload to update UI
                    showStatus('✅ Settings reset to defaults', 'success');
                } else {
                    showStatus('❌ Failed to reset settings', 'error');
                }
            } catch (error) {
                console.error('Failed to reset settings:', error);
                showStatus('❌ Error: ' + error.message, 'error');
            }
        }
        
        function showStatus(message, type) {
            const statusEl = document.getElementById('save-status');
            statusEl.textContent = message;
            statusEl.className = 'save-status ' + type;
            
            // Clear after 3 seconds
            setTimeout(() => {
                statusEl.textContent = '';
                statusEl.className = 'save-status';
            }, 3000);
        }
        
        // Load settings when opening settings tab
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', function() {
                if (this.textContent.includes('Settings')) {
                    loadSettings();
                }
            });
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


# ============================================================
# END OF FILE
# ============================================================
