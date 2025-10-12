"""
Shared Mock Viewport Data for Testing
Provides realistic viewport contexts based on the mock TestProject.
"""

def get_mock_viewport_context():
    """Get a realistic mock viewport context with camera, actors, lighting."""
    return {
        "camera": {
            "location": [1200.5, -850.0, 450.25],
            "rotation": [-15.0, 90.0, 0.0],
            "fov": 90.0
        },
        "actors": {
            "total": 8,
            "names": [
                "PlayerStart",
                "DirectionalLight_0",
                "SkyAtmosphere_0",
                "BP_Player_2",
                "BP_Enemy_3",
                "StaticMeshActor_4",
                "PointLight_5",
                "Cube_6"
            ],
            "types": {
                "PlayerStart": 1,
                "DirectionalLight": 1,
                "SkyAtmosphere": 1,
                "Blueprint": 2,
                "StaticMeshActor": 1,
                "PointLight": 1,
                "Cube": 1
            },
            "level": "Persistent Level"
        },
        "lighting": {
            "directional_lights": [
                {
                    "name": "DirectionalLight_0",
                    "intensity": 3.14159,
                    "color": [255, 248, 220],
                    "rotation": [-45.0, 0.0, 0.0],
                    "cast_shadows": True
                }
            ],
            "point_lights": [
                {
                    "name": "PointLight_5",
                    "intensity": 5000.0,
                    "color": [255, 200, 150],
                    "location": [500.0, 0.0, 200.0],
                    "radius": 2000.0
                }
            ],
            "sky_lights": [],
            "total_count": 2
        },
        "environment": {
            "sky_atmosphere": {
                "enabled": True,
                "name": "SkyAtmosphere_0"
            },
            "fog": {
                "enabled": False
            },
            "post_process": {
                "auto_exposure": True,
                "bloom": True
            }
        },
        "selection": {
            "count": 1,
            "actor_name": "BP_Player_2",
            "actor_type": "Blueprint",
            "location": [0.0, 0.0, 88.0]
        },
        "project_metadata": {
            "project_name": "TestProject",
            "engine_version": "5.6.0",
            "modules": ["TestProject", "TestProjectEditor"],
            "plugins": ["PythonScriptPlugin", "EditorScriptingUtilities", "EnhancedInput"],
            "content_stats": {
                "total_assets": 5,
                "blueprints": 3,
                "textures": 1,
                "materials": 1,
                "meshes": 1
            }
        }
    }


def get_minimal_viewport_context():
    """Get minimal viewport context for concise style testing."""
    return {
        "camera": {
            "location": [0.0, 0.0, 500.0],
            "rotation": [-30.0, 0.0, 0.0]
        },
        "actors": {
            "total": 3,
            "names": ["PlayerStart", "DirectionalLight_0", "Cube_1"],
            "level": "TestLevel"
        },
        "selection": {
            "count": 1,
            "actor_name": "Cube_1"
        }
    }


def get_complex_viewport_context():
    """Get complex viewport context for detailed/technical style testing."""
    return {
        "camera": {
            "location": [2500.75, -1800.5, 750.0],
            "rotation": [-20.5, 135.0, 0.0],
            "fov": 75.0
        },
        "actors": {
            "total": 15,
            "names": [
                "PlayerStart", "DirectionalLight_0", "SkyAtmosphere_0",
                "BP_Player_2", "BP_Enemy_3", "BP_Enemy_4", "BP_Enemy_5",
                "StaticMeshActor_6", "StaticMeshActor_7", "StaticMeshActor_8",
                "PointLight_9", "PointLight_10", "SpotLight_11",
                "Cube_12", "Sphere_13"
            ],
            "types": {
                "PlayerStart": 1,
                "DirectionalLight": 1,
                "SkyAtmosphere": 1,
                "Blueprint": 4,
                "StaticMeshActor": 3,
                "PointLight": 2,
                "SpotLight": 1,
                "Cube": 1,
                "Sphere": 1
            },
            "level": "MainLevel"
        },
        "lighting": {
            "directional_lights": [
                {
                    "name": "DirectionalLight_0",
                    "intensity": 10.0,
                    "color": [255, 248, 220],
                    "rotation": [-60.0, 45.0, 0.0],
                    "cast_shadows": True
                }
            ],
            "point_lights": [
                {
                    "name": "PointLight_9",
                    "intensity": 8000.0,
                    "color": [255, 100, 50],
                    "location": [1000.0, -500.0, 300.0],
                    "radius": 3000.0
                },
                {
                    "name": "PointLight_10",
                    "intensity": 5000.0,
                    "color": [100, 150, 255],
                    "location": [-800.0, 600.0, 250.0],
                    "radius": 2500.0
                }
            ],
            "spot_lights": [
                {
                    "name": "SpotLight_11",
                    "intensity": 15000.0,
                    "color": [255, 255, 255],
                    "location": [0.0, 0.0, 800.0],
                    "inner_cone_angle": 20.0,
                    "outer_cone_angle": 45.0
                }
            ],
            "total_count": 4
        },
        "environment": {
            "sky_atmosphere": {
                "enabled": True,
                "name": "SkyAtmosphere_0"
            },
            "fog": {
                "enabled": True,
                "density": 0.02,
                "height_falloff": 0.2
            },
            "post_process": {
                "auto_exposure": True,
                "bloom": True,
                "ambient_occlusion": True,
                "motion_blur": False
            }
        },
        "selection": {
            "count": 3,
            "actors": ["BP_Enemy_3", "BP_Enemy_4", "BP_Enemy_5"]
        }
    }


def get_mock_project_profile():
    """Get mock project profile data."""
    return {
        "project_name": "TestProject",
        "project_path": "/path/to/TestProject",
        "engine_version": "5.6.0",
        "modules": ["TestProject", "TestProjectEditor"],
        "plugins": [
            "PythonScriptPlugin",
            "EditorScriptingUtilities", 
            "EnhancedInput"
        ],
        "content_stats": {
            "total_assets": 5,
            "blueprints": 3,
            "textures": 1,
            "materials": 1,
            "skeletal_meshes": 1,
            "sounds": 1
        },
        "source_stats": {
            "total_files": 8,
            "cpp_files": 4,
            "header_files": 4
        }
    }


def get_mock_blueprint_list():
    """Get mock blueprint list."""
    return [
        {
            "name": "BP_Player",
            "path": "/Game/Blueprints/BP_Player",
            "class": "Blueprint",
            "parent_class": "Character"
        },
        {
            "name": "BP_Enemy",
            "path": "/Game/Blueprints/BP_Enemy",
            "class": "Blueprint",
            "parent_class": "Pawn"
        },
        {
            "name": "BP_GameMode",
            "path": "/Game/Core/BP_GameMode",
            "class": "Blueprint",
            "parent_class": "GameModeBase"
        }
    ]


def get_mock_file_context():
    """Get mock file browsing context."""
    return {
        "root_path": "/Game/TestProject/Content",
        "total_files": 12,
        "total_size": 2048576,
        "files": [
            {
                "path": "/Game/Blueprints/BP_Player.uasset",
                "size": 256000,
                "type": "Blueprint"
            },
            {
                "path": "/Game/Blueprints/BP_Enemy.uasset",
                "size": 128000,
                "type": "Blueprint"
            },
            {
                "path": "/Game/Textures/T_Ground.uasset",
                "size": 512000,
                "type": "Texture2D"
            },
            {
                "path": "/Game/Materials/M_Character.uasset",
                "size": 64000,
                "type": "Material"
            }
        ],
        "search_query": None
    }
