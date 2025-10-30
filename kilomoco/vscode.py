"""VS Code integration helpers (scaffold).

This module should contain the functions defined in the architect research:
- create_temporary_user_data_dir()
- generate_mode_settings()
- apply_mode_configuration()
- launch_vscode_with_profile()

For this sprint create function signatures and minimal implementations or
raise NotImplementedError where appropriate so later sprints can implement them.
"""
import tempfile
from typing import Optional
import subprocess
import os
import json

def create_temporary_user_data_dir(prefix: str = "kilomoco-profile-") -> str:
    """Create and return a temporary directory path for VS Code user-data-dir."""
    return tempfile.mkdtemp(prefix=prefix)

def generate_mode_settings(profile) -> dict:
    """Return a dict that can be written to a User/settings.json for a given profile."""
    # Placeholder: return settings mapping if present
    return profile.settings or {}

def apply_mode_configuration(profile, *, strategy: str = "temp_user_data_dir", workspace: Optional[str] = None) -> str:
    """Apply the profile according to the chosen strategy and return a handle (path) describing the applied state.

    This is intentionally left unimplemented for the next sprint.
    """
    raise NotImplementedError("apply_mode_configuration must be implemented in a later sprint.")

def launch_vscode_with_profile(user_data_dir: str, workspace: Optional[str] = None, extensions_dir: Optional[str] = None) -> int:
    """Launch VS Code using the provided user-data-dir and optional workspace path."""
    cmd = ["code", "--user-data-dir", user_data_dir]
    if extensions_dir:
        cmd += ["--extensions-dir", extensions_dir]
    if workspace:
        cmd.append(workspace)
    return subprocess.call(cmd)