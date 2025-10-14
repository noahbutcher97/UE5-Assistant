"""
Testing operations automation.
"""

from pathlib import Path
from typing import Dict, List
import subprocess


class TestingOps:
    """Handles testing-related operations."""
    
    def __init__(self, root_path: Path):
        """Initialize testing operations."""
        self.root_path = root_path
        self.tests_dir = root_path / "tests"
    
    def run_all_tests(self, verbose: bool = False) -> Dict:
        """Run all tests in the project."""
        print("🧪 Running all tests...")
        
        if not self.tests_dir.exists():
            return {
                'success': False,
                'error': 'Tests directory not found'
            }
        
        try:
            cmd = ['python', '-m', 'pytest', 'tests/', '-v' if verbose else '-q']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root_path,
                timeout=300
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Tests timed out after 5 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_unit_tests(self, verbose: bool = False) -> Dict:
        """Run unit tests only."""
        print("🧪 Running unit tests...")
        
        try:
            cmd = ['python', '-m', 'pytest', 'tests/backend/', 'tests/ue5_client/', '-v' if verbose else '-q']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root_path,
                timeout=180
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'stdout': result.stdout
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_integration_tests(self, verbose: bool = False) -> Dict:
        """Run integration tests only."""
        print("🧪 Running integration tests...")
        
        try:
            cmd = ['python', '-m', 'pytest', 'tests/integration/', '-v' if verbose else '-q']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root_path,
                timeout=180
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'stdout': result.stdout
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_specific_test(self, test_path: str, verbose: bool = True) -> Dict:
        """Run a specific test file or test."""
        print(f"🧪 Running test: {test_path}")
        
        try:
            cmd = ['python', '-m', 'pytest', test_path, '-v' if verbose else '-q']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root_path,
                timeout=120
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_test_coverage(self) -> Dict:
        """Get test coverage report (if coverage is installed)."""
        print("📊 Generating test coverage report...")
        
        try:
            cmd = ['python', '-m', 'pytest', '--cov=app', '--cov=ue5_client', 'tests/']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root_path,
                timeout=300
            )
            
            return {
                'success': result.returncode == 0,
                'coverage_report': result.stdout
            }
            
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'pytest-cov not installed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
