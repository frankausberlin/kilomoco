"""Tests for TUI components."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from kilomoco.tui import ProfileList, ProfileDetails, InstanceInfo, MainScreen, KiloMocoTUI
from kilomoco.config import ModeCombinationProfile

pytestmark = pytest.mark.asyncio


@pytest.fixture
def sample_profiles():
    """Sample profiles for testing."""
    return {
        "test1": ModeCombinationProfile(
            id="test1",
            name="Test Profile 1",
            description="First test profile",
            modes={"default": "model1", "code": "model2"}
        ),
        "test2": ModeCombinationProfile(
            id="test2",
            name="Test Profile 2",
            description="Second test profile",
            modes={"default": "model3", "debug": "model4"}
        )
    }


class TestProfileList:
    """Test ProfileList widget."""

    def test_compose(self, sample_profiles):
        """Test that ProfileList composes correctly."""
        list_widget = ProfileList(sample_profiles)
        items = list(list_widget.compose())

        assert len(items) == 2
        # Check that the labels contain the expected text
        assert hasattr(items[0], 'label')
        assert hasattr(items[1], 'label')
        assert "test1" in str(items[0])
        assert "Test Profile 1" in str(items[0])
        assert "test2" in str(items[1])
        assert "Test Profile 2" in str(items[1])


class TestProfileDetails:
    """Test ProfileDetails widget."""

    def test_update_profile_with_profile(self, sample_profiles):
        """Test updating profile details with a valid profile."""
        details = ProfileDetails()
        profile = sample_profiles["test1"]

        details.update_profile(profile)

        # Check that the profile was stored
        assert details.current_profile == profile

    def test_update_profile_with_none(self):
        """Test updating profile details with None."""
        details = ProfileDetails()
        details.update_profile(None)

        # Check that the profile was set to None
        assert details.current_profile is None


class TestInstanceInfo:
    """Test InstanceInfo widget."""

    def test_update_instances_with_instances(self):
        """Test updating instance info with instances."""
        info = InstanceInfo()
        instances = [
            {"workspace": "/path/to/workspace", "user_data_dir": "/tmp/user-data", "has_kilo": True, "pid": 1234},
            {"workspace": None, "user_data_dir": "/tmp/user-data2", "has_kilo": True, "pid": 5678}
        ]

        info.update_instances(instances)

        # Check that instances were stored
        assert len(info.instances) == 2
        assert info.instances[0]["workspace"] == "/path/to/workspace"
        assert info.instances[1]["workspace"] is None

    def test_update_instances_empty(self):
        """Test updating instance info with no instances."""
        info = InstanceInfo()
        info.update_instances([])

        # Check that instances were stored as empty list
        assert len(info.instances) == 0


class TestMainScreen:
    """Test MainScreen."""

    @patch('kilomoco.tui.detect_vscode_instances')
    @patch('kilomoco.tui.get_current_profile_from_instance')
    def test_refresh_instances(self, mock_get_profile, mock_detect, sample_profiles):
        """Test instance refresh functionality."""
        mock_detect.return_value = []
        mock_get_profile.return_value = None

        with patch('kilomoco.tui.default_profiles', return_value=sample_profiles):
            screen = MainScreen()
            screen.refresh_instances()

            mock_detect.assert_called_once()

    @patch('kilomoco.tui.prepare_and_launch')
    async def test_launch_profile_success(self, mock_launch):
        """Test successful profile launch."""
        mock_launch.return_value = 0

        screen = MainScreen()
        await screen.launch_profile("test_profile")

        mock_launch.assert_called_once_with("test_profile")

    @patch('kilomoco.tui.prepare_and_launch')
    async def test_launch_profile_error(self, mock_launch):
        """Test profile launch with error."""
        mock_launch.side_effect = ValueError("Profile not found")

        screen = MainScreen()
        
        # Test that the exception is properly raised
        with pytest.raises(ValueError, match="Profile not found"):
            await screen.launch_profile("invalid_profile")

        mock_launch.assert_called_once_with("invalid_profile")


class TestKiloMocoTUI:
    """Test main TUI application."""

    @patch('kilomoco.tui.check_vscode_available')
    @patch('kilomoco.tui.Path.home')
    def test_on_mount_vscode_available(self, mock_home, mock_check_vscode):
        """Test app mounting when VS Code is available."""
        mock_check_vscode.return_value = True
        mock_home.return_value = Path("/home/user")

        # Mock extension directory check
        with patch('pathlib.Path.exists', return_value=True):
            app = KiloMocoTUI()
            app.on_mount()  # Should not exit

    @patch('kilomoco.tui.check_vscode_available')
    def test_on_mount_vscode_not_available(self, mock_check_vscode):
        """Test app mounting when VS Code is not available."""
        mock_check_vscode.return_value = False

        app = KiloMocoTUI()
        with patch.object(app, 'exit') as mock_exit:
            app.on_mount()
            mock_exit.assert_called_once_with("VS Code CLI ('code') not found in PATH. Please ensure VS Code is installed.")