"""
Cleanup rules and patterns for identifying temporary, redundant, and outdated files.
"""

from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass
from enum import Enum


class FileCategory(Enum):
    """Categories for file classification."""
    TEMPORARY = "temporary"
    REDUNDANT = "redundant"
    OUTDATED = "outdated"
    BUILD_ARTIFACT = "build_artifact"
    DUPLICATE = "duplicate"
    MISPLACED = "misplaced"
    ARCHIVE = "archive"


@dataclass
class CleanupRule:
    """Represents a cleanup rule."""
    name: str
    category: FileCategory
    patterns: List[str]
    directories: List[str]
    description: str
    safe_to_auto_delete: bool = False


class CleanupRules:
    """Manages cleanup rules for the project."""
    
    @staticmethod
    def get_all_rules() -> List[CleanupRule]:
        """Get all cleanup rules."""
        return [
            CleanupRule(
                name="Python Cache Files",
                category=FileCategory.BUILD_ARTIFACT,
                patterns=["*.pyc", "*.pyo"],
                directories=["__pycache__"],
                description="Python bytecode cache files",
                safe_to_auto_delete=True
            ),
            CleanupRule(
                name="Test Cache",
                category=FileCategory.BUILD_ARTIFACT,
                patterns=[".pytest_cache", ".coverage", "htmlcov"],
                directories=[".pytest_cache"],
                description="Test framework cache files",
                safe_to_auto_delete=True
            ),
            CleanupRule(
                name="Temporary Logs",
                category=FileCategory.TEMPORARY,
                patterns=["Pasted-*.txt", "*.tmp", "*.log.old"],
                directories=["attached_assets"],
                description="Temporary pasted logs and old log files",
                safe_to_auto_delete=False
            ),
            CleanupRule(
                name="Backup Files",
                category=FileCategory.TEMPORARY,
                patterns=["*.bak", "*.backup", "*~", "*.swp"],
                directories=[],
                description="Editor backup and swap files",
                safe_to_auto_delete=True
            ),
            CleanupRule(
                name="OS Cache",
                category=FileCategory.BUILD_ARTIFACT,
                patterns=[".DS_Store", "Thumbs.db", "desktop.ini"],
                directories=[],
                description="Operating system cache files",
                safe_to_auto_delete=True
            ),
            CleanupRule(
                name="Old Documentation",
                category=FileCategory.ARCHIVE,
                patterns=["*_SUMMARY.md", "*_OLD.md", "DEPRECATED_*.md"],
                directories=["archive/docs"],
                description="Archived documentation and summaries",
                safe_to_auto_delete=False
            ),
            CleanupRule(
                name="Duplicate Test Files",
                category=FileCategory.REDUNDANT,
                patterns=["test_*_old.py", "test_*_backup.py"],
                directories=["tests"],
                description="Old or backup test files",
                safe_to_auto_delete=False
            ),
            CleanupRule(
                name="Build Directories",
                category=FileCategory.BUILD_ARTIFACT,
                patterns=["dist", "build", "*.egg-info"],
                directories=["dist", "build"],
                description="Python build and distribution directories",
                safe_to_auto_delete=True
            ),
        ]
    
    @staticmethod
    def get_protected_paths() -> Set[str]:
        """Get paths that should never be deleted."""
        return {
            ".git",
            ".gitignore",
            "node_modules",
            ".pythonlibs",  # External dependencies
            "venv",
            ".venv",
            "requirements.txt",
            "pyproject.toml",
            "main.py",
            "replit.md",
            "README.md"
        }
    
    @staticmethod
    def get_safe_auto_delete_rules() -> List[CleanupRule]:
        """Get rules that are safe for automatic deletion."""
        return [rule for rule in CleanupRules.get_all_rules() if rule.safe_to_auto_delete]
    
    @staticmethod
    def get_manual_review_rules() -> List[CleanupRule]:
        """Get rules that require manual review before deletion."""
        return [rule for rule in CleanupRules.get_all_rules() if not rule.safe_to_auto_delete]
    
    @staticmethod
    def is_protected_path(path: Path) -> bool:
        """Check if a path is protected from deletion."""
        protected = CleanupRules.get_protected_paths()
        path_str = str(path)
        
        for protected_path in protected:
            if protected_path in path_str:
                return True
        
        return False
    
    @staticmethod
    def categorize_file(file_path: Path) -> Dict[str, any]:
        """Categorize a file based on cleanup rules."""
        for rule in CleanupRules.get_all_rules():
            for pattern in rule.patterns:
                if file_path.match(pattern):
                    return {
                        "path": file_path,
                        "rule": rule.name,
                        "category": rule.category.value,
                        "safe_to_auto_delete": rule.safe_to_auto_delete,
                        "description": rule.description
                    }
        
        return None
