"""
File scanner for identifying files that need cleanup.
"""

from pathlib import Path
from typing import List, Dict, Set
import hashlib
from collections import defaultdict

from .cleanup_rules import CleanupRules, FileCategory


class FileScanner:
    """Scans project files and identifies cleanup candidates."""
    
    def __init__(self, root_path: Path = None):
        """Initialize scanner with project root path."""
        self.root_path = root_path or Path.cwd()
        self.cleanup_rules = CleanupRules()
    
    def scan_project(self, exclude_dirs: Set[str] = None) -> Dict[str, List[Path]]:
        """Scan project and categorize files for cleanup."""
        if exclude_dirs is None:
            exclude_dirs = {'.git', '.pythonlibs', 'venv', '.venv', 'node_modules'}
        
        results = defaultdict(list)
        
        for file_path in self._walk_directory(self.root_path, exclude_dirs):
            if self.cleanup_rules.is_protected_path(file_path):
                continue
            
            category_info = self.cleanup_rules.categorize_file(file_path)
            if category_info:
                category = category_info['category']
                results[category].append({
                    'path': file_path,
                    'info': category_info
                })
        
        return dict(results)
    
    def find_duplicates(self, directories: List[Path] = None) -> Dict[str, List[Path]]:
        """Find duplicate files by content hash."""
        if directories is None:
            directories = [self.root_path]
        
        hash_map = defaultdict(list)
        
        for directory in directories:
            for file_path in directory.rglob('*'):
                if file_path.is_file() and not self.cleanup_rules.is_protected_path(file_path):
                    try:
                        file_hash = self._hash_file(file_path)
                        hash_map[file_hash].append(file_path)
                    except Exception:
                        pass
        
        return {k: v for k, v in hash_map.items() if len(v) > 1}
    
    def find_large_files(self, min_size_mb: int = 10) -> List[Dict]:
        """Find files larger than specified size."""
        min_bytes = min_size_mb * 1024 * 1024
        large_files = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and not self.cleanup_rules.is_protected_path(file_path):
                try:
                    size = file_path.stat().st_size
                    if size > min_bytes:
                        large_files.append({
                            'path': file_path,
                            'size_mb': round(size / (1024 * 1024), 2)
                        })
                except Exception:
                    pass
        
        return sorted(large_files, key=lambda x: x['size_mb'], reverse=True)
    
    def find_empty_directories(self) -> List[Path]:
        """Find empty directories in the project."""
        empty_dirs = []
        
        for dir_path in self.root_path.rglob('*'):
            if dir_path.is_dir() and not self.cleanup_rules.is_protected_path(dir_path):
                try:
                    if not any(dir_path.iterdir()):
                        empty_dirs.append(dir_path)
                except Exception:
                    pass
        
        return empty_dirs
    
    def find_old_files(self, days: int = 90) -> List[Dict]:
        """Find files not modified in specified days."""
        import time
        
        threshold = time.time() - (days * 24 * 60 * 60)
        old_files = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and not self.cleanup_rules.is_protected_path(file_path):
                try:
                    mtime = file_path.stat().st_mtime
                    if mtime < threshold:
                        old_files.append({
                            'path': file_path,
                            'days_old': int((time.time() - mtime) / (24 * 60 * 60))
                        })
                except Exception:
                    pass
        
        return sorted(old_files, key=lambda x: x['days_old'], reverse=True)
    
    def _walk_directory(self, path: Path, exclude_dirs: Set[str]) -> List[Path]:
        """Walk directory excluding specified directories."""
        files = []
        
        for item in path.rglob('*'):
            if item.is_file():
                skip = False
                for exclude in exclude_dirs:
                    if exclude in str(item):
                        skip = True
                        break
                if not skip:
                    files.append(item)
        
        return files
    
    def _hash_file(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        
        return sha256.hexdigest()
