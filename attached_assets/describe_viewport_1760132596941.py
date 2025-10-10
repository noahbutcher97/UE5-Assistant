"""
===============================================================================
 Unreal Engine 5.6+ AI Viewport Assistant  |  Version 1.2  (Oct 2025)
 Author: Noah Butcher
 Description:
     Collects real-time editor viewport data and sends it to an external
     FastAPI backend for AI scene summarization and visualization.
 Compatibility:
     ✅ UE 5.6 launcher binaries (Python 3.11.8)
     ✅ Tested up to UE 5.7-Preview
===============================================================================
"""
import check_dependencies
check_dependencies.ensure_dependencies()

import json
import time
import requests
import unreal

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

API_URL = "https://ue5-assistant-noahbutcher97.replit.app/describe_viewport"
MAX_RETRIES = 3
RETRY_DELAY = 2.5  # seconds


# -----------------------------------------------------------------------------
# LOGGING HELPERS
# -----------------------------------------------------------------------------

def log_info(msg: str):
    unreal.log(f"[DescribeViewport] {msg}")
    print("[DescribeViewport]", msg)


def log_warn(msg: str):
    unreal.log_warning(f"[DescribeViewport] ⚠️ {msg}")
    print("[DescribeViewport] ⚠️", msg)


def log_error(msg: str):
    unreal.log_error(f"[DescribeViewport] ❌ {msg}")
    print("[DescribeViewport] ❌", msg)


# -----------------------------------------------------------------------------
# VIEWPORT DATA COLLECTION (UE 5.6 + SAFE)
# -----------------------------------------------------------------------------

def collect_viewport_data():
    """
    Safely collects scene-level information from the current Unreal Editor viewport
    using modern subsystem APIs, with fallbacks for legacy interfaces.
    """
    try:
        # --- Actor collection ---
        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        selected_actors = actor_subsystem.get_selected_level_actors() if actor_subsystem else []
        all_actors = actor_subsystem.get_all_level_actors() if actor_subsystem else []

        # --- World reference (compatible fallback) ---
        world = None
        if all_actors:
            world = all_actors[0].get_world()
        elif actor_subsystem:
            try:
                world = actor_subsystem.get_editor_world()
            except Exception:
                world = None

        # --- Camera transform (modern method first) ---
        camera_location = [0, 0, 0]
        camera_rotation = [0, 0, 0]

        try:
            # Newer API in 5.6+: Unreal Editor Subsystem → get_level_viewport_camera_info
            editor_subsys = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            if editor_subsys and hasattr(editor_subsys, "get_level_viewport_camera_info"):
                cam_loc, cam_rot = editor_subsys.get_level_viewport_camera_info()
                camera_location = [cam_loc.x, cam_loc.y, cam_loc.z]
                camera_rotation = [cam_rot.pitch, cam_rot.yaw, cam_rot.roll]
            else:
                # Fallback: legacy EditorLevelLibrary
                cam_loc, cam_rot = unreal.EditorLevelLibrary.get_level_viewport_camera_info()
                camera_location = [cam_loc.x, cam_loc.y, cam_loc.z]
                camera_rotation = [cam_rot.pitch, cam_rot.yaw, cam_rot.roll]
        except Exception as e:
            log_warn(f"Could not read viewport camera info: {e}")

        # --- Construct payload ---
        data = {
            "camera_location": camera_location,
            "camera_rotation": camera_rotation,
            "visible_actors": [a.get_name() for a in all_actors[:100]],  # limit for brevity
            "selected_actor": selected_actors[0].get_name() if selected_actors else None,
            "additional_info": {
                "total_actors": len(all_actors),
                "selected_count": len(selected_actors),
                "level_name": world.get_name() if world else "Unknown",
            },
        }

        log_info("Viewport description complete.")
        return data

    except Exception as e:
        log_warn(f"Error collecting viewport data: {e}")
        return {}


# -----------------------------------------------------------------------------
# API COMMUNICATION
# -----------------------------------------------------------------------------

def send_to_api(data):
    """Send viewport data to the FastAPI backend and print the AI summary."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(API_URL, json=data, timeout=20)
            if response.status_code == 200:
                try:
                    result = response.json()
                    desc = result.get("description", "<no description>")
                    raw = result.get("raw_context", {})
                    log_info("✅ AI Description Received:")
                    log_info(f"   {desc}")
                    log_info(f"   (Actors: {len(raw.get('visible_actors', []))}, "
                             f"Level: {raw.get('additional_info', {}).get('level_name', 'Unknown')})")
                    return True
                except json.JSONDecodeError:
                    log_warn("Invalid JSON response from server.")
                    return False
            else:
                log_warn(f"Server returned status {response.status_code}: {response.text}")
                return False

        except requests.RequestException as e:
            log_error(f"Request failed (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                log_info("Retrying...")
            else:
                log_error("Exhausted all retries.")
                return False


# -----------------------------------------------------------------------------
# MAIN ENTRY POINT
# -----------------------------------------------------------------------------

def send_viewport_description():
    """Main function: collect viewport data and send to API."""
    log_info("Collecting viewport data...")
    payload = collect_viewport_data()
    if not payload:
        log_error("Failed to collect viewport data. Aborting.")
        return
    log_info(f"Sending data to API ({API_URL})...")
    send_to_api(payload)


# -----------------------------------------------------------------------------
# MANUAL EXECUTION (TEST ENTRY)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    log_info("UE 5.6 + Safe Edition | DescribeViewport v1.2 starting…")
    send_viewport_description()
