"""
Main project cleaner for automated cleanup operations.
"""

from pathlib import Path
from typing import List, Dict, Optional
import shutil
import json
from datetime import datetime

from .file_scanner import FileScanner
from .cleanup_rules import CleanupRules, FileCategory


class ProjectCleaner:
    """Main class for project cleanup operations."""
    
    def __init__(self, root_path: Path = None, dry_run: bool = True):
        """Initialize project cleaner."""
        self.root_path = root_path or Path.cwd()
        self.dry_run = dry_run
        self.scanner = FileScanner(self.root_path)
        self.cleanup_rules = CleanupRules()
        self.cleanup_log = []
    
    def analyze_project(self) -> Dict:
        """Analyze project and generate cleanup report."""
        print("🔍 Analyzing project for cleanup opportunities...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'root_path': str(self.root_path),
            'categories': {},
            'duplicates': {},
            'large_files': [],
            'empty_directories': [],
            'old_files': [],
            'total_size_to_clean_mb': 0
        }
        
        categorized_files = self.scanner.scan_project()
        for category, files in categorized_files.items():
            report['categories'][category] = {
                'count': len(files),
                'files': [str(f['path']) for f in files],
                'safe_auto_delete': files[0]['info']['safe_to_auto_delete'] if files else False
            }
        
        duplicates = self.scanner.find_duplicates()
        if duplicates:
            report['duplicates'] = {
                hash_val: [str(p) for p in paths]
                for hash_val, paths in duplicates.items()
            }
        
        large_files = self.scanner.find_large_files(min_size_mb=5)
        report['large_files'] = [
            {'path': str(f['path']), 'size_mb': f['size_mb']}
            for f in large_files
        ]
        
        empty_dirs = self.scanner.find_empty_directories()
        report['empty_directories'] = [str(d) for d in empty_dirs]
        
        old_files = self.scanner.find_old_files(days=90)
        report['old_files'] = [
            {'path': str(f['path']), 'days_old': f['days_old']}
            for f in old_files[:20]
        ]
        
        total_size = self._calculate_total_size(categorized_files, large_files)
        report['total_size_to_clean_mb'] = round(total_size, 2)
        
        return report
    
    def auto_cleanup(self, force: bool = False) -> Dict:
        """Perform automatic cleanup of safe-to-delete files."""
        if not force and not self.dry_run:
            raise ValueError("Auto cleanup requires either dry_run=True or force=True")
        
        print(f"🧹 Running auto cleanup (dry_run={self.dry_run})...")
        
        results = {
            'deleted_files': [],
            'deleted_dirs': [],
            'errors': [],
            'total_space_freed_mb': 0
        }
        
        safe_rules = self.cleanup_rules.get_safe_auto_delete_rules()
        
        for rule in safe_rules:
            for pattern in rule.patterns:
                files = list(self.root_path.rglob(pattern))
                for file_path in files:
                    if self.cleanup_rules.is_protected_path(file_path):
                        continue
                    
                    try:
                        size_mb = self._get_size_mb(file_path)
                        
                        if not self.dry_run:
                            if file_path.is_file():
                                file_path.unlink()
                            elif file_path.is_dir():
                                shutil.rmtree(file_path)
                        
                        if file_path.is_file():
                            results['deleted_files'].append(str(file_path))
                        else:
                            results['deleted_dirs'].append(str(file_path))
                        
                        results['total_space_freed_mb'] += size_mb
                        
                        self._log_action('delete', file_path, size_mb, rule.name)
                        
                    except Exception as e:
                        results['errors'].append({
                            'path': str(file_path),
                            'error': str(e)
                        })
        
        results['total_space_freed_mb'] = round(results['total_space_freed_mb'], 2)
        
        return results
    
    def cleanup_category(self, category: FileCategory, confirm: bool = False) -> Dict:
        """Clean up files in a specific category."""
        if not confirm and not self.dry_run:
            raise ValueError("Cleanup requires confirmation when not in dry_run mode")
        
        print(f"🧹 Cleaning up category: {category.value} (dry_run={self.dry_run})...")
        
        results = {
            'deleted_files': [],
            'errors': [],
            'total_space_freed_mb': 0
        }
        
        categorized = self.scanner.scan_project()
        files_in_category = categorized.get(category.value, [])
        
        for file_info in files_in_category:
            file_path = file_info['path']
            
            try:
                size_mb = self._get_size_mb(file_path)
                
                if not self.dry_run:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                
                results['deleted_files'].append(str(file_path))
                results['total_space_freed_mb'] += size_mb
                
                self._log_action('delete', file_path, size_mb, category.value)
                
            except Exception as e:
                results['errors'].append({
                    'path': str(file_path),
                    'error': str(e)
                })
        
        results['total_space_freed_mb'] = round(results['total_space_freed_mb'], 2)
        
        return results
    
    def cleanup_attached_assets(self, pattern: str = "Pasted-*.txt") -> Dict:
        """Clean up temporary files in attached_assets directory."""
        print(f"🧹 Cleaning attached_assets/{pattern} (dry_run={self.dry_run})...")
        
        results = {
            'deleted_files': [],
            'total_space_freed_mb': 0
        }
        
        attached_assets_dir = self.root_path / "attached_assets"
        if not attached_assets_dir.exists():
            return results
        
        for file_path in attached_assets_dir.glob(pattern):
            try:
                size_mb = self._get_size_mb(file_path)
                
                if not self.dry_run:
                    file_path.unlink()
                
                results['deleted_files'].append(str(file_path))
                results['total_space_freed_mb'] += size_mb
                
                self._log_action('delete', file_path, size_mb, 'attached_assets_cleanup')
                
            except Exception as e:
                print(f"❌ Error deleting {file_path}: {e}")
        
        results['total_space_freed_mb'] = round(results['total_space_freed_mb'], 2)
        
        return results
    
    def save_cleanup_log(self, filepath: Path = None):
        """Save cleanup log to file."""
        if filepath is None:
            filepath = self.root_path / "automation" / "logs" / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.cleanup_log, f, indent=2)
        
        print(f"📝 Cleanup log saved to: {filepath}")
    
    def _get_size_mb(self, path: Path) -> float:
        """Get size of file or directory in MB."""
        if path.is_file():
            return path.stat().st_size / (1024 * 1024)
        elif path.is_dir():
            total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return total / (1024 * 1024)
        return 0
    
    def _calculate_total_size(self, categorized_files: Dict, large_files: List) -> float:
        """Calculate total size of files to clean."""
        total = 0
        
        for category, files in categorized_files.items():
            for file_info in files:
                total += self._get_size_mb(file_info['path'])
        
        return total
    
    def _log_action(self, action: str, path: Path, size_mb: float, rule: str):
        """Log cleanup action."""
        self.cleanup_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'path': str(path),
            'size_mb': round(size_mb, 4),
            'rule': rule,
            'dry_run': self.dry_run
        })
