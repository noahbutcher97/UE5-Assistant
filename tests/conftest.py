"""
Pytest fixtures and configuration for UE5 AI Assistant tests.
"""
import tempfile
from pathlib import Path
import pytest
from app.project_registry import ProjectRegistry


@pytest.fixture
def temp_registry_file():
    """Create a temporary registry file for tests."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
        f.write('{"active_project_id": null, "projects": {}}')
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def isolated_registry(temp_registry_file):
    """Create an isolated ProjectRegistry for tests that doesn't pollute production data."""
    registry = ProjectRegistry(registry_file=temp_registry_file)
    return registry


@pytest.fixture(autouse=True, scope="function")
def use_test_registry(temp_registry_file):
    """
    Automatically use isolated test registry for all tests.
    This prevents tests from polluting the production registry file.
    """
    import app.project_registry
    
    # Save original registry
    original_registry = app.project_registry._registry
    
    # Create test registry with temporary file
    app.project_registry._registry = ProjectRegistry(registry_file=temp_registry_file)
    
    yield
    
    # Restore original registry
    app.project_registry._registry = original_registry
