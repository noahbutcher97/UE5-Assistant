"""File system service for secure file operations."""
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.models import FileContext, FileEntry


class FileSystemService:
    """Handles secure file system operations with path validation."""
    
    def __init__(
        self, allowed_roots: Optional[List[str]] = None, max_depth: int = 10
    ):
        """
        Initialize file system service.
        
        Args:
            allowed_roots: List of allowed root paths. If None, uses
                current working directory.
            max_depth: Maximum directory traversal depth for security.
        """
        self.max_depth = max_depth
        self.allowed_roots = allowed_roots or [os.getcwd()]
        self.allowed_roots = [Path(root).resolve() for root in self.allowed_roots]
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is within allowed roots using secure containment test."""
        resolved_path = Path(path).resolve()
        for root in self.allowed_roots:
            try:
                resolved_path.relative_to(root)
                return True
            except ValueError:
                continue
        return False
    
    def _get_file_entry(self, path: Path, include_content: bool = False) -> FileEntry:
        """Convert a path to a FileEntry."""
        stat = path.stat()
        entry = FileEntry(
            path=str(path),
            name=path.name,
            type="directory" if path.is_dir() else "file",
            extension=path.suffix if path.is_file() else None,
            size=stat.st_size if path.is_file() else None,
            modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
        )
        
        if include_content and path.is_file():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    entry.content = f.read()
            except Exception:
                entry.content = None
        
        return entry
    
    def list_directory(
        self, directory_path: str, recursive: bool = False
    ) -> FileContext:
        """List files in a directory."""
        if not self._is_path_allowed(directory_path):
            raise PermissionError(f"Access denied to path: {directory_path}")
        
        path = Path(directory_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {directory_path}")
        
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")
        
        files = []
        total_size = 0
        
        if recursive:
            for root, _, filenames in os.walk(path):
                depth = len(Path(root).relative_to(path).parts)
                if depth > self.max_depth:
                    continue
                
                for filename in filenames:
                    file_path = Path(root) / filename
                    entry = self._get_file_entry(file_path)
                    files.append(entry)
                    total_size += entry.size or 0
        else:
            for item in path.iterdir():
                entry = self._get_file_entry(item)
                files.append(entry)
                if entry.type == "file":
                    total_size += entry.size or 0
        
        return FileContext(
            root_path=str(path),
            files=files,
            total_files=len(files),
            total_size=total_size
        )
    
    def read_file(self, file_path: str) -> FileEntry:
        """Read a file's content."""
        if not self._is_path_allowed(file_path):
            raise PermissionError(f"Access denied to file: {file_path}")
        
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise IsADirectoryError(f"Not a file: {file_path}")
        
        return self._get_file_entry(path, include_content=True)
    
    def search_files(
        self,
        root_path: str,
        pattern: Optional[str] = None,
        extension: Optional[str] = None,
        max_results: int = 100
    ) -> FileContext:
        """Search for files matching criteria."""
        if not self._is_path_allowed(root_path):
            raise PermissionError(f"Access denied to path: {root_path}")
        
        path = Path(root_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {root_path}")
        
        files = []
        total_size = 0
        
        for root, _, filenames in os.walk(path):
            depth = len(Path(root).relative_to(path).parts)
            if depth > self.max_depth:
                continue
            
            for filename in filenames:
                if len(files) >= max_results:
                    break
                
                if pattern and pattern.lower() not in filename.lower():
                    continue
                
                if extension and not filename.endswith(extension):
                    continue
                
                file_path = Path(root) / filename
                entry = self._get_file_entry(file_path)
                files.append(entry)
                total_size += entry.size or 0
        
        search_query = (
            f"pattern={pattern}, ext={extension}"
            if pattern or extension
            else None
        )
        
        return FileContext(
            root_path=str(path),
            files=files,
            search_query=search_query,
            total_files=len(files),
            total_size=total_size
        )
