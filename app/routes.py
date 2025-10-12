"""API routes for the UE5 AI Assistant backend."""
from typing import Any, Dict, List, Optional, cast

from fastapi import HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import DEFAULT_CONFIG, RESPONSE_STYLES
from app.models import (
    BlueprintCapture,
    ConfigUpdate,
    ConversationEntry,
    GuidanceRequest,
    ProjectProfile,
    ViewportContext,
)
from app.services import conversation
from app.services.file_system import FileSystemService
from app.services.filtering import filter_viewport_data
from app.services.guidance import GuidanceService
from app.services.openai_client import (
    generate_viewport_description,
    test_openai_connection,
)


def generate_ue56_utility_script(name: str, desc: str, capabilities: list) -> str:
    """Generate UE 5.6 compliant utility script."""
    script = f'''"""
{name} - {desc}
AI-Powered Editor Utility Widget
UE 5.6 Compatible
"""
import unreal


@unreal.uclass()
class {name}(unreal.EditorUtilityWidget):
    """
    {desc}
    
    Capabilities: {", ".join(capabilities)}
    """
    
    def __init__(self):
        super().__init__()
        # Load AI Assistant client
        try:
            import sys
            import os
            project_dir = unreal.Paths.project_dir()
            python_dir = os.path.join(project_dir, "Content", "Python")
            if python_dir not in sys.path:
                sys.path.append(python_dir)
            
            from AIAssistant.api_client import get_client
            self.api_client = get_client()
        except Exception as e:
            unreal.log_error(f"Failed to load AI client: {{e}}")
            self.api_client = None
'''

    if 'spawn_actors' in capabilities:
        script += '''
    
    @unreal.ufunction(ret=None, params=[str])
    def spawn_from_description(self, description):
        """Spawn actors based on natural language description."""
        if not self.api_client:
            unreal.log_error("AI client not available")
            return
        
        try:
            response = self.api_client.post_json(
                "/api/generate_action_plan",
                {"description": description}
            )
            
            if response.get("success") and response.get("plan"):
                self._execute_plan(response["plan"])
            else:
                unreal.log_warning("Failed to generate plan")
        except Exception as e:
            unreal.log_error(f"Spawn error: {e}")
    
    def _execute_plan(self, plan):
        """Execute AI-generated action plan."""
        actor_subsystem = unreal.get_editor_subsystem(
            unreal.EditorActorSubsystem
        )
        asset_library = unreal.EditorAssetLibrary
        
        for action in plan:
            action_type = action.get("type")
            
            if action_type == "spawn":
                asset_path = action.get("asset", "")
                location = action.get("location", [0, 0, 0])
                rotation = action.get("rotation", [0, 0, 0])
                
                # Load and spawn the requested asset
                if asset_path:
                    try:
                        # Load the asset (Blueprint/Class)
                        asset = asset_library.load_asset(asset_path)
                        
                        if asset:
                            # Get the generated class from Blueprint
                            if isinstance(asset, unreal.Blueprint):
                                actor_class = asset.generated_class
                            else:
                                actor_class = asset
                            
                            # Spawn with transform
                            spawned = actor_subsystem.spawn_actor_from_class(
                                actor_class,
                                unreal.Vector(location[0], location[1], location[2]),
                                unreal.Rotator(rotation[0], rotation[1], rotation[2])
                            )
                            
                            if spawned:
                                unreal.log(f"✅ Spawned: {asset_path}")
                            else:
                                unreal.log_warning(f"Failed to spawn: {asset_path}")
                        else:
                            unreal.log_warning(f"Asset not found: {asset_path}")
                    except Exception as e:
                        unreal.log_error(f"Spawn error: {e}")
                else:
                    # Fallback: spawn generic actor
                    actor_subsystem.spawn_actor_from_class(
                        unreal.Actor,
                        unreal.Vector(location[0], location[1], location[2])
                    )
'''

    if 'query_project' in capabilities:
        script += '''
    
    @unreal.ufunction(ret=None, params=[str])
    def query_ai(self, question):
        """Query AI about the project."""
        if not self.api_client:
            unreal.log_error("AI client not available")
            return
        
        try:
            response = self.api_client.post_json(
                "/api/project_query",
                {"query": question}
            )
            
            answer = response.get("response", "No response")
            unreal.log(f"AI: {answer}")
            
            # Write to file for Blueprint to read
            import os
            project_dir = unreal.Paths.project_dir()
            response_file = os.path.join(
                project_dir, "Saved", "AIConsole", "utility_response.txt"
            )
            os.makedirs(os.path.dirname(response_file), exist_ok=True)
            with open(response_file, 'w') as f:
                f.write(answer)
                
        except Exception as e:
            unreal.log_error(f"Query error: {e}")
'''

    script += '''

    @unreal.ufunction(ret=str, params=[])
    def get_status(self):
        """Get utility status."""
        if self.api_client:
            return "✅ Connected to AI Backend"
        return "❌ Not connected"
'''

    return script

# Session messages for execute_command context (global state for single-user UE integration)
session_messages: List[Dict[str, str]] = []


def get_system_message(app_config: Dict[str, Any]) -> str:
    """Generate system message with current response style."""
    current_style = app_config.get("response_style", "descriptive")
    style_config = RESPONSE_STYLES.get(
        current_style, RESPONSE_STYLES["descriptive"]
    )
    style_modifier = style_config["prompt_modifier"]
    
    base_msg = (
        "You are an AI assistant for Unreal Engine 5.6. "
        "Generate structured prose describing editor state and scene contents. "
        "Use terminology appropriate for UE5, include specific names and values. "
        "\n\n"
        "IMPORTANT CAPABILITIES:\n"
        "When users ask about THEIR specific project/editor state, "
        "you can trigger real-time data collection by responding with "
        "[UE_REQUEST] tokens:\n"
        "\n"
        "VIEWPORT & SCENE:\n"
        "- [UE_REQUEST] describe_viewport - When user asks 'describe my viewport', 'what's in my scene', 'describe what I see'\n"
        "  Use this for 3D viewport scene description, actors, lighting, camera\n"
        "\n"
        "BLUEPRINTS:\n"
        "- [UE_REQUEST] capture_blueprint - ONLY when user explicitly asks to 'capture blueprint' or 'screenshot blueprint'\n"
        "  Requires Blueprint Editor to be open. NOT for viewport description!\n"
        "- [UE_REQUEST] list_blueprints - List all Blueprint assets in project\n"
        "\n"
        "PROJECT INFO:\n"
        "- [UE_REQUEST] get_project_info - Get project name, modules, blueprints count\n"
        "- [UE_REQUEST] browse_files - Browse project file structure and count files\n"
        "\n"
        "CRITICAL: 'describe viewport' = describe_viewport, NOT capture_blueprint!\n"
        "\n"
        "For GENERAL advice (e.g., 'how do I create a C++ file'), provide "
        "helpful guidance without tokens. "
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
    
    @app.post("/api/deploy_client")
    async def deploy_client(request: dict):
        """Deploy client files directly to UE5 project path."""
        import shutil
        from pathlib import Path
        
        project_path = request.get("project_path", "")
        overwrite = request.get("overwrite", True)
        
        if not project_path:
            return {"success": False, "error": "No project path provided"}
        
        try:
            # Construct target path
            target_base = Path(project_path) / "Content" / "Python" / "AIAssistant"
            source_base = Path("ue5_client/AIAssistant")
            
            if not source_base.exists():
                return {"success": False, "error": "Source files not found"}
            
            # Create target directory
            target_base.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            copied_files = []
            overwrote_count = 0
            
            for file_path in source_base.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(source_base)
                    target_file = target_base / rel_path
                    
                    # Track if overwriting
                    if target_file.exists():
                        if not overwrite:
                            continue
                        overwrote_count += 1
                    
                    # Create parent directory
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(file_path, target_file)
                    copied_files.append(str(rel_path))
            
            return {
                "success": True,
                "message": f"Deployed {len(copied_files)} files",
                "files_copied": copied_files,
                "overwrote_existing": overwrote_count if overwrote_count > 0 else None,
                "target_path": str(target_base),
                "instructions": [
                    "1. Open Unreal Editor",
                    "2. Open Python Console (Tools → Python Console)",
                    "3. Run: import AIAssistant.main",
                    "4. Check Output Log for '✅ Project registered' message"
                ]
            }
        except PermissionError:
            return {
                "success": False,
                "error": "Permission denied. The browser cannot write to your local file system. Please download the client ZIP and extract manually."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Deployment failed: {str(e)}. Browser cannot access local files - please use manual download."
            }
    
    @app.get("/deploy/modern")
    async def modern_deploy_page():
        """Serve the modern File System Access API deployment page."""
        from pathlib import Path
        template_path = Path("app/templates/file_system_access.html")
        if template_path.exists():
            content = template_path.read_text()
            return HTMLResponse(content=content)
        return {"error": "Deployment page not found"}
    
    @app.get("/api/deploy_agent_installer")
    async def get_deploy_agent_installer():
        """Download the Deploy Agent installer batch file."""
        from pathlib import Path

        from fastapi.responses import Response
        
        installer_path = Path("scripts/deploy_agent_installer.bat")
        if installer_path.exists():
            content = installer_path.read_text()
            return Response(
                content=content,
                media_type="text/plain",
                headers={
                    "Content-Disposition": "attachment; filename=deploy_agent_installer.bat"
                }
            )
        return {"error": "Installer not found"}
    
    @app.post("/api/deploy_agent_bootstrap")
    async def deploy_agent_bootstrap_post():
        """Bootstrap endpoint for Deploy Agent (POST bypasses CDN cache)."""
        from pathlib import Path

        from fastapi.responses import Response
        
        agent_path = Path("ue5_client/deploy_agent.py")
        if agent_path.exists():
            content = agent_path.read_text()
            return Response(
                content=content,
                media_type="text/plain",
                headers={
                    "Content-Disposition": "attachment; filename=deploy_agent.py",
                    "Cache-Control": "no-cache, no-store, must-revalidate"
                }
            )
        return {"error": "Deploy agent not found"}
    
    @app.get("/api/protocol_handler")
    async def get_protocol_handler():
        """Generate Windows registry file for protocol handler."""
        from pathlib import Path

        from fastapi.responses import Response
        
        reg_path = Path("scripts/ue5_protocol_handler.reg")
        if reg_path.exists():
            content = reg_path.read_bytes()  # Use read_bytes for .reg files
            return Response(
                content=content,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": "attachment; filename=ue5_protocol_handler.reg"
                }
            )
        return {"error": "Protocol handler not found"}
    
    @app.get("/api/get_installer_script")
    async def get_installer_script_new():
        """Download batch installer (no admin required)."""
        from pathlib import Path

        from fastapi.responses import Response
        
        script_path = Path("scripts/install_client.bat")
        if script_path.exists():
            content = script_path.read_text()
            return Response(
                content=content,
                media_type="text/plain",
                headers={
                    "Content-Disposition": "attachment; filename=install_ue5_assistant.bat",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
        return {"error": "Installer script not found"}
    
    @app.post("/api/installer_script")
    async def get_installer_script_post():
        """POST version to bypass CDN cache completely."""
        from pathlib import Path

        from fastapi.responses import Response
        
        script_path = Path("scripts/install_ue5_assistant.ps1")
        if script_path.exists():
            content = script_path.read_text(encoding='utf-8')
            return Response(
                content=content,
                media_type="text/plain; charset=utf-8",
                headers={
                    "Content-Disposition": "attachment; filename=install_ue5_assistant.ps1",
                    "Cache-Control": "no-cache, no-store, must-revalidate"
                }
            )
        return {"error": "Installer script not found"}
    
    @app.post("/api/client_manifest")
    async def get_client_manifest():
        """
        Return manifest of current client files (bypasses CDN via POST).
        Includes content hash for Deploy Agent to detect updates.
        """
        import hashlib
        from pathlib import Path
        
        client_dir = Path("ue5_client/AIAssistant")
        
        # Collect all files and compute content hash
        files_data = []
        hasher = hashlib.sha256()
        
        if client_dir.exists():
            for file_path in sorted(client_dir.rglob("*")):
                if file_path.is_file():
                    # Add file content to hash
                    content = file_path.read_bytes()
                    hasher.update(content)
                    hasher.update(str(file_path).encode())
                    
                    files_data.append({
                        "path": str(file_path.relative_to("ue5_client")),
                        "size": len(content)
                    })
        
        content_hash = hasher.hexdigest()
        
        return {
            "version": content_hash[:12],  # Short version for readability
            "full_hash": content_hash,
            "file_count": len(files_data),
            "files": files_data,
            "timestamp": __import__('time').time()
        }
    
    @app.post("/api/download_client_bundle")
    async def download_client_bundle():
        """
        Download client bundle via POST (bypasses CDN cache).
        Deploy Agent should use this instead of GET /api/download_client.
        """
        import io
        import time
        import zipfile
        from pathlib import Path

        from fastapi.responses import StreamingResponse
        
        # Create in-memory zip
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all AIAssistant files (fresh read from filesystem)
            client_dir = Path("ue5_client/AIAssistant")
            
            if client_dir.exists():
                for file_path in client_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to("ue5_client"))
                        zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        
        # POST requests bypass CDN, but add headers anyway
        headers = {
            "Content-Disposition": "attachment; filename=UE5_AIAssistant_Client.zip",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "X-Content-Version": str(int(time.time()))
        }
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers=headers
        )
    
    @app.get("/api/download_client")
    async def download_client():
        """
        Download client bundle via GET (reliable Replit-compatible endpoint).
        This is the primary download endpoint used by UE5 auto-update.
        """
        import io
        import time
        import zipfile
        from pathlib import Path

        from fastapi.responses import StreamingResponse
        
        # Create in-memory zip
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all AIAssistant files (fresh read from filesystem)
            client_dir = Path("ue5_client/AIAssistant")
            
            if client_dir.exists():
                for file_path in client_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to("ue5_client"))
                        zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        
        # Add cache-busting headers
        headers = {
            "Content-Disposition": "attachment; filename=UE5_AIAssistant_Client.zip",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Content-Version": str(int(time.time()))
        }
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers=headers
        )
    
    @app.get("/api/download_client_bundle")
    async def download_client_bundle_get():
        """Alias for /api/download_client (backwards compatibility)."""
        return await download_client()

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
        # Accept both "prompt" (new) and "user_input" (legacy) for backwards compatibility
        user_input = request.get("prompt") or request.get("user_input", "")
        if not user_input:
            return {"error": "No prompt provided."}

        try:
            lower = user_input.lower()

            # Tokenized command routing
            
            # Viewport/Scene queries
            if any(k in lower for k in [
                "what do i see", "viewport", "describe viewport", "scene"
            ]):
                return {"response": "[UE_REQUEST] describe_viewport"}
            
            # Actor list queries
            if "list actors" in lower or "list of actors" in lower:
                return {"response": "[UE_REQUEST] list_actors"}
            
            # Selection queries
            if "selected" in lower and ("info" in lower or "details" in lower):
                return {"response": "[UE_REQUEST] get_selected_info"}
            
            # Project-specific queries - need AI interpretation
            if any(k in lower for k in [
                "my project", "project name", "project called",
                "what am i working on", "current project",
                "this project", "project info", "breakdown"
            ]):
                # Signal UE5 to collect context and send for AI processing
                return {"response": f"[UE_CONTEXT_REQUEST] project_info|{user_input}"}
            
            # Blueprint capture requests - need AI interpretation
            if any(k in lower for k in [
                "capture", "screenshot", "screen shot",
                "show blueprint", "picture of", "image of"
            ]) and any(b in lower for b in [
                "blueprint", "bp_", "graph", "node"
            ]):
                return {
                    "response": f"[UE_CONTEXT_REQUEST] blueprint_capture|{user_input}"
                }
            
            # File/Asset browsing
            if any(k in lower for k in [
                "show files", "list files", "browse files",
                "what files", "project files"
            ]):
                return {"response": "[UE_REQUEST] browse_files"}
            
            # Blueprint listing
            if "list" in lower and "blueprint" in lower:
                return {"response": "[UE_REQUEST] list_blueprints"}

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

    @app.post("/answer_with_context")
    async def answer_with_context(request: dict):
        """
        Answer user question using collected context data and AI.
        This allows natural language responses instead of canned summaries.
        """
        import json

        import openai
        user_question = request.get("question", "")
        context_data = request.get("context", {})
        context_type = request.get("context_type", "unknown")
        
        if not user_question:
            return {"error": "No question provided"}
        
        try:
            # Build context-aware prompt
            context_str = json.dumps(context_data, indent=2)
            
            prompt = (
                f"User question: {user_question}\n\n"
                f"Context data ({context_type}):\n{context_str}\n\n"
                f"Answer the user's specific question using the context data. "
                f"Be concise and answer exactly what they asked - don't provide "
                f"extra information they didn't request."
            )
            
            # Get AI response
            model_name = app_config.get("model", "gpt-4o-mini")
            response = openai.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": get_system_message(app_config)},
                    {"role": "user", "content": prompt}
                ],
                temperature=app_config.get("temperature", 0.7),
            )
            
            reply = (response.choices[0].message.content or "").strip()
            
            # Log to conversation history
            conversation.add_to_history(
                user_question,
                reply,
                "answer_with_context",
                {"context_type": context_type}
            )
            
            return {"response": reply}
            
        except Exception as e:
            print(f"[ERROR] answer_with_context: {e}")
            return {"error": str(e)}
    
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

    # Blueprint Capture Routes
    blueprint_capture_cache: Dict[str, BlueprintCapture] = {}
    
    @app.post("/api/blueprints/capture")
    async def submit_blueprint_capture(capture: BlueprintCapture):
        """Store a blueprint screenshot capture."""
        blueprint_capture_cache[capture.capture_id] = capture
        return {
            "success": True,
            "message": "Blueprint capture stored successfully",
            "capture_id": capture.capture_id,
            "blueprint_name": capture.blueprint_name
        }
    
    @app.get("/api/blueprints/{capture_id}")
    async def get_blueprint_capture(capture_id: str):
        """Retrieve a specific blueprint capture."""
        if capture_id in blueprint_capture_cache:
            return {
                "success": True,
                "data": blueprint_capture_cache[capture_id].model_dump()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Blueprint capture not found: {capture_id}"
            )
    
    @app.get("/api/blueprints")
    async def list_blueprint_captures():
        """List all stored blueprint captures."""
        return {
            "success": True,
            "captures": [
                {
                    "capture_id": capture.capture_id,
                    "blueprint_name": capture.blueprint_name,
                    "blueprint_path": capture.blueprint_path,
                    "timestamp": capture.timestamp,
                    "has_image": bool(capture.image_base64 or capture.image_url)
                }
                for capture in blueprint_capture_cache.values()
            ],
            "count": len(blueprint_capture_cache)
        }

    # Project Registry Endpoints
    @app.post("/api/register_project")
    async def register_project(request: dict):
        """Register a UE5 project from the client or browser."""
        import hashlib

        from app.project_registry import get_registry
        
        # Support both formats: direct fields or nested project_data
        if "project_data" in request:
            # Format from UE5 client
            project_id = request.get("project_id", "")
            project_data = request.get("project_data", {})
        else:
            # Format from browser manual registration
            name = request.get("name", "")
            path = request.get("path", "")
            version = request.get("version", "5.6")
            metadata = request.get("metadata", {})
            
            if not path:
                return {"success": False, "error": "No project path provided"}
            
            # Generate project_id from path hash
            project_id = hashlib.md5(path.encode()).hexdigest()[:12]
            
            project_data = {
                "name": name or path.split('/')[-2],  # Use folder name if no name
                "path": path,
                "version": version,
                "metadata": metadata
            }
        
        if not project_id:
            return {"success": False, "error": "No project_id provided"}
        
        registry = get_registry()
        result = registry.register_project(project_id, project_data)
        return result
    
    @app.get("/api/projects")
    async def list_projects():
        """List all registered projects."""
        from app.project_registry import get_registry
        
        registry = get_registry()
        return {
            "success": True,
            "projects": registry.list_projects()
        }
    
    @app.get("/api/active_project")
    async def get_active_project():
        """Get the currently active project."""
        from app.project_registry import get_registry
        
        registry = get_registry()
        project = registry.get_active_project()
        
        if project:
            return {"success": True, "project": project}
        else:
            return {"success": False, "message": "No active project"}
    
    @app.post("/api/set_active_project")
    async def set_active_project(request: dict):
        """Set the active project."""
        from app.project_registry import get_registry
        
        project_id = request.get("project_id", "")
        
        if not project_id:
            return {"success": False, "error": "No project_id provided"}
        
        registry = get_registry()
        return registry.set_active_project(project_id)
    
    @app.post("/api/set_connection_mode")
    async def set_connection_mode(request: dict):
        """Set connection mode preference for a project."""
        from app.project_registry import get_registry
        
        project_id = request.get("project_id", "")
        connection_mode = request.get("connection_mode", "http")
        
        if not project_id:
            return {"success": False, "error": "No project_id provided"}
        
        if connection_mode not in ["http", "websocket"]:
            return {"success": False, "error": "Invalid connection mode"}
        
        registry = get_registry()
        result = registry.set_connection_mode(project_id, connection_mode)
        
        return result

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """Serve the unified dashboard with Project Hub."""
        from pathlib import Path
        dashboard_path = Path(__file__).parent / "templates" / "unified_dashboard.html"
        return HTMLResponse(content=dashboard_path.read_text())
    
    @app.get("/dashboard/project-hub", response_class=HTMLResponse)
    async def project_hub():
        """Serve the Project Hub HTML page."""
        from pathlib import Path
        hub_path = Path(__file__).parent / "templates" / "dashboard_project_hub.html"
        return HTMLResponse(content=hub_path.read_text())
    
    @app.post("/api/project_query")
    async def project_query(request: dict):
        """
        Handle project intelligence queries from browser.
        Uses active project context and can trigger UE5 data collection.
        """
        import openai

        from app.project_registry import get_registry
        
        query = request.get("query", "")
        
        if not query:
            return {"error": "No query provided"}
        
        try:
            # Get active project context
            registry = get_registry()
            active_project = registry.get_active_project()
            
            # Build context-aware system message with UE_REQUEST capabilities
            if active_project:
                project_name = active_project.get('name', 'Unknown')
                project_path = active_project.get('path', '')
                project_metadata = active_project.get('metadata', {})
                
                context = f"""You are an AI assistant for Unreal Engine 5 with LIVE project data access.

Active Project: {project_name}
Path: {project_path}
Metadata: {project_metadata}

IMPORTANT: You can collect REAL data from the running UE5 editor by using [UE_REQUEST] tokens:

- [UE_REQUEST] get_project_info - Get actual project modules, blueprints count
- [UE_REQUEST] browse_files - Browse and COUNT files in project (use for "how many files")
- [UE_REQUEST] list_blueprints - List all Blueprint assets
- [UE_REQUEST] describe_viewport - Describe 3D viewport scene

When users ask about their project's actual data (file counts, blueprints, etc), ALWAYS use the appropriate [UE_REQUEST] to get real data instead of guessing. Respond ONLY with the [UE_REQUEST] token, nothing else."""
            else:
                context = "You are an AI assistant for Unreal Engine 5 development. No active project detected. Provide general technical guidance."
            
            # Call OpenAI API to determine if UE_REQUEST is needed
            response = openai.chat.completions.create(
                model=app_config.get("model", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,  # Lower temp for more consistent token detection
                max_tokens=1500
            )
            
            ai_response = (response.choices[0].message.content or "").strip()
            
            # Check if AI wants to collect data from UE5
            if ai_response.startswith("[UE_REQUEST]"):
                # Extract action token
                action = ai_response.replace("[UE_REQUEST]", "").strip()
                
                # Try to execute in connected UE5 client
                from app.websocket_manager import get_manager
                manager = get_manager()
                
                # Check if UE5 client is connected for this project
                if active_project:
                    project_id = active_project.get("project_id")
                    
                    # Try to send command to UE5
                    try:
                        ue5_response = await manager.send_command_to_ue5(
                            project_id,
                            {
                                "type": "execute_action",
                                "action": action,
                                "params": {}
                            }
                        )
                        
                        if ue5_response and ue5_response.get("success"):
                            # Got data from UE5! Now ask AI to format it nicely
                            ue5_data = ue5_response.get("data", {})
                            
                            # Second AI call to format the raw UE5 data
                            format_response = openai.chat.completions.create(
                                model=app_config.get("model", "gpt-4o-mini"),
                                messages=[
                                    {"role": "system", "content": f"You are an AI assistant. Format this UE5 data into a helpful response for: {query}"},
                                    {"role": "user", "content": f"Raw data from UE5:\n{ue5_data}\n\nOriginal question: {query}"}
                                ],
                                temperature=0.7,
                                max_tokens=1500
                            )
                            
                            formatted_response = (format_response.choices[0].message.content or "").strip()
                            
                            return {
                                "response": formatted_response,
                                "project_context": active_project["name"] if active_project else None,
                                "ue5_data": ue5_data
                            }
                        else:
                            # UE5 didn't respond properly
                            error_msg = ue5_response.get("error", "No response") if ue5_response else "Connection timeout"
                            return {
                                "response": f"⚠️ UE5 client didn't respond to: {action}\n\nError: {error_msg}\n\nMake sure your UE5 project has the AI Assistant running (import AIAssistant.main in UE5 Python Console).",
                                "project_context": active_project["name"] if active_project else None
                            }
                    except Exception as e:
                        # Connection failed - inform user
                        return {
                            "response": f"🔄 This query requires live data from your UE5 editor.\n\nAction needed: {action}\n\nError connecting to UE5: {str(e)}\n\nTo enable automatic data collection, make sure your UE5 project has the AI Assistant client running.",
                            "project_context": active_project["name"] if active_project else None,
                            "ue_request": action
                        }
                else:
                    # No active project
                    return {
                        "response": f"🔄 This query requires live data from your UE5 editor.\n\nAction needed: {action}\n\nNo active project selected. Please select a project first.",
                        "project_context": None,
                        "ue_request": action
                    }
            
            return {
                "response": ai_response,
                "project_context": active_project["name"] if active_project else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    # WebSocket endpoints for real-time UE5 <-> Dashboard communication
    @app.websocket("/ws/ue5/{project_id}")
    async def websocket_ue5_endpoint(websocket: WebSocket, project_id: str):
        """WebSocket endpoint for UE5 client connections."""
        from app.websocket_manager import get_manager
        
        print(f"🔌 WebSocket connection attempt from UE5: {project_id}")
        print(f"   Headers: {websocket.headers}")
        print(f"   Client: {websocket.client}")
        
        manager = get_manager()
        await manager.connect_ue5(websocket, project_id)
        
        try:
            while True:
                # Receive messages from UE5
                data = await websocket.receive_json()
                
                # Handle UE5 response
                await manager.handle_ue5_response(project_id, data)
                
        except WebSocketDisconnect:
            await manager.disconnect_ue5(project_id)
    
    @app.websocket("/ws/dashboard")
    async def websocket_dashboard_endpoint(websocket: WebSocket):
        """WebSocket endpoint for dashboard connections."""
        from app.websocket_manager import get_manager
        
        manager = get_manager()
        await manager.connect_dashboard(websocket)
        
        try:
            while True:
                # Receive commands from dashboard
                data = await websocket.receive_json()
                
                command_type = data.get("type")
                
                if command_type == "execute_action":
                    # Execute action in UE5
                    project_id = data.get("project_id")
                    action = data.get("action")
                    params = data.get("params", {})
                    
                    response = await manager.send_command_to_ue5(
                        project_id,
                        {
                            "type": "execute_action",
                            "action": action,
                            "params": params
                        }
                    )
                    
                    # Send response back to dashboard
                    await websocket.send_json({
                        "type": "action_result",
                        "action": action,
                        "result": response
                    })
                
                elif command_type == "auto_update":
                    # Broadcast auto-update to all UE5 clients
                    result = await manager.broadcast_update_to_ue5_clients()
                    
                    # Send response back to dashboard
                    await websocket.send_json({
                        "type": "auto_update_result",
                        "result": result
                    })
                    
        except WebSocketDisconnect:
            manager.disconnect_dashboard(websocket)
    
    @app.post("/api/trigger_auto_update")
    async def trigger_auto_update():
        """Trigger auto-update for all connected UE5 clients (called on backend republish)."""
        from app.websocket_manager import get_manager
        
        manager = get_manager()
        result = await manager.broadcast_update_to_ue5_clients()
        
        return result
    
    @app.post("/api/generate_utility")
    async def generate_utility(request: dict):
        """Generate UE 5.6 compliant editor utility widget."""

        from app.project_registry import get_registry
        
        name = request.get("name", "CustomTool")
        description = request.get("description", "")
        capabilities = request.get("capabilities", [])
        
        try:
            # Get active project for correct path
            registry = get_registry()
            active_project = registry.get_active_project()
            
            # Generate UE 5.6 compliant Python script
            script = generate_ue56_utility_script(
                name, description, capabilities
            )
            
            # Determine save path
            if active_project:
                project_path = active_project.get('path', '')
                script_path = f"{project_path}Content/Python/AIAgentUtilities/{name}.py"
            else:
                script_path = f"Content/Python/AIAgentUtilities/{name}.py"
            
            return {
                "success": True,
                "widget_name": name,
                "script_path": script_path,
                "script_content": script,
                "instructions": [
                    "1. Copy the generated script to your project",
                    "2. Restart Unreal Editor to load the utility",
                    "3. Find in Content Browser under Python/AIAgentUtilities",
                    "4. Right-click and execute"
                ]
            }
        except Exception as e:
            return {"error": str(e)}
    
    @app.post("/api/generate_action_plan")
    async def generate_action_plan(request: dict):
        """Generate AI action plan for scene building."""
        import openai
        
        description = request.get("description", "")
        
        if not description:
            return {"error": "No description provided"}
        
        try:
            # Ask AI to create action plan
            model_name = app_config.get("model", "gpt-4o-mini")
            
            prompt = f"""Create a detailed action plan for building this scene in Unreal Engine:

{description}

Return a JSON array of actions. Each action should have:
- type: "spawn", "align", "camera", etc.
- asset: asset path (for spawn actions)
- location: [x, y, z]
- rotation: [pitch, yaw, roll]
- parameters: additional params

Example:
[
  {{"type": "spawn", "asset": "/Game/Meshes/House", "location": [0, 0, 0]}},
  {{"type": "align", "axis": "z", "align_to": "min"}}
]

Return ONLY the JSON array, no explanation."""

            response = openai.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a UE5 scene planning AI. Generate precise action plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            plan_text = response.choices[0].message.content or ""
            
            # Try to parse JSON
            import json
            start = plan_text.find('[')
            end = plan_text.rfind(']') + 1
            
            if start != -1 and end > start:
                plan = json.loads(plan_text[start:end])
                return {"success": True, "plan": plan}
            else:
                return {"success": True, "plan": [], "raw_response": plan_text}
                
        except Exception as e:
            return {"error": str(e)}
    
    # ========================================================================
    # HTTP Polling Endpoints (Fallback for when WebSocket doesn't work)
    # Non-destructive addition - WebSocket code remains unchanged
    # ========================================================================
    
    @app.post("/api/ue5/register_http")
    async def register_ue5_http(request: dict):
        """Register UE5 client via HTTP polling (WebSocket fallback)."""
        from app.websocket_manager import get_manager
        from datetime import datetime
        
        project_id = request.get("project_id")
        project_name = request.get("project_name", "Unknown")
        
        if not project_id:
            return {"success": False, "error": "project_id required"}
        
        manager = get_manager()
        # Store as HTTP client instead of WebSocket
        if not hasattr(manager, 'http_clients'):
            manager.http_clients = {}
        
        manager.http_clients[project_id] = {
            "name": project_name,
            "last_poll": datetime.now(),
            "pending_commands": []
        }
        
        print(f"✅ UE5 HTTP client registered: {project_id} ({project_name})")
        
        # Notify dashboards
        await manager.broadcast_to_dashboards({
            "type": "ue5_status",
            "project_id": project_id,
            "status": "connected",
            "connection_type": "http_polling",
            "timestamp": datetime.now().isoformat()
        })
        
        return {"success": True, "message": "Registered via HTTP polling"}
    
    @app.post("/api/ue5/poll")
    async def poll_for_commands(request: dict):
        """UE5 client polls for pending commands."""
        from app.websocket_manager import get_manager
        from datetime import datetime
        
        project_id = request.get("project_id")
        if not project_id:
            return {"commands": [], "registered": False}
        
        manager = get_manager()
        if not hasattr(manager, 'http_clients'):
            manager.http_clients = {}
        
        # Auto-register if not registered (handles server restarts gracefully)
        if project_id not in manager.http_clients:
            project_name = request.get("project_name", "Unknown")
            manager.http_clients[project_id] = {
                "name": project_name,
                "last_poll": datetime.now(),
                "pending_commands": []
            }
            print(f"🔄 Auto-registered HTTP client on poll: {project_id}")
            
            # Notify dashboards
            await manager.broadcast_to_dashboards({
                "type": "ue5_status",
                "project_id": project_id,
                "status": "connected",
                "connection_type": "http_polling",
                "timestamp": datetime.now().isoformat()
            })
        
        # Update last poll time
        manager.http_clients[project_id]["last_poll"] = datetime.now()
        
        # Get pending commands
        commands = manager.http_clients[project_id].get("pending_commands", [])
        
        # Clear pending commands after sending
        manager.http_clients[project_id]["pending_commands"] = []
        
        return {"commands": commands, "registered": True}
    
    @app.post("/api/ue5/heartbeat")
    async def ue5_heartbeat(request: dict):
        """Keep-alive heartbeat from UE5 HTTP client."""
        from app.websocket_manager import get_manager
        from datetime import datetime
        
        project_id = request.get("project_id")
        if not project_id:
            return {"success": False}
        
        manager = get_manager()
        if not hasattr(manager, 'http_clients'):
            manager.http_clients = {}
        
        if project_id in manager.http_clients:
            manager.http_clients[project_id]["last_poll"] = datetime.now()
            return {"success": True, "status": "alive"}
        
        return {"success": False, "error": "Not registered"}
    
    @app.post("/api/ue5/response")
    async def ue5_response(request: dict):
        """Receive action response from UE5 HTTP client."""
        from app.websocket_manager import get_manager
        
        project_id = request.get("project_id")
        response_data = request.get("response", {})
        
        if not project_id:
            return {"success": False, "error": "project_id required"}
        
        manager = get_manager()
        
        # Store response for pending requests (same as WebSocket does)
        request_id = response_data.get("request_id")
        if request_id:
            manager.pending_requests[request_id] = response_data
            print(f"[HTTP Polling] Received response for request: {request_id}")
        
        # Forward response to dashboards (same as WebSocket would do)
        await manager.broadcast_to_dashboards({
            "type": "action_result",
            "project_id": project_id,
            **response_data
        })
        
        return {"success": True}
