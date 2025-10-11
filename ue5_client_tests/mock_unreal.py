"""
Mock Unreal Engine module for testing UE5 client code in non-UE environments.
Simulates the `unreal` module API to enable unit testing and development in Replit.
"""

from pathlib import Path
from typing import Any, List


class MockPaths:
    """Mock implementation of unreal.Paths for testing."""
    
    @staticmethod
    def project_dir() -> str:
        """Return mock project directory."""
        return str(Path(__file__).parent / "mock_project")
    
    @staticmethod
    def project_content_dir() -> str:
        """Return mock content directory."""
        return str(Path(__file__).parent / "mock_project" / "Content")
    
    @staticmethod
    def project_saved_dir() -> str:
        """Return mock saved directory."""
        return str(Path(__file__).parent / "mock_project" / "Saved")
    
    @staticmethod
    def project_config_dir() -> str:
        """Return mock config directory."""
        return str(Path(__file__).parent / "mock_project" / "Config")
    
    @staticmethod
    def get_project_file_path() -> str:
        """Return mock .uproject file path."""
        return str(Path(__file__).parent / "mock_project" / "TestProject.uproject")


class MockAssetData:
    """Mock asset data object."""
    
    def __init__(self, asset_name: str, asset_class: str, package_name: str):
        self.asset_name = asset_name
        self.package_name = package_name
        
        # Mock asset_class_path
        class MockAssetClassPath:
            def __init__(self, name):
                self.asset_name = name
        
        self.asset_class_path = MockAssetClassPath(asset_class)
    
    def get_asset(self):
        """Mock get_asset method."""
        return None


class MockAssetRegistry:
    """Mock asset registry for testing."""
    
    def get_assets(self, ar_filter: Any) -> List[MockAssetData]:
        """Return mock asset list based on filter."""
        # Check filter type
        class_names = getattr(ar_filter, 'class_names', [])
        
        if 'Blueprint' in class_names:
            # Return mock blueprints
            return [
                MockAssetData("BP_Player", "Blueprint", "/Game/Blueprints/BP_Player"),
                MockAssetData("BP_Enemy", "Blueprint", "/Game/Blueprints/BP_Enemy"),
                MockAssetData("BP_GameMode", "Blueprint", "/Game/Core/BP_GameMode"),
            ]
        else:
            # Return mixed assets
            return [
                MockAssetData(
                    "T_Ground", "Texture2D", "/Game/Textures/T_Ground"
                ),
                MockAssetData(
                    "M_Character", "Material", "/Game/Materials/M_Character"
                ),
                MockAssetData(
                    "SK_Character",
                    "SkeletalMesh",
                    "/Game/Meshes/SK_Character"
                ),
                MockAssetData(
                    "BP_Player", "Blueprint", "/Game/Blueprints/BP_Player"
                ),
                MockAssetData(
                    "SFX_Explosion",
                    "SoundWave",
                    "/Game/Audio/SFX_Explosion"
                ),
            ]


class MockAssetRegistryHelpers:
    """Mock asset registry helpers."""
    
    @staticmethod
    def get_asset_registry() -> MockAssetRegistry:
        """Return mock asset registry."""
        return MockAssetRegistry()


class MockARFilter:
    """Mock ARFilter class."""
    
    def __init__(self, class_names=None, package_paths=None, recursive_paths=None):
        self.class_names = class_names or []
        self.package_paths = package_paths or []
        self.recursive_paths = recursive_paths or False


class MockEditorAssetSubsystem:
    """Mock editor asset subsystem."""
    
    def does_asset_exist(self, asset_path: str) -> bool:
        """Check if mock asset exists."""
        # Simulate some existing blueprints
        existing = [
            "/Game/Blueprints/BP_Player",
            "/Game/Blueprints/BP_Enemy",
            "/Game/Core/BP_GameMode"
        ]
        return asset_path in existing
    
    def find_asset_data(self, asset_path: str) -> MockAssetData:
        """Find mock asset data."""
        if "/BP_Player" in asset_path:
            return MockAssetData("BP_Player", "Blueprint", asset_path)
        elif "/BP_Enemy" in asset_path:
            return MockAssetData("BP_Enemy", "Blueprint", asset_path)
        return MockAssetData("UnknownAsset", "Blueprint", asset_path)


class MockEditorLevelLibrary:
    """Mock editor level library."""
    
    @staticmethod
    def get_all_level_actors() -> List[Any]:
        """Return mock actor list."""
        class MockActor:
            def __init__(self, name, actor_class):
                self.name = name
                self.actor_class = actor_class
            
            def get_fname(self):
                return self.name
            
            def get_class(self):
                actor_cls = self.actor_class
                class MockClass:
                    def get_name(self):
                        return actor_cls
                return MockClass()
            
            def get_root_component(self):
                class MockComponent:
                    def get_component_transform(self):
                        class MockTransform:
                            class MockVector:
                                x, y, z = 0.0, 0.0, 0.0
                            translation = MockVector()
                        return MockTransform()
                return MockComponent()
        
        return [
            MockActor("PlayerStart", "PlayerStart"),
            MockActor("DirectionalLight", "DirectionalLight"),
            MockActor("SkyAtmosphere", "SkyAtmosphere"),
        ]
    
    @staticmethod
    def get_selected_level_actors() -> List[Any]:
        """Return mock selected actors."""
        return []


class MockSystemLibrary:
    """Mock system library."""
    
    @staticmethod
    def get_engine_version() -> str:
        """Return mock engine version."""
        return "5.6.0-mock"


class MockAutomationLibrary:
    """Mock automation library for screenshots."""
    
    @staticmethod
    def take_high_res_screenshot(width: int, height: int, filename: str) -> None:
        """Mock screenshot capture."""
        print(f"[MOCK] Capturing screenshot {width}x{height} -> {filename}")


# Mock subsystem getters
def get_editor_subsystem(subsystem_class: Any) -> Any:
    """Return mock editor subsystem."""
    if subsystem_class == MockEditorAssetSubsystem or str(subsystem_class) == "EditorAssetSubsystem":
        return MockEditorAssetSubsystem()
    raise ValueError(f"Unknown subsystem: {subsystem_class}")


def log_warning(message: str) -> None:
    """Mock log warning."""
    print(f"[MOCK WARNING] {message}")


def log(message: str) -> None:
    """Mock log."""
    print(f"[MOCK LOG] {message}")


# Export mock classes and functions
Paths = MockPaths
AssetRegistryHelpers = MockAssetRegistryHelpers
ARFilter = MockARFilter
EditorAssetSubsystem = MockEditorAssetSubsystem
EditorLevelLibrary = MockEditorLevelLibrary
SystemLibrary = MockSystemLibrary
AutomationLibrary = MockAutomationLibrary
