"""
Maintenance operations automation.
"""

from pathlib import Path
from typing import Dict, List
import subprocess
import json


class MaintenanceOps:
    """Handles maintenance-related operations."""
    
    def __init__(self, root_path: Path):
        """Initialize maintenance operations."""
        self.root_path = root_path
    
    def health_check(self) -> Dict:
        """Run comprehensive project health check."""
        print("🏥 Running project health check...")
        
        checks = {
            'project_structure': self._check_project_structure(),
            'dependencies': self._check_dependencies_health(),
            'configuration': self._check_configuration(),
            'api_health': self._check_api_health(),
            'client_health': self._check_client_health()
        }
        
        all_healthy = all(check['healthy'] for check in checks.values())
        
        return {
            'success': True,
            'healthy': all_healthy,
            'checks': checks
        }
    
    def update_dependencies(self, dry_run: bool = True, **kwargs) -> Dict:
        """Update project dependencies."""
        print(f"📦 Updating dependencies (dry_run={dry_run})...")
        
        results = {
            'success': True,
            'updated': [],
            'errors': []
        }
        
        try:
            if dry_run:
                result = subprocess.run(
                    ['python', '-m', 'pip', 'list', '--outdated'],
                    capture_output=True,
                    text=True,
                    cwd=self.root_path
                )
                
                results['outdated_packages'] = result.stdout
            else:
                result = subprocess.run(
                    ['python', '-m', 'pip', 'install', '--upgrade', '-r', 'requirements.txt'],
                    capture_output=True,
                    text=True,
                    cwd=self.root_path
                )
                
                results['success'] = result.returncode == 0
                results['output'] = result.stdout
                
        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
        
        return results
    
    def validate_project_structure(self) -> Dict:
        """Validate project structure matches expected layout."""
        print("📁 Validating project structure...")
        
        expected_structure = {
            'app': ['routes.py', 'config.py', 'models.py', 'dashboard.py'],
            'app/services': ['openai_client.py', 'conversation.py', 'filtering.py'],
            'app/templates': ['unified_dashboard.html'],
            'ue5_client/AIAssistant': [
                'core', 'network', 'execution', 'system', 
                'tools', 'collection', 'ui', 'troubleshoot'
            ],
            'tests': ['backend', 'integration', 'ue5_client', 'ui'],
            'automation': ['cleanup', 'standard_ops']
        }
        
        validation = {
            'valid': True,
            'missing': [],
            'extra': []
        }
        
        for directory, expected_items in expected_structure.items():
            dir_path = self.root_path / directory
            
            if not dir_path.exists():
                validation['valid'] = False
                validation['missing'].append(directory)
                continue
            
            for item in expected_items:
                item_path = dir_path / item
                if not item_path.exists():
                    validation['missing'].append(f"{directory}/{item}")
                    validation['valid'] = False
        
        return validation
    
    def _check_project_structure(self) -> Dict:
        """Check if core project structure is intact."""
        required_dirs = ['app', 'ue5_client', 'tests', 'automation']
        missing = []
        
        for dir_name in required_dirs:
            if not (self.root_path / dir_name).exists():
                missing.append(dir_name)
        
        return {
            'healthy': len(missing) == 0,
            'missing_directories': missing
        }
    
    def _check_dependencies_health(self) -> Dict:
        """Check if all dependencies are properly installed."""
        requirements_file = self.root_path / "requirements.txt"
        
        if not requirements_file.exists():
            return {
                'healthy': False,
                'error': 'requirements.txt not found'
            }
        
        try:
            result = subprocess.run(
                ['python', '-m', 'pip', 'check'],
                capture_output=True,
                text=True,
                cwd=self.root_path
            )
            
            return {
                'healthy': result.returncode == 0,
                'output': result.stdout
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_configuration(self) -> Dict:
        """Check if configuration files are valid."""
        config_file = self.root_path / "app" / "data" / "config.json"
        
        if not config_file.exists():
            return {
                'healthy': False,
                'error': 'config.json not found'
            }
        
        try:
            with open(config_file) as f:
                config = json.load(f)
            
            required_keys = ['model', 'temperature', 'max_tokens']
            missing = [key for key in required_keys if key not in config]
            
            return {
                'healthy': len(missing) == 0,
                'missing_keys': missing
            }
        except json.JSONDecodeError:
            return {
                'healthy': False,
                'error': 'Invalid JSON in config.json'
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_api_health(self) -> Dict:
        """Check if API routes are properly defined."""
        routes_file = self.root_path / "app" / "routes.py"
        
        if not routes_file.exists():
            return {
                'healthy': False,
                'error': 'routes.py not found'
            }
        
        try:
            with open(routes_file) as f:
                content = f.read()
            
            required_routes = [
                '/describe_viewport',
                '/execute_command',
                '/api/projects',
                '/dashboard'
            ]
            
            missing = [route for route in required_routes if route not in content]
            
            return {
                'healthy': len(missing) == 0,
                'missing_routes': missing
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_client_health(self) -> Dict:
        """Check if UE5 client structure is intact."""
        client_dir = self.root_path / "ue5_client" / "AIAssistant"
        
        if not client_dir.exists():
            return {
                'healthy': False,
                'error': 'UE5 client directory not found'
            }
        
        required_modules = ['core', 'network', 'execution', 'system']
        missing = []
        
        for module in required_modules:
            if not (client_dir / module).exists():
                missing.append(module)
        
        return {
            'healthy': len(missing) == 0,
            'missing_modules': missing
        }
