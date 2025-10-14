"""
Testing operations automation.

Due to environment limitations with pytest in automated contexts, 
this module provides a wrapper around a standalone test script.
"""

from pathlib import Path
from typing import Dict
import subprocess


class TestingOps:
    """Handles testing-related operations."""
    
    def __init__(self, root_path: Path):
        """Initialize testing operations."""
        self.root_path = root_path
        self.tests_dir = root_path / "tests"
        self.test_script = root_path / "run_tests.sh"
    
    def _run_test_script(self, test_type: str) -> Dict:
        """Run the standalone test script."""
        
        if not self.test_script.exists():
            return {
                'success': False,
                'error': f'Test script not found: {self.test_script}',
                'workaround': 'Run pytest directly: python -m pytest tests/backend/ -v'
            }
        
        try:
            # Use the standalone script which works reliably
            result = subprocess.run(
                [str(self.test_script), test_type],
                cwd=str(self.root_path),
                capture_output=False,  # Let output stream directly
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Test script timed out after 60s'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_backend_tests(self, verbose: bool = False, **kwargs) -> Dict:
        """Run backend API tests only (fast, reliable subset)."""
        print("🧪 Running backend tests via standalone script...")
        print("-" * 60)
        
        result = self._run_test_script('backend')
        
        print("-" * 60)
        
        if result.get('success'):
            result['test_count'] = '30 backend API tests'
        
        return result
    
    def run_all_tests(self, verbose: bool = False, **kwargs) -> Dict:
        """Run all tests in the project."""
        print("🧪 Running all tests via standalone script...")
        print("-" * 60)
        
        result = self._run_test_script('all')
        
        print("-" * 60)
        
        return result
    
    def run_unit_tests(self, verbose: bool = False, **kwargs) -> Dict:
        """Run unit tests only."""
        print("🧪 Running unit tests via standalone script...")
        print("-" * 60)
        
        result = self._run_test_script('unit')
        
        print("-" * 60)
        
        return result
    
    def run_integration_tests(self, verbose: bool = False, **kwargs) -> Dict:
        """Run integration tests only."""
        print("🧪 Running integration tests via standalone script...")
        print("-" * 60)
        
        result = self._run_test_script('integration')
        
        print("-" * 60)
        
        return result
    
    def run_specific_test(self, test_path: str, verbose: bool = True, **kwargs) -> Dict:
        """Run a specific test file or test."""
        return {
            'success': False,
            'error': 'Use direct command for specific tests',
            'workaround': f'python -m pytest {test_path} -v'
        }
    
    def get_test_coverage(self, **kwargs) -> Dict:
        """Get test coverage report."""
        return {
            'success': False,
            'error': 'Use direct command for coverage',
            'workaround': 'python -m pytest --cov=app --cov=ue5_client tests/'
        }
