"""
Operations manager for standard project operations.
"""

from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import json
from datetime import datetime

from .deployment import DeploymentOps
from .testing import TestingOps
from .maintenance import MaintenanceOps


class OpsManager:
    """Central manager for all standard operations."""
    
    def __init__(self, root_path: Path = None):
        """Initialize operations manager."""
        self.root_path = root_path or Path.cwd()
        self.deployment = DeploymentOps(self.root_path)
        self.testing = TestingOps(self.root_path)
        self.maintenance = MaintenanceOps(self.root_path)
        self.ops_log = []
    
    def run_operation(self, operation: str, **kwargs) -> Dict:
        """Run a standard operation by name."""
        operations_map = {
            'test': lambda **kw: self.testing.run_all_tests(**kw),
            'test_backend': lambda **kw: self.testing.run_backend_tests(**kw),
            'test_unit': lambda **kw: self.testing.run_unit_tests(**kw),
            'test_integration': lambda **kw: self.testing.run_integration_tests(**kw),
            'deploy_prepare': lambda **kw: self.deployment.prepare_deployment(**kw),
            'deploy_validate': lambda **kw: self.deployment.validate_deployment(),
            'health_check': lambda **kw: self.maintenance.health_check(),
            'update_dependencies': lambda **kw: self.maintenance.update_dependencies(**kw),
            'validate_structure': lambda **kw: self.maintenance.validate_project_structure(),
        }
        
        if operation not in operations_map:
            raise ValueError(f"Unknown operation: {operation}")
        
        print(f"🚀 Running operation: {operation}")
        
        result = operations_map[operation](**kwargs)
        
        self._log_operation(operation, result)
        
        return result
    
    def get_available_operations(self) -> List[Dict]:
        """Get list of available operations."""
        return [
            {
                'name': 'test',
                'description': 'Run all tests (may timeout on large suites)',
                'category': 'testing'
            },
            {
                'name': 'test_backend',
                'description': 'Run backend API tests (30 tests, fast & reliable)',
                'category': 'testing'
            },
            {
                'name': 'test_unit',
                'description': 'Run unit tests only',
                'category': 'testing'
            },
            {
                'name': 'test_integration',
                'description': 'Run integration tests only',
                'category': 'testing'
            },
            {
                'name': 'deploy_prepare',
                'description': 'Prepare project for deployment',
                'category': 'deployment'
            },
            {
                'name': 'deploy_validate',
                'description': 'Validate deployment readiness',
                'category': 'deployment'
            },
            {
                'name': 'health_check',
                'description': 'Run project health check',
                'category': 'maintenance'
            },
            {
                'name': 'update_dependencies',
                'description': 'Update project dependencies',
                'category': 'maintenance'
            },
            {
                'name': 'validate_structure',
                'description': 'Validate project structure',
                'category': 'maintenance'
            },
        ]
    
    def save_ops_log(self, filepath: Path = None):
        """Save operations log to file."""
        if filepath is None:
            filepath = self.root_path / "automation" / "logs" / f"ops_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.ops_log, f, indent=2)
        
        print(f"📝 Operations log saved to: {filepath}")
    
    def _log_operation(self, operation: str, result: Dict):
        """Log operation execution."""
        self.ops_log.append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'result': result,
            'success': result.get('success', False)
        })
