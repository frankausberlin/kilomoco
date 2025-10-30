"""Tests for YAML-based profile loading."""
import tempfile
import warnings
from pathlib import Path
from unittest.mock import patch

import pytest

from kilomoco.config import (
    ModeCombinationProfile,
    load_profiles_from_dir,
    discover_profiles,
    default_profiles,
    profiles_dir_candidates,
)


def test_load_profiles_from_dir_success():
    """Test loading profiles from a directory with valid YAML files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a sample YAML file
        yaml_content = """
id: lopr
name: Low-Price (Economy)
description: Budget-friendly...
modes:
  default: llama-4-maverick
  orchestrator: deepseek-v3.2-exp
"""
        yaml_file = Path(temp_dir) / "lopr.yaml"
        yaml_file.write_text(yaml_content)

        profiles = load_profiles_from_dir(temp_dir)

        assert "lopr" in profiles
        profile = profiles["lopr"]
        assert isinstance(profile, ModeCombinationProfile)
        assert profile.id == "lopr"
        assert profile.name == "Low-Price (Economy)"
        assert profile.description == "Budget-friendly..."
        assert profile.modes["default"] == "llama-4-maverick"
        assert profile.modes["orchestrator"] == "deepseek-v3.2-exp"


def test_discover_profiles_env_var_priority():
    """Test that KILOMOCO_PROFILES_DIR takes priority."""
    with tempfile.TemporaryDirectory() as temp_env_dir, \
         tempfile.TemporaryDirectory() as temp_cwd_dir:

        # Create profile in env var directory
        yaml_content = """
id: test_profile
name: Test Profile
description: Test description
modes:
  default: test-model
"""
        env_yaml_file = Path(temp_env_dir) / "test_profile.yaml"
        env_yaml_file.write_text(yaml_content)

        # Mock environment variable and cwd profiles
        with patch.dict("os.environ", {"KILOMOCO_PROFILES_DIR": temp_env_dir}), \
             patch("pathlib.Path.cwd") as mock_cwd, \
             patch("pathlib.Path.home") as mock_home:

            mock_cwd.return_value = Path(temp_cwd_dir)
            mock_home.return_value = Path("/tmp")  # Non-existent

            profiles = discover_profiles()

            assert "test_profile" in profiles
            assert profiles["test_profile"].id == "test_profile"


def test_invalid_yaml_is_skipped():
    """Test that invalid YAML files are skipped with warnings."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create invalid YAML (missing modes)
        invalid_yaml = """
id: invalid
name: Invalid Profile
"""
        invalid_file = Path(temp_dir) / "invalid.yaml"
        invalid_file.write_text(invalid_yaml)

        # Create valid YAML
        valid_yaml = """
id: valid
name: Valid Profile
modes:
  default: valid-model
"""
        valid_file = Path(temp_dir) / "valid.yaml"
        valid_file.write_text(valid_yaml)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            profiles = load_profiles_from_dir(temp_dir)

            # Should have warning for invalid file
            assert len(w) == 1
            assert "Skipping invalid profile file" in str(w[0].message)

            # Should only load valid profile
            assert "valid" in profiles
            assert "invalid" not in profiles


def test_default_profiles_fallback_to_builtin_when_no_yaml():
    """Test that default_profiles falls back to builtin when no YAML found."""
    # Mock no directories exist
    with patch("kilomoco.config.profiles_dir_candidates", return_value=[]):
        profiles = default_profiles()

        # Should return builtin profiles
        assert "lopr" in profiles
        assert "copr" in profiles
        assert isinstance(profiles["lopr"], ModeCombinationProfile)


def test_profiles_dir_candidates():
    """Test profiles_dir_candidates returns correct order."""
    with tempfile.TemporaryDirectory() as temp_env, \
         tempfile.TemporaryDirectory() as temp_cwd, \
         tempfile.TemporaryDirectory() as temp_home_base:

        temp_home = Path(temp_home_base) / "user"
        temp_home_profiles = temp_home / ".kilomoco" / "profiles"
        temp_home_profiles.mkdir(parents=True, exist_ok=True)

        with patch.dict("os.environ", {"KILOMOCO_PROFILES_DIR": temp_env}), \
             patch("pathlib.Path.cwd") as mock_cwd, \
             patch("pathlib.Path.home") as mock_home:

            mock_cwd.return_value = Path(temp_cwd)
            mock_home.return_value = temp_home

            # Create the directories
            Path(temp_env).mkdir(exist_ok=True)
            Path(temp_cwd).mkdir(exist_ok=True)

            candidates = profiles_dir_candidates()

            # Should include env and home, but cwd only if profiles subdir exists
            assert temp_env in candidates
            assert str(temp_home_profiles) in candidates

            # Since we created temp_cwd but not temp_cwd/profiles, it shouldn't be included
            # The function checks if cwd_profiles.exists(), and we didn't create it
            assert len(candidates) == 2  # Only env and home

            # Check order: env first, then home (cwd not included since profiles doesn't exist)
            env_idx = candidates.index(temp_env)
            home_idx = candidates.index(str(temp_home_profiles))
            assert env_idx < home_idx