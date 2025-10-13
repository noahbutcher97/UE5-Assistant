"""
Project Registry - Manages connected UE5 projects
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProjectRegistry:
    """Manages multiple UE5 project connections."""

    def __init__(self, registry_file: Optional[Path] = None):
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.active_project_id: Optional[str] = None
        self.registry_file = registry_file or Path(
            "data/project_registry.json")
        # Ensure parent directory exists
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_registry()

    def register_project(self, project_id: str,
                         project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register or update a UE5 project.

        Args:
            project_id: Unique project identifier (hash of project path)
            project_data: Project metadata from UE5 client

        Returns:
            Registration result
        """
        is_new = project_id not in self.projects

        # Preserve existing connection_mode if updating
        existing_mode = None
        if not is_new and 'connection_mode' in self.projects[project_id]:
            existing_mode = self.projects[project_id]['connection_mode']
            # Only preserve if not explicitly provided in new data
            if 'connection_mode' not in project_data:
                project_data['connection_mode'] = existing_mode

        # Get existing registration time or use current time
        registered_at = self.projects.get(project_id,
                                          {}).get("registered_at",
                                                  datetime.now().isoformat())

        # Build project record
        self.projects[project_id] = {
            "project_id": project_id,
            "name": project_data.get("name", "Unknown Project"),
            "path": project_data.get("path", ""),
            "version": project_data.get("version", "5.6"),
            "metadata": project_data.get("metadata", {}),
            "registered_at": registered_at,
            "last_updated": datetime.now().isoformat(),
        }

        # Add any additional fields from project_data
        excluded_keys = {"name", "path", "version", "metadata"}
        for k, v in project_data.items():
            if k not in excluded_keys:
                self.projects[project_id][k] = v

        # Set as active if first project or no active project
        if not self.active_project_id or len(self.projects) == 1:
            self.active_project_id = project_id

        self._save_registry()

        return {
            "success": True,
            "project_id": project_id,
            "is_new": is_new,
            "is_active": self.active_project_id == project_id
        }

    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """
        Delete a project from the registry.

        Args:
            project_id: Project to delete

        Returns:
            Result dict with success status
        """
        if project_id not in self.projects:
            return {"success": False, "error": "Project not found"}

        # Store project name for response message
        project_name = self.projects[project_id].get("name", project_id)

        # Delete the project
        del self.projects[project_id]

        # If deleting active project, set next available as active
        if self.active_project_id == project_id:
            self.active_project_id = next(iter(self.projects), None)

        self._save_registry()

        return {
            "success": True,
            "message": f"Project '{project_name}' deleted successfully",
            "new_active_project_id": self.active_project_id
        }

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID."""
        return self.projects.get(project_id)

    def get_active_project(self) -> Optional[Dict[str, Any]]:
        """
        Get currently active project.

        Auto-repairs invalid active_project_id by selecting first available.
        """
        # Check if active project ID is valid
        if self.active_project_id and self.active_project_id in self.projects:
            return self.projects.get(self.active_project_id)

        # Auto-repair: If active ID is invalid or gone, find first available
        if self.projects:
            self.active_project_id = next(iter(self.projects))
            self._save_registry()
            return self.projects.get(self.active_project_id)

        return None

    def set_active_project(self, project_id: str) -> Dict[str, Any]:
        """Set active project."""
        if project_id not in self.projects:
            return {
                "success": False,
                "error": f"Project not found: {project_id}"
            }

        self.active_project_id = project_id
        self._save_registry()

        return {
            "success": True,
            "project_id": project_id,
            "project": self.projects[project_id]
        }

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all registered projects."""
        return [{
            **project, "is_active":
            project["project_id"] == self.active_project_id
        } for project in self.projects.values()]

    def update_project_metadata(self, project_id: str,
                                metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update project metadata."""
        if project_id not in self.projects:
            return {
                "success": False,
                "error": f"Project not found: {project_id}"
            }

        self.projects[project_id]["metadata"] = metadata
        self.projects[project_id]["last_updated"] = (
            datetime.now().isoformat())
        self._save_registry()

        return {"success": True, "project_id": project_id}

    def set_connection_mode(self, project_id: str,
                            connection_mode: str) -> Dict[str, Any]:
        """Set connection mode preference for a project."""
        if project_id not in self.projects:
            return {
                "success": False,
                "error": f"Project not found: {project_id}"
            }

        if connection_mode not in ["http", "websocket"]:
            return {
                "success": False,
                "error":
                "Invalid connection mode. Must be 'http' or 'websocket'"
            }

        self.projects[project_id]["connection_mode"] = connection_mode
        self.projects[project_id]["last_updated"] = (
            datetime.now().isoformat())
        self._save_registry()

        return {
            "success": True,
            "project_id": project_id,
            "connection_mode": connection_mode
        }

    def get_connection_mode(self, project_id: str) -> str:
        """Get connection mode preference for a project (default: http)."""
        if project_id in self.projects:
            return self.projects[project_id].get("connection_mode", "http")
        return "http"

    def clear_all_projects(self) -> Dict[str, Any]:
        """
        Clear all projects from registry.

        Returns:
            Result dict with success status and count of deleted projects
        """
        count = len(self.projects)
        self.projects = {}
        self.active_project_id = None
        self._save_registry()

        return {
            "success": True,
            "message": f"Cleared {count} project(s) from registry",
            "count": count
        }

    def _save_registry(self):
        """Save registry to disk."""
        data = {
            "active_project_id": self.active_project_id,
            "projects": self.projects
        }

        try:
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save registry: {e}")

    def _load_registry(self):
        """Load registry from disk."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    self.active_project_id = data.get("active_project_id")
                    self.projects = data.get("projects", {})
            except Exception as e:
                print(f"Failed to load registry: {e}")


# Global registry
_registry: Optional[ProjectRegistry] = None


def get_registry() -> ProjectRegistry:
    """Get the global project registry."""
    global _registry
    if _registry is None:
        _registry = ProjectRegistry()
    return _registry


def reset_registry():
    """Reset the global registry (useful for testing)."""
    global _registry
    _registry = None
