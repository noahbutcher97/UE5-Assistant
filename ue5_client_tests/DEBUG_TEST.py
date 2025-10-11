"""
Debug script to test context collection directly.
Run this in Unreal Engine's Python console to see what's being collected.
"""

from AIAssistant.context_collector import get_collector  # type: ignore

# Enable verbose logging
collector = get_collector()
collector.logger.verbose = True

print("\n=== DEBUG: Testing Context Collection ===\n")

# Test camera data
print("1. Testing camera collection...")
camera_data = collector._collect_camera_data()
print(f"Camera data: {camera_data}\n")

# Test actor data
print("2. Testing actor collection...")
actor_data = collector._collect_actor_data()
print(f"Actor count: {actor_data.get('total', 0)}")
print(f"Actor types: {actor_data.get('types', {})}\n")

# Test lighting data
print("3. Testing lighting collection...")
lighting_data = collector._collect_lighting_data()
print(f"Lighting data: {lighting_data}\n")

# Test full collection
print("4. Testing full viewport collection...")
full_data = collector.collect_viewport_data()
print(f"Full context keys: {list(full_data.keys())}")
print(f"Full context: {full_data}\n")

print("=== DEBUG COMPLETE ===")
print("\nIf you see empty/null values above, there's an issue with UE API access.")
print("Expected: Camera location, actor counts, lighting info")
