"""
Enhanced context collection for UE5 scenes.
Gathers viewport, lighting, materials, and environmental data.
"""
from typing import Any, Dict, Optional

try:
    import unreal  # type: ignore
    HAS_UNREAL = True
except ImportError:
    HAS_UNREAL = False

from .utils import Logger


class ContextCollector:
    """Collects comprehensive scene context for AI analysis."""

    def __init__(self):
        self.logger = Logger("ContextCollector", verbose=False)

    def collect_viewport_data(self) -> Dict[str, Any]:
        """
        Collect comprehensive viewport and scene data.
        Includes camera, actors, lighting, materials, and environment.
        """
        if not HAS_UNREAL:
            self.logger.error("Unreal module not available")
            return {}

        try:
            data = {
                "camera": self._collect_camera_data(),
                "actors": self._collect_actor_data(),
                "lighting": self._collect_lighting_data(),
                "environment": self._collect_environment_data(),
                "selection": self._collect_selection_data(),
            }

            self.logger.success("Context collection complete")
            return data

        except Exception as e:
            self.logger.error(f"Context collection failed: {e}")
            return {}

    def _collect_camera_data(self) -> Dict[str, Any]:
        """Collect camera position and rotation."""
        try:
            editor_subsys = unreal.get_editor_subsystem(
                unreal.UnrealEditorSubsystem
            )

            has_method = hasattr(
                editor_subsys, "get_level_viewport_camera_info"
            )

            if editor_subsys and has_method:
                cam_loc, cam_rot = (
                    editor_subsys.get_level_viewport_camera_info()
                )
            else:
                cam_loc, cam_rot = (
                    unreal.EditorLevelLibrary
                    .get_level_viewport_camera_info()
                )

            return {
                "location": [cam_loc.x, cam_loc.y, cam_loc.z],
                "rotation": [
                    cam_rot.pitch,
                    cam_rot.yaw,
                    cam_rot.roll,
                ],
            }
        except Exception as e:
            self.logger.warn(f"Camera data unavailable: {e}")
            return {"location": [0, 0, 0], "rotation": [0, 0, 0]}

    def _collect_actor_data(self) -> Dict[str, Any]:
        """Collect actor list with types and counts."""
        try:
            actor_subsys = unreal.get_editor_subsystem(
                unreal.EditorActorSubsystem
            )

            all_actors = actor_subsys.get_all_level_actors() if actor_subsys else []

            # Get world for level name
            world = None
            if all_actors:
                world = all_actors[0].get_world()

            # Categorize actors by type
            actor_types: Dict[str, int] = {}
            actor_names = []

            for actor in all_actors[:100]:  # Limit for performance
                actor_name = actor.get_name()
                actor_class = (
                    actor.get_class().get_name()
                    if actor.get_class()
                    else "Unknown"
                )

                actor_names.append(actor_name)

                if actor_class in actor_types:
                    actor_types[actor_class] += 1
                else:
                    actor_types[actor_class] = 1

            return {
                "total": len(all_actors),
                "names": actor_names,
                "types": actor_types,
                "level": world.get_name() if world else "Unknown",
            }
        except Exception as e:
            self.logger.warn(f"Actor data unavailable: {e}")
            return {"total": 0, "names": [], "types": {}}

    def _collect_lighting_data(self) -> Dict[str, Any]:
        """Collect lighting setup information."""
        try:
            actor_subsys = unreal.get_editor_subsystem(
                unreal.EditorActorSubsystem
            )

            if not actor_subsys:
                return {}

            all_actors = actor_subsys.get_all_level_actors()
            lighting_data = {
                "directional_lights": [],
                "point_lights": [],
                "spot_lights": [],
                "sky_atmosphere": None,
            }

            for actor in all_actors:
                actor_class = (
                    actor.get_class().get_name()
                    if actor.get_class()
                    else ""
                )

                # Directional lights
                if "DirectionalLight" in actor_class:
                    light_data = self._extract_light_info(actor)
                    if light_data:
                        lighting_data["directional_lights"].append(
                            light_data
                        )

                # Point lights
                elif "PointLight" in actor_class:
                    light_data = self._extract_light_info(actor)
                    if light_data:
                        lighting_data["point_lights"].append(
                            light_data
                        )

                # Spot lights
                elif "SpotLight" in actor_class:
                    light_data = self._extract_light_info(actor)
                    if light_data:
                        lighting_data["spot_lights"].append(light_data)

                # Sky atmosphere
                elif "SkyAtmosphere" in actor_class:
                    lighting_data["sky_atmosphere"] = actor.get_name()

            return lighting_data
        except Exception as e:
            self.logger.warn(f"Lighting data unavailable: {e}")
            return {}

    def _extract_light_info(
        self, actor: Any
    ) -> Optional[Dict[str, Any]]:
        """Extract info from a light actor."""
        try:
            light_comp = actor.get_component_by_class(
                unreal.LightComponent
            )

            if not light_comp:
                return None

            # Get transform
            transform = actor.get_actor_transform()
            location = transform.translation
            rotation = transform.rotation.rotator()

            return {
                "name": actor.get_name(),
                "location": [location.x, location.y, location.z],
                "rotation": [
                    rotation.pitch,
                    rotation.yaw,
                    rotation.roll,
                ],
                "intensity": getattr(
                    light_comp, "intensity", "unknown"
                ),
            }
        except Exception:
            return None

    def _collect_environment_data(self) -> Dict[str, Any]:
        """Collect environmental elements (fog, PP volumes, etc.)."""
        try:
            actor_subsys = unreal.get_editor_subsystem(
                unreal.EditorActorSubsystem
            )

            if not actor_subsys:
                return {}

            all_actors = actor_subsys.get_all_level_actors()
            env_data = {
                "fog": [],
                "post_process_volumes": [],
                "landscape": None,
            }

            for actor in all_actors:
                actor_class = (
                    actor.get_class().get_name()
                    if actor.get_class()
                    else ""
                )

                if "Fog" in actor_class:
                    env_data["fog"].append(actor.get_name())
                elif "PostProcessVolume" in actor_class:
                    env_data["post_process_volumes"].append(
                        actor.get_name()
                    )
                elif "Landscape" in actor_class:
                    env_data["landscape"] = actor.get_name()

            return env_data
        except Exception as e:
            self.logger.warn(f"Environment data unavailable: {e}")
            return {}

    def _collect_selection_data(self) -> Dict[str, Any]:
        """Collect selected actor information with materials."""
        try:
            actor_subsys = unreal.get_editor_subsystem(
                unreal.EditorActorSubsystem
            )

            if not actor_subsys:
                return {}

            selected = actor_subsys.get_selected_level_actors()

            if not selected:
                return {"count": 0, "actors": []}

            selection_data = {"count": len(selected), "actors": []}

            for actor in selected[:10]:  # Limit to 10 for performance
                actor_info = {
                    "name": actor.get_name(),
                    "class": (
                        actor.get_class().get_name()
                        if actor.get_class()
                        else "Unknown"
                    ),
                    "location": None,
                    "materials": [],
                }

                # Get location
                try:
                    transform = actor.get_actor_transform()
                    loc = transform.translation
                    actor_info["location"] = [loc.x, loc.y, loc.z]
                except Exception:
                    pass

                # Get materials (if it has a static mesh component)
                try:
                    mesh_comp = actor.get_component_by_class(
                        unreal.StaticMeshComponent
                    )
                    if mesh_comp:
                        num_materials = mesh_comp.get_num_materials()
                        for i in range(num_materials):
                            mat = mesh_comp.get_material(i)
                            if mat:
                                mat_name = mat.get_name()
                                actor_info["materials"].append(
                                    mat_name
                                )
                except Exception:
                    pass

                selection_data["actors"].append(actor_info)

            return selection_data
        except Exception as e:
            self.logger.warn(f"Selection data unavailable: {e}")
            return {"count": 0, "actors": []}


# Global collector instance
_collector: Optional[ContextCollector] = None


def get_collector() -> ContextCollector:
    """Get or create the global context collector."""
    global _collector
    if _collector is None:
        _collector = ContextCollector()
    return _collector
