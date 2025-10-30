"""VS Code integration helpers.

Implements the temporary user data directory strategy for applying kilo extension mode configurations.
"""
import tempfile
import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
import shutil
import psutil

def create_temporary_user_data_dir(prefix: str = "kilomoco-profile-") -> str:
    """Create and return a temporary directory path for VS Code user-data-dir."""
    return tempfile.mkdtemp(prefix=prefix)

def generate_mode_settings(profile) -> Dict[str, Any]:
    """Generate VS Code settings dict for the given mode combination profile.

    Based on architect research, kilo extension uses 'kilo-code.*' settings keys.
    Sets model for each mode in the profile combination.
    """
    settings = {}
    for mode_name, model_name in profile.modes.items():
        settings[f"kilo-code.{mode_name}.model"] = model_name
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


def detect_vscode_instances() -> List[Dict[str, Any]]:
    """Detect running VS Code instances with kilo extension.

    Returns a list of dicts with keys: 'workspace' (str or None), 'user_data_dir' (str or None), 'has_kilo' (bool), 'pid' (int).
    Only includes instances with kilo extension installed.
    """
    instances = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info.get('name')
            if name in ('code', 'Code'):
                cmdline = proc.info['cmdline'] or []
                user_data_dir = None
                workspace = None

                # Parse command line args
                i = 0
                while i < len(cmdline):
                    arg = cmdline[i]
                    if arg == '--user-data-dir' and i + 1 < len(cmdline):
                        user_data_dir = cmdline[i + 1]
                        i += 1
                    elif not arg.startswith('-') and workspace is None and arg != 'code':
                        # First non-flag argument that is not 'code' is likely the workspace
                        workspace = arg
                    i += 1

                # Check if kilo extension is installed
                has_kilo = False
                if user_data_dir:
                    extensions_dir = Path(user_data_dir) / 'extensions'
                    kilo_ext_dir = extensions_dir / 'kilocode.kilo-code'
                    has_kilo = kilo_ext_dir.exists()

                if has_kilo:
                    instances.append({
                        'workspace': workspace,
                        'user_data_dir': user_data_dir,
                        'has_kilo': has_kilo,
                        'pid': proc.info['pid']
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return instances


def get_current_profile_from_instance(instance: Dict[str, Any]) -> Optional[str]:
    """Get the current profile ID from a VS Code instance.

    Reads settings.json from the instance's user-data-dir and matches kilo-code.* settings against known profiles.
    Returns profile ID if match found, else None.
    """
    user_data_dir = instance.get('user_data_dir')
    if not user_data_dir:
        return None

    settings_path = Path(user_data_dir) / 'User' / 'settings.json'
    if not settings_path.exists():
        return None

    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    # Extract kilo-code settings
    kilo_settings = {}
    for key, value in settings.items():
        if key.startswith('kilo-code.'):
            mode = key.split('.', 2)[1]  # kilo-code.{mode}.model
            if key.endswith('.model'):
                kilo_settings[mode] = value

    if not kilo_settings:
        return None

    # Import here to avoid circular imports
    from .config import default_profiles

    profiles = default_profiles()
    for profile_id, profile in profiles.items():
        if profile.modes == kilo_settings:
            return profile_id

    return None