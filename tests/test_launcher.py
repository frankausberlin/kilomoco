import pytest
from unittest.mock import patch, MagicMock
from kilomoco.launcher import check_vscode_available, prepare_and_launch
from kilomoco.config import ModeProfile

def test_check_vscode_available_true():
    """Test VS Code availability check when code is in PATH."""
    with patch('shutil.which', return_value='/usr/bin/code'):
        assert check_vscode_available() is True

def test_check_vscode_available_false():
    """Test VS Code availability check when code is not in PATH."""
    with patch('shutil.which', return_value=None):
        assert check_vscode_available() is False

def test_prepare_and_launch_invalid_profile():
    """Test error handling for invalid profile name."""
    with patch('kilomoco.launcher.check_vscode_available', return_value=True):
        with pytest.raises(ValueError, match="Profile 'invalid' not found"):
            prepare_and_launch("invalid")

def test_prepare_and_launch_vscode_not_available():
    """Test error handling when VS Code CLI is not available."""
    with patch('kilomoco.launcher.check_vscode_available', return_value=False):
        with pytest.raises(RuntimeError, match="VS Code CLI.*not found"):
            prepare_and_launch("Code")

@patch('kilomoco.launcher.launch_vscode_with_profile')
@patch('kilomoco.launcher.apply_mode_configuration')
@patch('kilomoco.launcher.check_vscode_available', return_value=True)
def test_prepare_and_launch_success(mock_check, mock_apply, mock_launch):
    """Test successful profile application and launch."""
    mock_apply.return_value = "/tmp/test-dir"
    mock_launch.return_value = 0

    result = prepare_and_launch("Code")

    assert result == 0
    mock_apply.assert_called_once()
    mock_launch.assert_called_once_with("/tmp/test-dir", workspace=None)

@patch('kilomoco.launcher.launch_vscode_with_profile')
@patch('kilomoco.launcher.apply_mode_configuration')
@patch('kilomoco.launcher.check_vscode_available', return_value=True)
def test_prepare_and_launch_with_workspace(mock_check, mock_apply, mock_launch):
    """Test launch with workspace parameter."""
    mock_apply.return_value = "/tmp/test-dir"
    mock_launch.return_value = 0

    result = prepare_and_launch("Code", workspace="/path/to/workspace")

    assert result == 0
    mock_launch.assert_called_once_with("/tmp/test-dir", workspace="/path/to/workspace")

@patch('shutil.rmtree')
@patch('kilomoco.launcher.launch_vscode_with_profile', side_effect=Exception("Launch failed"))
@patch('kilomoco.launcher.apply_mode_configuration')
@patch('kilomoco.launcher.check_vscode_available', return_value=True)
def test_prepare_and_launch_cleanup_on_error(mock_check, mock_apply, mock_launch, mock_rmtree):
    """Test that temp directory is cleaned up when launch fails."""
    mock_apply.return_value = "/tmp/test-dir"

    with pytest.raises(Exception, match="Launch failed"):
        prepare_and_launch("Code")

    mock_rmtree.assert_called_once_with("/tmp/test-dir")

def test_cli_profile_argument(capsys):
    """Test CLI --profile argument integration."""
    import kilomoco.cli as cli

    with patch('kilomoco.launcher.prepare_and_launch', return_value=0) as mock_launch:
        rc = cli.main(["--profile", "Code"])
        assert rc == 0
        mock_launch.assert_called_once_with("Code", workspace=None)

def test_cli_profile_with_workspace(capsys):
    """Test CLI --profile with --workspace argument."""
    import kilomoco.cli as cli

    with patch('kilomoco.launcher.prepare_and_launch', return_value=0) as mock_launch:
        rc = cli.main(["--profile", "Code", "--workspace", "/test/workspace"])
        assert rc == 0
        mock_launch.assert_called_once_with("Code", workspace="/test/workspace")

def test_cli_profile_error_handling(capsys):
    """Test CLI error handling for invalid profile."""
    import kilomoco.cli as cli

    with patch('kilomoco.launcher.prepare_and_launch', side_effect=ValueError("Invalid profile")):
        rc = cli.main(["--profile", "Invalid"])
        assert rc == 1
        captured = capsys.readouterr()
        assert "Error: Invalid profile" in captured.err