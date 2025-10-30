"""Launcher helpers for starting VS Code with modified configuration."""
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .config import default_profiles, ModeProfile
from .vscode import apply_mode_configuration, launch_vscode_with_profile

def check_vscode_available() -> bool:
    """Check if VS Code CLI is available in PATH."""
    return shutil.which("code") is not None

def prepare_and_launch(profile_name: str, workspace: Optional[str] = None) -> int:
    """Apply the specified profile configuration and launch VS Code.

    Args:
        profile_name: Name of the mode profile to apply
        workspace: Optional path to workspace directory

    Returns:
        Exit code from VS Code process

    Raises:
        ValueError: If profile_name is not found in default profiles
        RuntimeError: If VS Code CLI is not available
    """
    # Check VS Code availability
    if not check_vscode_available():
        raise RuntimeError("VS Code CLI ('code') not found in PATH. Please ensure VS Code is installed and 'code' command is available.")

    # Get profile
    profiles = default_profiles()
    if profile_name not in profiles:
        available = ", ".join(sorted(profiles.keys()))
        raise ValueError(f"Profile '{profile_name}' not found. Available profiles: {available}")

    profile = profiles[profile_name]

    # Apply configuration
    temp_dir = apply_mode_configuration(profile)

    try:
        # Launch VS Code
        return launch_vscode_with_profile(temp_dir, workspace=workspace)
    except Exception:
        # Cleanup temp directory on error
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass  # Ignore cleanup errors
        raise