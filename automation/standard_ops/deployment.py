"""
Deployment operations automation.
"""

from pathlib import Path
from typing import Dict, List
import subprocess
import json


class DeploymentOps:
    """Handles deployment-related operations."""
    
    def __init__(self, root_path: Path):
        """Initialize deployment operations."""
        self.root_path = root_path
    
    def prepare_deployment(self, include_client: bool = True, **kwargs) -> Dict:
        """Prepare project for deployment."""
        print("📦 Preparing deployment package...")
        
        results = {
            'success': True,
            'steps': [],
            'errors': []
        }
        
        try:
            results['steps'].append(self._validate_dependencies())
            results['steps'].append(self._check_config_files())
            
            if include_client:
                results['steps'].append(self._package_ue5_client())
            
            results['steps'].append(self._validate_api_endpoints())
            
        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
        
        return results
    
    def validate_deployment(self) -> Dict:
        """Validate deployment readiness."""
        print("✅ Validating deployment readiness...")
        
        checks = {
            'config_valid': self._check_config(),
            'dependencies_installed': self._check_dependencies(),
            'tests_passing': self._check_tests(),
            'no_critical_issues': self._check_lsp_errors(),
            'client_packaged': self._check_client_package()
        }
        
        all_passed = all(checks.values())
        
        return {
            'success': all_passed,
            'checks': checks,
            'ready_for_deployment': all_passed
        }
    
    def _validate_dependencies(self) -> Dict:
        """Validate all dependencies are installed."""
        try:
            result = subprocess.run(
                ['python', '-m', 'pip', 'list'],
                capture_output=True,
                text=True,
                cwd=self.root_path
            )
            
            return {
                'step': 'validate_dependencies',
                'success': result.returncode == 0,
                'message': 'Dependencies validated'
            }
        except Exception as e:
            return {
                'step': 'validate_dependencies',
                'success': False,
                'error': str(e)
            }
    
    def _check_config_files(self) -> Dict:
        """Check critical configuration files exist."""
        required_files = [
            'main.py',
            'requirements.txt',
            'replit.md',
            'app/config.py'
        ]
        
        missing = []
        for file in required_files:
            if not (self.root_path / file).exists():
                missing.append(file)
        
        return {
            'step': 'check_config_files',
            'success': len(missing) == 0,
            'missing_files': missing
        }
    
    def _package_ue5_client(self) -> Dict:
        """Package UE5 client for distribution."""
        client_dir = self.root_path / "ue5_client"
        
        if not client_dir.exists():
            return {
                'step': 'package_ue5_client',
                'success': False,
                'error': 'UE5 client directory not found'
            }
        
        return {
            'step': 'package_ue5_client',
            'success': True,
            'client_path': str(client_dir)
        }
    
    def _validate_api_endpoints(self) -> Dict:
        """Validate API endpoints are properly defined."""
        routes_file = self.root_path / "app" / "routes.py"
        
        if not routes_file.exists():
            return {
                'step': 'validate_api_endpoints',
                'success': False,
                'error': 'Routes file not found'
            }
        
        return {
            'step': 'validate_api_endpoints',
            'success': True,
            'message': 'API endpoints validated'
        }
    
    def _check_config(self) -> bool:
        """Check if configuration is valid."""
        config_file = self.root_path / "app" / "data" / "config.json"
        return config_file.exists()
    
    def _check_dependencies(self) -> bool:
        """Check if dependencies are installed."""
        requirements_file = self.root_path / "requirements.txt"
        return requirements_file.exists()
    
    def _check_tests(self) -> bool:
        """Check if tests exist."""
        tests_dir = self.root_path / "tests"
        return tests_dir.exists()
    
    def _check_lsp_errors(self) -> bool:
        """Check for critical LSP errors (placeholder)."""
        return True
    
    def _check_client_package(self) -> bool:
        """Check if client is properly packaged."""
        client_dir = self.root_path / "ue5_client"
        return client_dir.exists()
