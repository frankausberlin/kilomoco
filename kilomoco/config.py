"""Configuration model and simple persistence helpers for kilomoco."""
from dataclasses import dataclass, asdict
from typing import Dict, Optional
import json
import os
import warnings
from pathlib import Path
import yaml

@dataclass
class ModeCombinationProfile:
    id: str
    name: str
    description: str
    modes: Dict[str, str]  # mode_name -> model_name

def default_profiles() -> Dict[str, ModeCombinationProfile]:
    """Return the default mode combination profiles.

    First attempts to discover profiles from YAML files in candidate directories.
    If no YAML profiles are found, falls back to built-in profiles.
    """
    discovered = discover_profiles()
    if discovered:
        return discovered
    # Fallback to built-in profiles
    return {
        "lopr": ModeCombinationProfile(
            id="lopr",
            name="Low-Price (Economy)",
            description="Budget-friendly model combinations for cost-conscious usage",
            modes={
                "default": "llama-4-maverick",
                "orchestrator": "deepseek-v3.2-exp",
                "architect": "minimax-m2",
                "code": "minimax-m2",
                "debug": "deepseek-v3.1-terminus",
                "ask": "llama-4-maverick",
                "administrator": "deepseek-v3.2-exp"
            }
        ),
        "copr": ModeCombinationProfile(
            id="copr",
            name="Complex-Programming (Agentic Coding)",
            description="Optimized for complex programming tasks and agentic workflows",
            modes={
                "default": "gpt-5-mini",
                "orchestrator": "claude-sonnet-4.5",
                "architect": "gemini-2.5-pro",
                "code": "qwen3-coder",
                "debug": "claude-haiku-4.5",
                "ask": "glm-4.6",
                "administrator": "glm-4.6"
            }
        ),
        "hiq": ModeCombinationProfile(
            id="hiq",
            name="High-Quality (Premium)",
            description="Premium models for highest quality output",
            modes={
                "default": "gemini-2.5-pro",
                "orchestrator": "claude-sonnet-4.5",
                "architect": "gpt-5",
                "code": "claude-sonnet-4.5",
                "debug": "claude-sonnet-4.5",
                "ask": "gemini-2.5-pro",
                "administrator": "gpt-5"
            }
        ),
        "bas": ModeCombinationProfile(
            id="bas",
            name="Balanced-Speed (speed)",
            description="Balanced performance with good speed",
            modes={
                "default": "grok-code-fast-1",
                "orchestrator": "gemini-2.5-flash",
                "architect": "gpt-5-mini",
                "code": "grok-code-fast-1",
                "debug": "gemini-2.5-flash",
                "ask": "grok-code-fast-1",
                "administrator": "gemini-2.5-flash"
            }
        ),
        "res": ModeCombinationProfile(
            id="res",
            name="Repository-Scale (big codebases)",
            description="Optimized for large codebases and repository-scale tasks",
            modes={
                "default": "gemini-2.5-flash",
                "orchestrator": "gemini-2.5-pro",
                "architect": "qwen3-max",
                "code": "qwen3-coder",
                "debug": "glm-4.6",
                "ask": "llama-4-maverick",
                "administrator": "qwen3-max"
            }
        ),
        "ags": ModeCombinationProfile(
            id="ags",
            name="Agent-Specialist (Autonome Workflows)",
            description="Specialized for autonomous workflows and agent operations",
            modes={
                "default": "minimax-m2",
                "orchestrator": "claude-sonnet-4.5",
                "architect": "deepseek-v3.1-terminus",
                "code": "glm-4.6",
                "debug": "claude-haiku-4.5",
                "ask": "gpt-5-mini",
                "administrator": "deepseek-v3.1-terminus"
            }
        ),
        "refo": ModeCombinationProfile(
            id="refo",
            name="Research-Focused (analyse & science)",
            description="Optimized for research, analysis, and scientific tasks",
            modes={
                "default": "qwen3-max",
                "orchestrator": "gemini-2.5-pro",
                "architect": "gpt-5",
                "code": "mistral-large",
                "debug": "claude-sonnet-4.5",
                "ask": "gemini-2.5-flash",
                "administrator": "mistral-large"
            }
        ),
        "buco": ModeCombinationProfile(
            id="buco",
            name="Budget-Conscious-Pro (budget and efficiency)",
            description="Professional quality with budget consciousness",
            modes={
                "default": "gemini-2.5-flash",
                "orchestrator": "gpt-5-mini",
                "architect": "qwen3-coder",
                "code": "grok-code-fast-1",
                "debug": "claude-haiku-4.5",
                "ask": "deepseek-v3.2-exp",
                "administrator": "minimax-m2"
            }
        )
    }

def load_profiles_from_file(path: str) -> Dict[str, ModeCombinationProfile]:
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    return {k: ModeCombinationProfile(**v) for k, v in data.items()}

def save_profiles_to_file(profiles: Dict[str, ModeCombinationProfile], path: str) -> None:
    p = Path(path)
    p.write_text(json.dumps({k: asdict(v) for k, v in profiles.items()}, indent=2), encoding="utf-8")


def profiles_dir_candidates() -> list[str]:
    """Return candidate directories for profiles in priority order.

    Priority order:
    1. KILOMOCO_PROFILES_DIR environment variable (if set)
    2. ./profiles subdirectory in current working directory
    3. ~/.kilomoco/profiles user config directory

    Only returns directories that exist.
    """
    candidates = []

    # 1. Environment variable
    env_dir = os.getenv("KILOMOCO_PROFILES_DIR")
    if env_dir and Path(env_dir).exists():
        candidates.append(env_dir)

    # 2. ./profiles
    cwd_profiles = Path.cwd() / "profiles"
    if cwd_profiles.exists():
        candidates.append(str(cwd_profiles))

    # 3. ~/.kilomoco/profiles
    user_profiles = Path.home() / ".kilomoco" / "profiles"
    if user_profiles.exists():
        candidates.append(str(user_profiles))

    return candidates


def load_profiles_from_dir(path: str) -> Dict[str, ModeCombinationProfile]:
    """Load profiles from YAML files in the specified directory.

    Parses each .yml/.yaml file in the directory. Expected YAML structure:
    - id (optional): profile ID, defaults to filename stem
    - name (optional): profile name
    - description (optional): profile description
    - modes: mapping of mode_name -> model_name (required)

    Skips files with invalid structure (missing or invalid 'modes' key) with a warning.
    Returns a dict keyed by profile.id.
    """
    profiles = {}
    dir_path = Path(path)

    for yaml_file in dir_path.glob("*.yml"):
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or "modes" not in data or not isinstance(data["modes"], dict):
                warnings.warn(f"Skipping invalid profile file {yaml_file}: missing or invalid 'modes' key")
                continue

            profile_id = data.get("id", yaml_file.stem)
            profile = ModeCombinationProfile(
                id=profile_id,
                name=data.get("name", profile_id),
                description=data.get("description", ""),
                modes=data["modes"]
            )
            profiles[profile.id] = profile
        except Exception as e:
            warnings.warn(f"Error loading profile from {yaml_file}: {e}")
            continue

    # Also check .yaml files
    for yaml_file in dir_path.glob("*.yaml"):
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or "modes" not in data or not isinstance(data["modes"], dict):
                warnings.warn(f"Skipping invalid profile file {yaml_file}: missing or invalid 'modes' key")
                continue

            profile_id = data.get("id", yaml_file.stem)
            profile = ModeCombinationProfile(
                id=profile_id,
                name=data.get("name", profile_id),
                description=data.get("description", ""),
                modes=data["modes"]
            )
            profiles[profile.id] = profile
        except Exception as e:
            warnings.warn(f"Error loading profile from {yaml_file}: {e}")
            continue

    return profiles


def discover_profiles() -> Dict[str, ModeCombinationProfile]:
    """Discover profiles from YAML files in candidate directories.

    Iterates over profiles_dir_candidates() and loads profiles from each directory.
    Later directories override earlier ones if they have the same profile ID.
    If no YAML profiles are found, returns an empty dict.
    """
    all_profiles = {}
    for dir_path in profiles_dir_candidates():
        dir_profiles = load_profiles_from_dir(dir_path)
        all_profiles.update(dir_profiles)
    return all_profiles