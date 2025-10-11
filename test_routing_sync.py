#!/usr/bin/env python3
"""Test that backend routing tokens match UE5 registered actions."""

import json
import re
from pathlib import Path

# Extract backend tokens
backend_file = Path("app/routes.py")
backend_content = backend_file.read_text()
backend_tokens = set(re.findall(r'\[UE_REQUEST\] (\w+)', backend_content))

# Extract UE5 actions
ue5_file = Path("attached_assets/AIAssistant/action_executor.py")
ue5_content = ue5_file.read_text()
ue5_actions = set(re.findall(r'self\.register\("(\w+)"', ue5_content))

print("=" * 60)
print("BACKEND ↔ UE5 SYNCHRONIZATION TEST")
print("=" * 60)

print("\n✅ Backend sends these tokens:")
for token in sorted(backend_tokens):
    status = "✓" if token in ue5_actions else "✗ MISSING"
    print(f"  {status} {token}")

print("\n✅ UE5 has these actions registered:")
for action in sorted(ue5_actions):
    is_backend = "← sent by backend" if action in backend_tokens else ""
    print(f"  ✓ {action} {is_backend}")

# Check for mismatches
missing_in_ue5 = backend_tokens - ue5_actions
extra_in_ue5 = ue5_actions - backend_tokens

print("\n" + "=" * 60)
if not missing_in_ue5:
    print("✅ ALL BACKEND TOKENS ARE REGISTERED IN UE5")
else:
    print(f"❌ MISSING IN UE5: {missing_in_ue5}")

print("\nℹ️  Extra actions in UE5 (internal use):")
for action in sorted(extra_in_ue5):
    print(f"  • {action}")

print("=" * 60)
print("\n✅ SYNCHRONIZATION: PASS" if not missing_in_ue5 else "\n❌ SYNCHRONIZATION: FAIL")
