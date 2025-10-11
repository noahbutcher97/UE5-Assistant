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
from .config import get_config
from .context_collector import get_collector
from .utils import Logger


class ActionExecutor:
    """Executes actions in Unreal Engine based on AI commands."""

    def __init__(self):
        self.logger = Logger("ActionExecutor", verbose=False)
        self.config = get_config()
        self.actions: Dict[str, Callable[[], str]] = {}
        self._register_default_actions()

    def _register_default_actions(self) -> None:
        """Register the default action set."""
        self.register("describe_viewport", self._describe_viewport)
        self.register("list_actors", self._list_actors)
        self.register("get_selected_info", self._get_selected_info)

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


# Global executor instance
_executor: Optional[ActionExecutor] = None


def get_executor() -> ActionExecutor:
    """Get or create the global action executor."""
    global _executor
    if _executor is None:
        _executor = ActionExecutor()
    return _executor
