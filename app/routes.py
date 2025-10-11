"""API routes for the UE5 AI Assistant backend."""
import json
from typing import Any, Dict, List, Optional, cast
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse

from app.models import (
    ViewportContext, ConversationEntry, ConfigUpdate,
    FileContext, FileEntry, ProjectProfile, GuidanceRequest, BlueprintCapture
)
from app.config import RESPONSE_STYLES, DEFAULT_CONFIG
from app.services.filtering import filter_viewport_data
from app.services.openai_client import generate_viewport_description, test_openai_connection
from app.services import conversation
from app.services.file_system import FileSystemService
from app.services.guidance import GuidanceService
from app.dashboard import get_dashboard_html

# Session messages for execute_command context (global state for single-user UE integration)
session_messages: List[Dict[str, str]] = []


def get_system_message(app_config: Dict[str, Any]) -> str:
    """Generate system message with current response style."""
    current_style = app_config.get("response_style", "descriptive")
    style_modifier = RESPONSE_STYLES.get(current_style, RESPONSE_STYLES["descriptive"])["prompt_modifier"]
    
    base_msg = (
        "You are an AI assistant for Unreal Engine 5.6. "
        "Generate structured prose describing editor state and scene contents. "
        "Use terminology appropriate for UE5, include specific names and values. "
    )
    return base_msg + style_modifier


def init_session_messages(app_config: Dict[str, Any]) -> None:
    """Initialize session messages with system message."""
    global session_messages
    session_messages = [{
        "role": "system",
        "content": get_system_message(app_config)
    }]


def register_routes(app, app_config: Dict[str, Any], save_config_func):
    """Register all routes with the FastAPI app."""
    
    # Initialize session messages
    init_session_messages(app_config)
    
    @app.get("/")
    async def home():
        """Redirect to dashboard."""
        return RedirectResponse(url="/dashboard", status_code=307)

    @app.get("/health")
    async def health_check():
        """Health check endpoint for API monitoring."""
        return {"status": "online", "message": "UE5 AI Assistant running!", "version": "3.0"}

    @app.get("/test")
    async def test_endpoint():
        """Quick test route."""
        return {"status": "ok", "message": "FastAPI test route reachable."}

    @app.get("/ping_openai")
    async def ping_openai():
        """Verifies OpenAI connectivity."""
        model = app_config.get("model", "gpt-4o-mini")
        return test_openai_connection(model)

    @app.post("/execute_command")
    async def execute_command(request: dict):
        """
        Handles user prompts from Unreal's AI Command Console.
        Maintains short-term conversation context across turns.
        """
        import openai
        user_input = request.get("prompt", "")
        if not user_input:
            return {"error": "No prompt provided."}

        try:
            lower = user_input.lower()

            # Tokenized command routing
            if any(k in lower for k in ["what do i see", "viewport", "describe viewport", "scene"]):
                return {"response": "[UE_REQUEST] describe_viewport"}
            if "list actors" in lower or "list of actors" in lower:
                return {"response": "[UE_REQUEST] list_actors"}
            if "selected" in lower and ("info" in lower or "details" in lower):
                return {"response": "[UE_REQUEST] get_selected_info"}

            # Update memory
            session_messages.append({"role": "user", "content": user_input})
            max_context_turns = app_config.get("max_context_turns", 6)
            user_assistant_msgs = [m for m in session_messages if m["role"] != "system"]
            if len(user_assistant_msgs) > max_context_turns * 2:
                session_messages[:] = session_messages[:1] + user_assistant_msgs[-(max_context_turns * 2):]

            # Send to OpenAI
            model_name = app_config.get("model", "gpt-4o-mini")
            response = openai.chat.completions.create(
                model=model_name,
                messages=cast(List[Any], session_messages),
                temperature=app_config.get("temperature", 0.7),
            )

            reply = (response.choices[0].message.content or "").strip()
            print(f"[AI Response] {reply}")

            # Handle UE-request tokens
            if reply.startswith("[UE_REQUEST]"):
                token = reply.replace("[UE_REQUEST]", "").strip()
                print(f"[AIConsole] Detected UE token: {token}")
                return {"response": f"[UE_REQUEST] {token}"}

            # Append reply to memory
            session_messages.append({"role": "assistant", "content": reply})
            conversation.add_to_history(user_input, reply, "execute_command")
            
            return {"response": reply}

        except Exception as e:
            print(f"[ERROR] {e}")
            error_msg = str(e)
            conversation.add_to_history(user_input, f"ERROR: {error_msg}", "execute_command", {"error": True})
            return {"error": error_msg}

    @app.post("/wrap_natural_language")
    async def wrap_natural_language(request: dict):
        """
        Takes a factual string from UE and converts it to structured technical prose.
        """
        import openai
        summary_text = request.get("summary", "")
        if not summary_text:
            return {"error": "No summary text provided."}

        try:
            model_name = app_config.get("model", "gpt-4o-mini")
            response = openai.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Convert the following technical data into structured technical prose. "
                            "Organize information into logical groups (spatial layout, actors by type, lighting setup). "
                            "Use precise terminology and include specific names and values."
                        ),
                    },
                    {"role": "user", "content": summary_text},
                ],
                temperature=app_config.get("temperature", 0.7),
            )
            
            wrapped = response.choices[0].message.content or ""
            conversation.add_to_history(summary_text, wrapped, "wrap_natural_language")
            return {"response": wrapped.strip()}

        except Exception as e:
            print(f"[Error in wrap_natural_language] {e}")
            return {"error": str(e)}

    @app.post("/describe_viewport")
    async def describe_viewport(request: Request):
        """
        Intelligently describes viewport using style-aware data filtering and prompting.
        """
        # Parse incoming JSON
        try:
            raw_data: dict[str, Any] = await request.json()
        except Exception as e:
            print(f"[Error] Failed to parse JSON: {e}")
            return {"response": f"Error reading viewport data: {e}", "raw_context": {}}

        # Coerce into ViewportContext
        try:
            context = ViewportContext(**raw_data)
        except Exception:
            try:
                context = ViewportContext.model_validate(raw_data)
            except Exception:
                context = ViewportContext()

        # Get configured response style and apply intelligent filtering
        current_style = app_config.get("response_style", "descriptive")
        style_config = RESPONSE_STYLES.get(current_style, RESPONSE_STYLES["descriptive"])
        
        filter_mode = style_config["data_filter"]
        filtered_data = filter_viewport_data(context, filter_mode)
        
        print(f"[Describe Viewport] Style: {current_style}, Filter: {filter_mode}")
        print(f"[Filtered Data] Keys: {list(filtered_data.keys())}")

        # Generate description using OpenAI
        model = app_config.get("model", "gpt-4o-mini")
        temperature = app_config.get("temperature", 0.7)
        
        summary = generate_viewport_description(
            filtered_data, current_style, style_config, model, temperature
        )

        # Fallback logic if AI fails
        if not summary or len(summary.split()) < 4:
            camera_data = context.camera or {}
            actors_data = context.actors or {}
            
            cam_loc = camera_data.get("location", context.camera_location or [0,0,0])
            cam_rot = camera_data.get("rotation", context.camera_rotation or [0,0,0])
            total = actors_data.get("total", len(context.visible_actors or []))
            lvl = actors_data.get("level", "Unknown")
            
            summary = (
                f"Camera at {cam_loc} facing {cam_rot} "
                f"in level '{lvl}' with approximately {total} visible actors."
            )
            print("[Fallback] Basic camera-level summary used.")

        # Log to conversation history
        user_prompt = "Describe viewport"
        actors_count = context.actors.get("total", 0) if context.actors else 0
        has_selection = context.selection.get("count", 0) > 0 if context.selection else False
        metadata = {"actors_count": actors_count, "has_selection": has_selection}
        
        conversation.add_to_history(user_prompt, summary, "describe_viewport", metadata)

        return {"response": summary, "raw_context": context.model_dump()}

    @app.get("/api/conversations")
    async def get_conversations(limit: int = 50):
        """Get recent conversation history for dashboard."""
        history = conversation.get_history(limit)
        recent = list(reversed(history))
        return {
            "conversations": recent,
            "total": len(conversation.conversation_history),
            "max_size": conversation.MAX_HISTORY_SIZE
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
        nonlocal app_config
        
        update_dict = updates.model_dump(exclude_none=True)
        
        for key, value in update_dict.items():
            app_config[key] = value
        
        # Update system message if response_style changed
        if "response_style" in update_dict:
            session_messages[0]["content"] = get_system_message(app_config)
        
        save_config_func(app_config)
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "config": app_config
        }

    @app.post("/api/log_conversation")
    async def log_conversation(entry: ConversationEntry):
        """Manually log a conversation (for UE5 client if needed)."""
        conversation.add_to_history(
            entry.user_input,
            entry.assistant_response,
            entry.command_type,
            entry.metadata
        )
        return {"status": "logged", "total_entries": len(conversation.conversation_history)}

    @app.delete("/api/conversations")
    async def clear_conversations():
        """Clear all conversation history (memory and file)."""
        try:
            conversation.clear_history()
            return {
                "success": True,
                "message": "Conversation history cleared successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to clear history: {str(e)}"
            }

    # File System Routes
    file_service = FileSystemService(max_depth=10)
    
    @app.post("/api/files/list")
    async def list_files(request: dict):
        """List files in a directory."""
        directory_path = request.get("path", ".")
        recursive = request.get("recursive", False)
        
        try:
            result = file_service.list_directory(directory_path, recursive)
            return {"success": True, "data": result.model_dump()}
        except PermissionError as e:
            return {"success": False, "error": str(e), "type": "permission"}
        except Exception as e:
            return {"success": False, "error": str(e), "type": "general"}
    
    @app.post("/api/files/read")
    async def read_file(request: dict):
        """Read a file's content."""
        file_path = request.get("path")
        
        if not file_path:
            return {"success": False, "error": "No file path provided"}
        
        try:
            result = file_service.read_file(file_path)
            return {"success": True, "data": result.model_dump()}
        except PermissionError as e:
            return {"success": False, "error": str(e), "type": "permission"}
        except Exception as e:
            return {"success": False, "error": str(e), "type": "general"}
    
    @app.post("/api/files/search")
    async def search_files(request: dict):
        """Search for files matching criteria."""
        root_path = request.get("root_path", ".")
        pattern = request.get("pattern")
        extension = request.get("extension")
        max_results = request.get("max_results", 100)
        
        try:
            result = file_service.search_files(root_path, pattern, extension, max_results)
            return {"success": True, "data": result.model_dump()}
        except PermissionError as e:
            return {"success": False, "error": str(e), "type": "permission"}
        except Exception as e:
            return {"success": False, "error": str(e), "type": "general"}

    # Project Metadata Routes
    project_metadata_cache: Dict[str, ProjectProfile] = {}
    
    @app.post("/api/project/metadata")
    async def submit_project_metadata(profile: ProjectProfile):
        """Receive and cache project metadata from UE5."""
        project_metadata_cache[profile.project_name] = profile
        return {
            "success": True,
            "message": "Project metadata cached successfully",
            "project": profile.project_name
        }
    
    @app.get("/api/project/metadata")
    async def get_project_metadata(project_name: Optional[str] = None):
        """Get cached project metadata."""
        if project_name:
            if project_name in project_metadata_cache:
                return {
                    "success": True,
                    "data": project_metadata_cache[project_name].model_dump()
                }
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"No metadata found for project: {project_name}"
                )
        else:
            return {
                "success": True,
                "data": {
                    name: profile.model_dump()
                    for name, profile in project_metadata_cache.items()
                },
                "count": len(project_metadata_cache)
            }

    # Guidance Routes
    guidance_service = GuidanceService(
        model=app_config.get("model", "gpt-4o-mini"),
        temperature=app_config.get("temperature", 0.7)
    )
    
    @app.post("/api/guidance")
    async def get_guidance(request: GuidanceRequest):
        """Provide context-aware implementation guidance."""
        try:
            guidance = guidance_service.generate_guidance(request)
            
            conversation.add_to_history(
                request.query,
                guidance,
                "guidance",
                {
                    "has_viewport": request.viewport_context is not None,
                    "has_files": request.file_context is not None,
                    "has_project": request.project_profile is not None,
                    "has_blueprints": bool(request.blueprint_captures),
                    "focus_area": request.focus_area
                }
            )
            
            return {
                "success": True,
                "guidance": guidance,
                "query": request.query
            }
        except Exception as e:
            print(f"[Error in guidance] {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """Serve the conversation dashboard HTML."""
        return HTMLResponse(content=get_dashboard_html())
