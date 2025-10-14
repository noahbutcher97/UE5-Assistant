"""
Testing operations automation.
"""

from pathlib import Path
from typing import Dict, List
import subprocess
import os
import sys


class TestingOps:
    """Handles testing-related operations."""
    
    def __init__(self, root_path: Path):
        """Initialize testing operations."""
        self.root_path = root_path
        self.tests_dir = root_path / "tests"
    
    def run_backend_tests(self, verbose: bool = False, **kwargs) -> Dict:
        """Run backend API tests only (fast, reliable subset)."""
        print("🧪 Running backend tests...")
        
        try:
            cmd = [
                sys.executable, '-m', 'pytest', 
                'tests/backend/', 
                '-q', '--tb=line',
                '--color=no'
            ]
            
            # Run without capture to avoid timeout issues
            result = subprocess.run(
                cmd,
                cwd=str(self.root_path),
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'test_count': '30 backend API tests',
                'note': 'Tests executed successfully' if result.returncode == 0 else 'Tests failed'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Tests timed out after 30s'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_all_tests(self, verbose: bool = False, **kwargs) -> Dict:
        """Run all tests in the project."""
        print("🧪 Running all tests...")
        
        if not self.tests_dir.exists():
            return {
                'success': False,
                'error': 'Tests directory not found'
            }
        
        try:
            cmd = [
                sys.executable, '-m', 'pytest', 
                'tests/', 
                '-q', '--tb=line',
                '--color=no'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(self.root_path),
                timeout=120
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'note': 'Tests executed successfully' if result.returncode == 0 else 'Tests failed'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Tests timed out after 2 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_unit_tests(self, verbose: bool = False, **kwargs) -> Dict:
        """Run unit tests only."""
        print("🧪 Running unit tests...")
        
        try:
            cmd = [sys.executable, '-m', 'pytest', 'tests/backend/', 'tests/ue5_client/', '-q']
            
            result = subprocess.run(
                cmd,
                cwd=str(self.root_path),
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_integration_tests(self, verbose: bool = False, **kwargs) -> Dict:
        """Run integration tests only."""
        print("🧪 Running integration tests...")
        
        try:
            cmd = [sys.executable, '-m', 'pytest', 'tests/integration/', '-q']
            
            result = subprocess.run(
                cmd,
                cwd=str(self.root_path),
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_specific_test(self, test_path: str, verbose: bool = True, **kwargs) -> Dict:
        """Run a specific test file or test."""
        print(f"🧪 Running test: {test_path}")
        
        try:
            cmd = [sys.executable, '-m', 'pytest', test_path, '-v' if verbose else '-q']
            
            result = subprocess.run(
                cmd,
                cwd=str(self.root_path),
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_test_coverage(self, **kwargs) -> Dict:
        """Get test coverage report (if coverage is installed)."""
        print("📊 Generating test coverage report...")
        
        try:
            cmd = [sys.executable, '-m', 'pytest', '--cov=app', '--cov=ue5_client', 'tests/']
            
            result = subprocess.run(
                cmd,
                cwd=str(self.root_path),
                timeout=120
            )
            
            return {
                'success': result.returncode == 0
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
