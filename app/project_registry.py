"""
Project Registry - Manages connected UE5 projects
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json


class ProjectRegistry:
    """Manages multiple UE5 project connections."""
    
    def __init__(self):
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.active_project_id: Optional[str] = None
        self.registry_file = Path("project_registry.json")
        self._load_registry()
    
    def register_project(
        self,
        project_id: str,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register or update a UE5 project.
        
        Args:
            project_id: Unique project identifier (hash of project path)
            project_data: Project metadata from UE5 client
        
        Returns:
            Registration result
        """
        self.projects[project_id] = {
            "project_id": project_id,
            "name": project_data.get("name", "Unknown Project"),
            "path": project_data.get("path", ""),
            "version": project_data.get("version", "5.6"),
            "metadata": project_data.get("metadata", {}),
            "registered_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Set as active if first project or no active project
        if not self.active_project_id or len(self.projects) == 1:
            self.active_project_id = project_id
        
        self._save_registry()
        
        return {
            "success": True,
            "project_id": project_id,
            "is_active": self.active_project_id == project_id
        }
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID."""
        return self.projects.get(project_id)
    
    def get_active_project(self) -> Optional[Dict[str, Any]]:
        """Get currently active project."""
        if self.active_project_id:
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
        return [
            {
                **project,
                "is_active": project["project_id"] == self.active_project_id
            }
            for project in self.projects.values()
        ]
    
    def update_project_metadata(
        self,
        project_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update project metadata."""
        if project_id not in self.projects:
            return {
                "success": False,
                "error": f"Project not found: {project_id}"
            }
        
        self.projects[project_id]["metadata"] = metadata
        self.projects[project_id]["last_updated"] = datetime.now().isoformat()
        self._save_registry()
        
        return {"success": True, "project_id": project_id}
    
    def _save_registry(self):
        """Save registry to disk."""
        data = {
            "active_project_id": self.active_project_id,
            "projects": self.projects
        }
        
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)
    
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
