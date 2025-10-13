import unreal
from AIAssistant.api_client import AIClient

@unreal.uclass()
class SceneEditor(unreal.EditorUtilityWidget):
    """
    SceneEditor is an Editor Utility Widget that allows users to spawn a 3D sphere
    in front of the main camera in the main viewport.
    """

    def __init__(self):
        super(SceneEditor, self).__init__()
        self.ai_client = AIClient()

    @unreal.ufunction(override=True)
    def on_construct(self):
        """
        Called when the widget is constructed. Initialize any necessary components here.
        """
        unreal.log("SceneEditor widget constructed.")

    @unreal.ufunction()
    def spawn_sphere(self):
        """
        Spawns a 3D sphere in front of the main camera in the main viewport.
        """
        try:
            # Access the main viewport
            viewport = unreal.EditorLevelLibrary.get_editor_world()
            camera = unreal.EditorLevelLibrary.get_active_viewport_camera()

            if not camera:
                unreal.log_error("No active camera found in the viewport.")
                return

            # Get camera location and rotation
            camera_location = camera.get_location()
            camera_rotation = camera.get_rotation()

            # Define the sphere's spawn location
            spawn_location = camera_location + camera_rotation.vector() * 200.0  # 200 units in front of the camera

            # Load the sphere asset
            sphere_asset_path = "/Game/Geometry/Sphere"
            sphere_asset = unreal.EditorAssetLibrary.load_asset(sphere_asset_path)

            if not sphere_asset:
                unreal.log_error(f"Failed to load asset from path: {sphere_asset_path}")
                return

            # Spawn the sphere actor in the world
            sphere_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(sphere_asset, spawn_location, camera_rotation)

            if sphere_actor:
                unreal.log(f"Spawned sphere at {spawn_location}.")
            else:
                unreal.log_error("Failed to spawn sphere actor.")

        except Exception as e:
            unreal.log_error(f"An error occurred while spawning the sphere: {str(e)}")

    @unreal.ufunction()
    def ai_integration(self):
        """
        Example function to demonstrate AI integration capabilities.
        """
        try:
            # Example AI query
            response = self.ai_client.query("Suggest a plan for scene optimization.")
            if response:
                unreal.log(f"AI Response: {response}")
            else:
                unreal.log_warning("No response from AI client.")

        except Exception as e:
            unreal.log_error(f"An error occurred during AI integration: {str(e)}")

    @unreal.ufunction()
    def modify_scene(self):
        """
        Modify the scene based on user input or AI suggestions.
        """
        # Placeholder for future implementation
        unreal.log("Modify scene function called. Implement your logic here.")

    @unreal.ufunction()
    def query_project(self):
        """
        Query project settings or assets.
        """
        # Placeholder for future implementation
        unreal.log("Query project function called. Implement your logic here.")

    @unreal.ufunction()
    def execute_plans(self):
        """
        Execute predefined plans or strategies for scene management.
        """
        # Placeholder for future implementation
        unreal.log("Execute plans function called. Implement your logic here.")