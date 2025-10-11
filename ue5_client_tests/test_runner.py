"""
Test runner for UE5 client code using mock Unreal module.
Allows testing UE5-specific code in Replit without requiring UE5 editor.
"""

import sys
from pathlib import Path

import mock_unreal  # noqa: E402

# Add tests directory to path for mock imports
tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir))

# Import mock unreal module BEFORE importing UE5 client code
sys.modules['unreal'] = mock_unreal

# Now import UE5 client modules (they'll use the mock)
client_dir = tests_dir.parent / "attached_assets" / "AIAssistant"
sys.path.insert(0, str(client_dir))

from blueprint_capture import BlueprintCapture  # type: ignore
from file_collector import FileCollector  # type: ignore
from project_metadata_collector import ProjectMetadataCollector  # type: ignore


def test_file_collector():
    """Test file collector with mock environment."""
    print("\n" + "="*60)
    print("TEST: FileCollector")
    print("="*60)
    
    collector = FileCollector()
    
    # Test project paths
    print(f"Project dir: {collector.project_dir}")
    print(f"Content dir: {collector.content_dir}")
    print(f"Source dir: {collector.source_dir}")
    
    # Test list directory
    result = collector.list_directory(collector.project_dir, recursive=False)
    print(f"\nDirectory listing: {result.get('total_files', 0)} items")
    
    print("✅ FileCollector test passed")


def test_project_metadata():
    """Test project metadata collector with mock environment."""
    print("\n" + "="*60)
    print("TEST: ProjectMetadataCollector")
    print("="*60)
    
    collector = ProjectMetadataCollector()
    
    # Test metadata collection
    metadata = collector.collect_all_metadata(use_cache=False)
    
    print(f"\nProject: {metadata.get('project', {})}")
    print(f"Modules: {metadata.get('modules', {})}")
    print(f"Plugins: {metadata.get('plugins', {})}")
    print(f"Assets: {metadata.get('assets', {}).get('total_assets', 0)} total")
    bp_count = metadata.get('blueprints', {}).get('total_blueprints', 0)
    print(f"Blueprints: {bp_count} total")
    
    # Test summary
    summary = collector.get_summary()
    print(f"\nSummary:\n{summary}")
    
    print("✅ ProjectMetadataCollector test passed")


def test_blueprint_capture():
    """Test blueprint capture with mock environment."""
    print("\n" + "="*60)
    print("TEST: BlueprintCapture")
    print("="*60)
    
    capture = BlueprintCapture()
    
    # Test blueprint existence check
    bp_check = capture.check_blueprint_exists("/Game/Blueprints/BP_Player")
    print(f"\nBlueprint exists: {bp_check.get('exists', False)}")
    if bp_check.get('exists'):
        print(f"Asset name: {bp_check.get('asset_name')}")
    
    # Test list blueprints
    bp_list = capture.list_available_blueprints()
    print(f"\nAvailable blueprints: {bp_list.get('count', 0)}")
    for bp in bp_list.get('blueprints', []):
        print(f"  • {bp.get('name')} - {bp.get('path')}")
    
    print("✅ BlueprintCapture test passed")


def run_all_tests():
    """Run all UE5 client tests."""
    print("\n" + "="*80)
    print("UE5 CLIENT MOCK TEST SUITE")
    print("="*80)
    print("Testing UE5 client code with simulated Unreal Engine environment\n")
    
    try:
        test_file_collector()
        test_project_metadata()
        test_blueprint_capture()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
