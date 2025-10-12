#!/usr/bin/env python3
"""
Architecture boundary check: Ensures backend doesn't import UE5 client code.
Verifies that main.py and app/ modules never import from attached_assets/.
"""

import ast
import sys
from pathlib import Path


def check_file_imports(filepath: Path) -> list[str]:
    """Check if a Python file imports from attached_assets."""
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    forbidden = (
                        'attached_assets' in alias.name or
                        'AIAssistant' in alias.name
                    )
                    if forbidden:
                        violations.append(
                            f"{filepath}:{node.lineno} - "
                            f"imports {alias.name}"
                        )
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    forbidden = (
                        'attached_assets' in node.module or
                        'AIAssistant' in node.module
                    )
                    if forbidden:
                        violations.append(
                            f"{filepath}:{node.lineno} - "
                            f"imports from {node.module}"
                        )
    
    except Exception as e:
        print(f"Warning: Could not parse {filepath}: {e}")
    
    return violations


def main():
    """Check all backend files for improper imports."""
    backend_files = []
    
    # Collect all Python files in backend
    backend_files.extend(Path('.').glob('main.py'))
    backend_files.extend(Path('app').rglob('*.py'))
    
    all_violations = []
    
    for filepath in backend_files:
        violations = check_file_imports(filepath)
        all_violations.extend(violations)
    
    if all_violations:
        print("❌ Architecture boundary violation detected!")
        print("\nBackend code should NOT import from attached_assets/:\n")
        for violation in all_violations:
            print(f"  {violation}")
        print("\n⚠️  Backend and UE5 client must communicate via HTTP API only.")
        sys.exit(1)
    else:
        print("✅ Architecture boundary check passed")
        print("   Backend is properly isolated from UE5 client code")
        sys.exit(0)


if __name__ == '__main__':
    main()
