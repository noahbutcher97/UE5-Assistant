import unreal
from AIAssistant.api_client import AIClient

@unreal.uclass()
class SceneEditor(unreal.EditorUtilityWidget):
    """
    SceneEditor is an Editor Utility Widget that spawns a 3D sphere in the viewport
    in front of the camera on the ground plane when a button is pressed.
    """

    def __init__(self):
        super().__init__()
        self.ai_client = AIClient()

    @unreal.ufunction(override=True)
    def on_button_press(self):
        """
        Called when the button is pressed. This function will spawn a sphere
        in front of the camera on the ground plane.
        """
        try:
            # Access the current editor viewport
            viewport = unreal.EditorLevelLibrary.get_editor_viewport()
            if not viewport:
                unreal.log_error("No active viewport found.")
                return

            # Get the camera location and rotation
            camera_location = viewport.get_camera_location()
            camera_rotation = viewport.get_camera_rotation()

            # Calculate spawn location in front of the camera
            spawn_location = camera_location + camera_rotation.vector() * 200.0
            spawn_location.z = 0  # Ensure it's on the ground plane

            # Spawn the sphere asset
            sphere_asset = self.spawn_sphere(spawn_location)

            # Log success
            if sphere_asset:
                unreal.log("Sphere spawned successfully at location: {}".format(spawn_location))
            else:
                unreal.log_error("Failed to spawn sphere.")

        except Exception as e:
            unreal.log_error("An error occurred: {}".format(str(e)))

    def spawn_sphere(self, location):
        """
        Spawns a 3D sphere at the specified location.

        Args:
            location (unreal.Vector): The location to spawn the sphere.

        Returns:
            unreal.Actor: The spawned sphere actor or None if failed.
        """
        try:
            # Load the sphere static mesh asset
            sphere_mesh = unreal.EditorAssetLibrary.load_asset("/Game/Path/To/SphereMesh")
            if not sphere_mesh:
                unreal.log_error("Sphere mesh asset not found.")
                return None

            # Spawn the sphere actor in the world
            sphere_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(sphere_mesh, location, unreal.Rotator(0, 0, 0))
            return sphere_actor

        except Exception as e:
            unreal.log_error("Failed to spawn sphere: {}".format(str(e)))
            return None

    @unreal.ufunction(override=True)
    def on_ai_request(self, prompt):
        """
        Sends a prompt to the AI client and logs the response.

        Args:
            prompt (str): The prompt to send to the AI.
        """
        try:
            response = self.ai_client.send_request(prompt)
            unreal.log("AI Response: {}".format(response))
        except Exception as e:
            unreal.log_error("AI request failed: {}".format(str(e)))