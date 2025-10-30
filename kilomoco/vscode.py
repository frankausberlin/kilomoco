"""VS Code integration helpers.

Implements the temporary user data directory strategy for applying kilo extension mode configurations.
"""
import tempfile
import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import shutil

def create_temporary_user_data_dir(prefix: str = "kilomoco-profile-") -> str:
    """Create and return a temporary directory path for VS Code user-data-dir."""
    return tempfile.mkdtemp(prefix=prefix)

def generate_mode_settings(profile) -> Dict[str, Any]:
    """Generate VS Code settings dict for the given profile.

    Based on architect research, kilo extension uses 'kilo-code.*' settings keys.
    """
    settings = {
        "kilo-code.mode": profile.name,
    }
    if profile.model:
        settings["kilo-code.model"] = profile.model
    if profile.prompt:
        settings["kilo-code.prompt"] = profile.prompt
    # Merge any additional settings from profile.settings
    if profile.settings:
        settings.update(profile.settings)
    return settings

def apply_mode_configuration(profile, *, strategy: str = "temp_user_data_dir", workspace: Optional[str] = None) -> str:
    """Apply the profile configuration using the specified strategy.

    Currently only supports 'temp_user_data_dir' strategy.
    Returns the path to the applied configuration (temp user data dir).
    """
    if strategy != "temp_user_data_dir":
        raise ValueError(f"Unsupported strategy: {strategy}. Only 'temp_user_data_dir' is implemented.")

    # Create temporary user data directory
    temp_dir = create_temporary_user_data_dir()
    user_dir = Path(temp_dir) / "User"
    user_dir.mkdir(parents=True, exist_ok=True)

    # Generate settings
    settings = generate_mode_settings(profile)

    # Write settings.json atomically
    settings_path = user_dir / "settings.json"
    _write_json_atomically(settings_path, settings)

    return temp_dir

def _write_json_atomically(path: Path, data: Dict[str, Any]) -> None:
    """Write JSON data to file atomically using a temporary file."""
    temp_path = path.with_suffix('.tmp')
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        temp_path.replace(path)  # Atomic move
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise

def launch_vscode_with_profile(user_data_dir: str, workspace: Optional[str] = None, extensions_dir: Optional[str] = None) -> int:
    """Launch VS Code using the provided user-data-dir and optional workspace path."""
    cmd = ["code", "--user-data-dir", user_data_dir]
    if extensions_dir:
        cmd += ["--extensions-dir", extensions_dir]
    if workspace:
        cmd.append(workspace)
    return subprocess.call(cmd)