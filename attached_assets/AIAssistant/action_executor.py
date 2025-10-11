"""
Action execution system with command registry pattern.
Handles [UE_REQUEST] tokens and executes Unreal Engine operations.
"""
from typing import Callable, Dict, Optional

try:
    import unreal  # type: ignore
    HAS_UNREAL = True
except ImportError:
    HAS_UNREAL = False
    unreal = None  # type: ignore  # Only available in UE environment

from .api_client import get_client
from .blueprint_capture import BlueprintCapture
from .config import get_config
from .context_collector import get_collector
from .file_collector import FileCollector
from .project_metadata_collector import get_collector as get_metadata_collector
from .utils import Logger


class ActionExecutor:
    """Executes actions in Unreal Engine based on AI commands."""

    def __init__(self):
        self.logger = Logger("ActionExecutor", verbose=False)
        self.config = get_config()
        self.actions: Dict[str, Callable[[], str]] = {}
        self.file_collector = FileCollector()
        self.blueprint_capture = BlueprintCapture()
        
        # Initialize metadata collector with config cache TTL
        cache_ttl = self.config.get("project_metadata_cache_ttl", 300)
        self.metadata_collector = get_metadata_collector()
        self.metadata_collector.cache_ttl_seconds = cache_ttl
        
        self._register_default_actions()

    def _register_default_actions(self) -> None:
        """Register the default action set."""
        # Existing actions
        self.register("describe_viewport", self._describe_viewport)
        self.register("list_actors", self._list_actors)
        self.register("get_selected_info", self._get_selected_info)
        
        # New file operation actions
        self.register("browse_files", self._browse_files)
        self.register("read_source_files", self._read_source_files)
        self.register("search_files", self._search_files)
        
        # Project metadata actions
        self.register("show_project_info", self._show_project_info)
        self.register("get_project_info", self._show_project_info)  # Alias
        
        # Blueprint capture actions
        self.register("capture_blueprint", self._capture_blueprint)
        self.register("list_blueprints", self._list_blueprints)

    def register(
        self, action_name: str, handler: Callable[[], str]
    ) -> None:
        """Register a new action handler."""
        self.actions[action_name] = handler
        self.logger.debug(f"Registered action: {action_name}")

    def execute(self, action_token: str) -> str:
        """Execute an action by token name."""
        action_name = action_token.lower().strip()

        if action_name not in self.actions:
            error_msg = (
                f"[UE_ERROR] Unknown action: {action_name}"
            )
            self.logger.error(error_msg)
            return error_msg

        try:
            self.logger.info(f"Executing: {action_name}")
            result = self.actions[action_name]()
            self.logger.success(f"Action completed: {action_name}")
            return result
        except Exception as e:
            error_msg = (
                f"[UE_ERROR] Action '{action_name}' failed: {e}"
            )
            self.logger.error(error_msg)
            return error_msg

    def _describe_viewport(self) -> str:
        """Collect viewport data and send to API for description."""
        if not HAS_UNREAL:
            return "[UE_ERROR] Unreal module not available"

        try:
            collector = get_collector()
            
            # Check if project metadata collection is enabled
            include_metadata = self.config.get("collect_project_metadata", True)
            context = collector.collect_viewport_data(
                include_project_metadata=include_metadata
            )

            if not context:
                return "[UE_ERROR] Failed to collect viewport data"

            client = get_client()
            response = client.describe_viewport(context)

            return response.get(
                "response",
                response.get("description", "(no description)")
            )
        except Exception as e:
            return f"[UE_ERROR] Viewport description failed: {e}"

    def _list_actors(self, limit: int = 30) -> str:
        """List actors in the current level."""
        if not HAS_UNREAL or unreal is None:
            return "[UE_ERROR] Unreal module not available"

        try:
            # unreal is available here (checked above, UE environment only)
            ell = unreal.EditorLevelLibrary  # type: ignore[union-attr]
            actors = list(ell.get_all_level_actors())
            names = [a.get_fname() for a in actors]
            total = len(names)

            lines = [f"Found {total} actors in the current level."]
            for name in names[:limit]:
                lines.append(f" - {name}")

            if total > limit:
                lines.append(f"... and {total - limit} more")

            return "\n".join(lines)
        except Exception as e:
            return f"[UE_ERROR] list_actors failed: {e}"

    def _get_selected_info(self) -> str:
        """Get detailed info about selected actors."""
        if not HAS_UNREAL or unreal is None:
            return "[UE_ERROR] Unreal module not available"

        try:
            # unreal is available here (checked above, UE environment only)
            ell = unreal.EditorLevelLibrary  # type: ignore[union-attr]
            selected = list(ell.get_selected_level_actors())

            if not selected:
                return "No actors currently selected."

            lines = [f"Selected Actors: {len(selected)}"]

            for actor in selected:
                name = actor.get_fname()
                cls = (
                    actor.get_class().get_name()
                    if actor.get_class()
                    else "UnknownClass"
                )

                loc_str = ""
                try:
                    t = actor.get_root_component().get_component_transform()
                    x = round(t.translation.x, 1)
                    y = round(t.translation.y, 1)
                    z = round(t.translation.z, 1)
                    loc_str = f" at ({x}, {y}, {z})"
                except Exception:
                    pass

                lines.append(f" - {name} ({cls}){loc_str}")

            return "\n".join(lines)
        except Exception as e:
            return f"[UE_ERROR] get_selected_info failed: {e}"
    
    def _browse_files(self) -> str:
        """Browse files in the Content directory."""
        if not self.config.get("enable_file_operations", True):
            return "[UE_ERROR] File operations are disabled in configuration"
        
        try:
            result = self.file_collector.list_directory(
                directory_path=self.file_collector.content_dir,
                recursive=True,
                max_depth=2
            )
            
            if result.get("error"):
                return f"[UE_ERROR] {result['error']}"
            
            lines = [f"📁 Content Directory: {result.get('root_path', 'Unknown')}"]
            lines.append(f"Total files: {result.get('total_files', 0)}\n")
            
            for file in result.get("files", [])[:20]:
                icon = "📁" if file.get("type") == "directory" else "📄"
                lines.append(f"{icon} {file.get('path', 'Unknown')}")
            
            if result.get("total_files", 0) > 20:
                lines.append(f"\n... and {result['total_files'] - 20} more files")
            
            return "\n".join(lines)
        except Exception as e:
            return f"[UE_ERROR] browse_files failed: {e}"
    
    def _read_source_files(self) -> str:
        """Read C++ source files."""
        if not self.config.get("enable_file_operations", True):
            return "[UE_ERROR] File operations are disabled in configuration"
        
        try:
            result = self.file_collector.get_source_files(max_files=10)
            
            if result.get("error"):
                return f"[UE_ERROR] {result['error']}"
            
            root_path = result.get('root_path', 'Unknown')
            lines = [f"📂 Source Directory: {root_path}"]
            types = result.get("file_types", {})
            lines.append(
                f"C++ files: {types.get('cpp', 0)}, "
                f"Headers: {types.get('headers', 0)}\n"
            )
            
            for file in result.get("files", [])[:10]:
                ext = file.get("extension", "")
                lines.append(f"  {ext} {file.get('name', 'Unknown')}")
            
            return "\n".join(lines)
        except Exception as e:
            return f"[UE_ERROR] read_source_files failed: {e}"
    
    def _search_files(self) -> str:
        """Search for files by pattern."""
        if not self.config.get("enable_file_operations", True):
            return "[UE_ERROR] File operations are disabled in configuration"
        
        try:
            # Default search for Blueprint files
            result = self.file_collector.search_files(
                pattern="BP_",
                max_results=20
            )
            
            if result.get("error"):
                return f"[UE_ERROR] {result['error']}"
            
            lines = [f"🔍 Search Results: {result.get('search_query', 'All files')}"]
            lines.append(f"Found {result.get('total_files', 0)} files\n")
            
            for file in result.get("files", []):
                lines.append(f"  • {file.get('name', 'Unknown')}")
            
            return "\n".join(lines)
        except Exception as e:
            return f"[UE_ERROR] search_files failed: {e}"
    
    def _show_project_info(self) -> str:
        """Show project metadata summary."""
        try:
            summary = self.metadata_collector.get_summary()
            return summary
        except Exception as e:
            return f"[UE_ERROR] show_project_info failed: {e}"
    
    def _capture_blueprint(self) -> str:
        """Capture screenshot of current Blueprint editor."""
        if not self.config.get("enable_blueprint_capture", True):
            return "[UE_ERROR] Blueprint capture is disabled in configuration"
        
        try:
            resolution = self.config.get("blueprint_capture_resolution", 2)
            result = self.blueprint_capture.capture_viewport_screenshot(
                blueprint_name="CurrentBlueprint",
                resolution_multiplier=resolution,
                check_blueprint=False  # Don't validate, just capture
            )
            
            if not result.get("success"):
                error_msg = result.get("message", result.get("error", "Unknown error"))
                return f"[UE_ERROR] Blueprint capture failed:\n{error_msg}"
            
            lines = [
                "✅ Blueprint screenshot captured successfully!",
                f"📸 File: {result.get('filename', 'Unknown')}",
                f"💾 Path: {result.get('path', 'Unknown')}"
            ]
            
            return "\n".join(lines)
        except Exception as e:
            return f"[UE_ERROR] capture_blueprint failed: {e}"
    
    def _list_blueprints(self) -> str:
        """List available blueprints in the project."""
        if not self.config.get("enable_blueprint_capture", True):
            return "[UE_ERROR] Blueprint operations are disabled in configuration"
        
        try:
            result = self.blueprint_capture.list_available_blueprints()
            
            if result.get("error"):
                return f"[UE_ERROR] {result['error']}"
            
            count = result.get("count", 0)
            lines = [f"📋 Found {count} Blueprints in project:\n"]
            
            for bp in result.get("blueprints", [])[:15]:
                lines.append(f"  • {bp.get('name', 'Unknown')} - {bp.get('path', '')}")
            
            if count > 15:
                lines.append(f"\n... and {count - 15} more")
            
            return "\n".join(lines)
        except Exception as e:
            return f"[UE_ERROR] list_blueprints failed: {e}"


# Global executor instance
_executor: Optional[ActionExecutor] = None


def get_executor() -> ActionExecutor:
    """Get or create the global action executor."""
    global _executor
    if _executor is None:
        _executor = ActionExecutor()
    return _executor
