"""Smart data filtering for viewport context based on response styles."""
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from app.models import ViewportContext


def filter_viewport_data(
    context: 'ViewportContext', filter_mode: str
) -> Dict[str, Any]:
    """
    Intelligently filter viewport data based on response style.
    Returns a filtered dict optimized for the requested level of detail.
    """
    filtered = {}
    
    # Camera is always included (spatial context is essential)
    filtered["camera"] = {
        "location": (
            context.camera.get("location", [0, 0, 0])
            if context.camera
            else [0, 0, 0]
        ),
        "rotation": (
            context.camera.get("rotation", [0, 0, 0])
            if context.camera
            else [0, 0, 0]
        )
    }
    
    actors_data = context.actors or {}
    selection_data = context.selection or {}
    lighting_data = context.lighting or {}
    environment_data = context.environment or {}
    
    if filter_mode == "minimal":  # Concise: Only camera + selected
        selected_actors = selection_data.get("actors", [])
        filtered["selection"] = {
            "count": len(selected_actors),
            "actors": (
                selected_actors[:3]
                if len(selected_actors) > 3
                else selected_actors
            )
        }
        filtered["actors_summary"] = {
            "total": actors_data.get("total", 0),
            "has_more": actors_data.get("total", 0) > len(selected_actors)
        }
    
    elif filter_mode == "highlights":  # Natural: Interesting elements only
        selected_actors = selection_data.get("actors", [])
        filtered["selection"] = selection_data
        all_names = actors_data.get("names", [])
        filtered["actors"] = {
            "total": actors_data.get("total", 0),
            "notable": (
                selected_actors + all_names[:5]
                if all_names
                else selected_actors
            ),
            "types_summary": actors_data.get("types", {})
        }
        if lighting_data.get("directional_lights") or lighting_data.get("point_lights"):
            filtered["lighting_summary"] = "present"
    
    elif filter_mode == "balanced":  # Balanced: Selected + summaries
        filtered["selection"] = selection_data
        filtered["actors"] = {
            "total": actors_data.get("total", 0),
            "types": actors_data.get("types", {}),
            "sample_names": actors_data.get("names", [])[:10]
        }
        filtered["lighting"] = {
            "directional_count": len(lighting_data.get("directional_lights", [])),
            "point_count": len(lighting_data.get("point_lights", [])),
            "spot_count": len(lighting_data.get("spot_lights", []))
        }
        if environment_data.get("fog") or environment_data.get("landscape"):
            filtered["environment"] = {
                "has_fog": bool(environment_data.get("fog")),
                "has_landscape": bool(environment_data.get("landscape"))
            }
    
    elif filter_mode == "standard":
        # Descriptive/Creative: Good detail without overwhelming
        filtered["selection"] = selection_data
        filtered["actors"] = {
            "total": actors_data.get("total", 0),
            "names": actors_data.get("names", [])[:15],
            "types": actors_data.get("types", {})
        }
        filtered["lighting"] = lighting_data
        filtered["environment"] = {
            "fog": environment_data.get("fog", {}),
            "landscape": environment_data.get("landscape", {})
        }
    
    elif filter_mode == "technical":  # Technical: Detailed but organized
        filtered["selection"] = selection_data
        filtered["actors"] = actors_data
        filtered["lighting"] = lighting_data
        filtered["environment"] = environment_data
        filtered["metadata"] = {
            "actor_count": actors_data.get("total", 0),
            "selected_count": selection_data.get("count", 0),
            "lighting_count": (
                len(lighting_data.get("directional_lights", [])) +
                len(lighting_data.get("point_lights", [])) +
                len(lighting_data.get("spot_lights", []))
            )
        }
    
    elif filter_mode == "complete":  # Detailed: Everything
        filtered["camera"] = context.camera
        filtered["actors"] = actors_data
        filtered["selection"] = selection_data
        filtered["lighting"] = lighting_data
        filtered["environment"] = environment_data
        if context.additional_info:
            filtered["additional_info"] = context.additional_info
    
    else:  # Fallback to standard
        return filter_viewport_data(context, "standard")
    
    return filtered
