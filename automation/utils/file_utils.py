"""
File utility functions for automation.
"""

from pathlib import Path
from typing import List, Set
from datetime import datetime
import shutil


class FileUtils:
    """Utility functions for file operations."""
    
    @staticmethod
    def safe_delete(path: Path, protected_paths: Set[str] = None) -> bool:
        """Safely delete a file or directory."""
        if protected_paths is None:
            protected_paths = {'.git', 'venv', '.pythonlibs'}
        
        path_str = str(path)
        for protected in protected_paths:
            if protected in path_str:
                return False
        
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_directory_size(path: Path) -> int:
        """Get total size of directory in bytes."""
        total = 0
        try:
            for file in path.rglob('*'):
                if file.is_file():
                    total += file.stat().st_size
        except Exception:
            pass
        return total
    
    @staticmethod
    def create_backup(source: Path, backup_dir: Path = None) -> Path:
        """Create backup of file or directory."""
        if backup_dir is None:
            backup_dir = source.parent / "backups"
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{source.name}.backup_{timestamp}"
        backup_path = backup_dir / backup_name
        
        if source.is_file():
            shutil.copy2(source, backup_path)
        elif source.is_dir():
            shutil.copytree(source, backup_path)
        
        return backup_path
    
    @staticmethod
    def find_files_by_pattern(root: Path, pattern: str) -> List[Path]:
        """Find all files matching pattern."""
        return list(root.rglob(pattern))
    
    @staticmethod
    def ensure_directory(path: Path):
        """Ensure directory exists."""
        path.mkdir(parents=True, exist_ok=True)
