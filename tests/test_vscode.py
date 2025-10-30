import tempfile
import json
from pathlib import Path
import pytest
from kilomoco.vscode import (
    create_temporary_user_data_dir,
    generate_mode_settings,
    apply_mode_configuration,
    _write_json_atomically,
)
from kilomoco.config import ModeCombinationProfile

def test_create_temporary_user_data_dir():
    """Test temporary directory creation with custom prefix."""
    temp_dir = create_temporary_user_data_dir("test-prefix-")
    assert temp_dir.startswith("/tmp/test-prefix-")
    assert Path(temp_dir).exists()
    assert Path(temp_dir).is_dir()

def test_generate_mode_settings_basic():
    """Test basic mode settings generation for profile combination."""
    profile = ModeCombinationProfile(
        id="test",
        name="Test Profile",
        description="Test description",
        modes={
            "default": "gpt-4",
            "code": "claude-3",
            "debug": "gpt-3.5"
        }
    )
    settings = generate_mode_settings(profile)
    assert settings["kilo-code.default.model"] == "gpt-4"
    assert settings["kilo-code.code.model"] == "claude-3"
    assert settings["kilo-code.debug.model"] == "gpt-3.5"
    assert len(settings) == 3

def test_generate_mode_settings_full_profile():
    """Test settings generation with all 7 modes."""
    profile = ModeCombinationProfile(
        id="full",
        name="Full Profile",
        description="Complete profile",
        modes={
            "default": "model1",
            "orchestrator": "model2",
            "architect": "model3",
            "code": "model4",
            "debug": "model5",
            "ask": "model6",
            "administrator": "model7"
        }
    )
    settings = generate_mode_settings(profile)
    assert len(settings) == 7
    for mode in ["default", "orchestrator", "architect", "code", "debug", "ask", "administrator"]:
        assert f"kilo-code.{mode}.model" in settings
        assert settings[f"kilo-code.{mode}.model"] == f"model{['default', 'orchestrator', 'architect', 'code', 'debug', 'ask', 'administrator'].index(mode) + 1}"

def test_apply_mode_configuration_temp_user_data_dir():
    """Test applying configuration with temp user data dir strategy."""
    profile = ModeCombinationProfile(
        id="test",
        name="Test Profile",
        description="Test",
        modes={"default": "gpt-4", "code": "claude-3"}
    )
    temp_dir = apply_mode_configuration(profile, strategy="temp_user_data_dir")

    # Check directory structure
    user_dir = Path(temp_dir) / "User"
    assert user_dir.exists()
    assert user_dir.is_dir()

    # Check settings.json content
    settings_file = user_dir / "settings.json"
    assert settings_file.exists()

    with open(settings_file, 'r', encoding='utf-8') as f:
        settings = json.load(f)

    assert settings["kilo-code.default.model"] == "gpt-4"
    assert settings["kilo-code.code.model"] == "claude-3"

def test_apply_mode_configuration_unsupported_strategy():
    """Test that unsupported strategies raise ValueError."""
    profile = ModeCombinationProfile(
        id="test",
        name="Test",
        description="Test",
        modes={"default": "gpt-4"}
    )
    with pytest.raises(ValueError, match="Unsupported strategy"):
        apply_mode_configuration(profile, strategy="unsupported")

def test_write_json_atomically():
    """Test atomic JSON writing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "test.json"
        data = {"key": "value", "number": 42}

        _write_json_atomically(path, data)

        assert path.exists()
        with open(path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        assert loaded == data

def test_write_json_atomically_atomicity():
    """Test that atomic write doesn't leave partial files on failure."""
    # This is a basic test; in practice, we'd need to simulate filesystem errors
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "test.json"
        data = {"key": "value"}

        _write_json_atomically(path, data)
        assert path.exists()

        # Verify no .tmp file remains
        tmp_file = path.with_suffix('.tmp')
        assert not tmp_file.exists()