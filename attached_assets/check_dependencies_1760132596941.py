"""
===============================================================================
 Unreal Engine Python Dependency Checker  |  Version 1.0  (Oct 2025)
 Author: Noah Butcher
 Description:
     Ensures required Python packages (like 'requests') are installed
     in Unreal Engine's embedded Python environment automatically.
===============================================================================
"""

import importlib
import subprocess
import sys

import unreal  # type: ignore

REQUIRED_PACKAGES = ["requests"]


def log(msg):
    unreal.log("[CheckDependencies] " + str(msg))
    print("[CheckDependencies]", msg)


def install_package(pkg_name):
    """
    Installs a Python package using pip from within the Unreal embedded interpreter.
    """
    python_exe = sys.executable
    try:
        log(f"Installing missing dependency: {pkg_name} ...")
        result = subprocess.run(
            [python_exe, "-m", "pip", "install", pkg_name],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            log(f"✅ Successfully installed: {pkg_name}")
        else:
            log(f"❌ Failed to install {pkg_name}:\n{result.stderr}")

    except Exception as e:
        log(f"⚠️ Error installing {pkg_name}: {e}")


def ensure_dependencies():
    """
    Verifies required modules and installs them if missing.
    """
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            log(f"✅ Dependency already satisfied: {pkg}")
        except ImportError:
            install_package(pkg)


if __name__ == "__main__":
    log("Running dependency check...")
    ensure_dependencies()
    log("Dependency check complete.")
