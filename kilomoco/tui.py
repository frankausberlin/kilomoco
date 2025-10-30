"""Textual-based TUI for profile selection and VS Code instance management."""

import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, Button
from textual.screen import Screen

from .config import default_profiles, ModeCombinationProfile
from .vscode import detect_vscode_instances, get_current_profile_from_instance
from .launcher import prepare_and_launch, check_vscode_available


class ProfileList(ListView):
    """List of available profiles."""

    def __init__(self, profiles: Dict[str, ModeCombinationProfile], **kwargs):
        super().__init__(**kwargs)
        self.profiles = profiles

    def compose(self) -> ComposeResult:
        for profile_id, profile in self.profiles.items():
            yield ListItem(Label(f"{profile_id}: {profile.name}"), id=f"profile-{profile_id}")


class ProfileDetails(Static):
    """Display details of selected profile."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_profile: Optional[ModeCombinationProfile] = None

    def update_profile(self, profile: Optional[ModeCombinationProfile]) -> None:
        """Update the displayed profile details."""
        self.current_profile = profile
        if profile:
            modes_text = "\n".join(f"  {mode}: {model}" for mode, model in profile.modes.items())
            content = f"""[bold]{profile.name}[/bold]

{profile.description}

[bold]Modes:[/bold]
{modes_text}"""
        else:
            content = "Select a profile to view details."
        self.update(content)


class InstanceInfo(Static):
    """Display information about running VS Code instances."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.instances = []

    def update_instances(self, instances: list) -> None:
        """Update the displayed instance information."""
        self.instances = instances
        if not instances:
            content = "No VS Code instances with kilo extension found."
        else:
            instance_lines = []
            for instance in instances:
                workspace = instance.get('workspace', 'N/A')
                profile = get_current_profile_from_instance(instance) or 'unknown'
                instance_lines.append(f"Workspace: {workspace} | Profile: {profile}")
            content = "\n".join(instance_lines)
        self.update(content)


class MainScreen(Screen):
    """Main TUI screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.profiles = default_profiles()
        self.instances = []

    def compose(self) -> ComposeResult:
        # Header with instance info
        yield Header()
        with Vertical():
            yield InstanceInfo(id="instance-info")
            with Horizontal():
                # Profile list (left)
                with Vertical():
                    yield Label("[bold]Profiles[/bold]")
                    yield ProfileList(self.profiles, id="profile-list")
                # Profile details (right)
                with Vertical():
                    yield Label("[bold]Profile Details[/bold]")
                    yield ProfileDetails(id="profile-details")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        self.refresh_instances()
        # Select first profile by default
        if self.profiles:
            first_profile = next(iter(self.profiles.values()))
            self.query_one(ProfileDetails).update_profile(first_profile)

    def refresh_instances(self) -> None:
        """Refresh the list of VS Code instances."""
        try:
            self.instances = detect_vscode_instances()
            self.query_one(InstanceInfo).update_instances(self.instances)
        except Exception as e:
            self.query_one(InstanceInfo).update(f"Error detecting instances: {e}")

    @on(ListView.Selected)
    def on_profile_selected(self, event: ListView.Selected) -> None:
        """Handle profile selection."""
        if event.item.id and event.item.id.startswith("profile-"):
            profile_id = event.item.id[8:]  # Remove "profile-" prefix
            profile = self.profiles.get(profile_id)
            if profile:
                self.query_one(ProfileDetails).update_profile(profile)

    async def key_enter(self) -> None:
        """Handle Enter key to launch selected profile."""
        profile_list = self.query_one("#profile-list", ProfileList)
        selected_item = profile_list.highlighted_child
        if selected_item and selected_item.id and selected_item.id.startswith("profile-"):
            profile_id = selected_item.id[8:]  # Remove "profile-" prefix
            await self.launch_profile(profile_id)

    async def launch_profile(self, profile_id: str) -> None:
        """Launch VS Code with the selected profile."""
        try:
            exit_code = prepare_and_launch(profile_id)
            self.notify(f"Successfully launched VS Code with profile '{profile_id}'", severity="information")
        except Exception as e:
            self.notify(f"Failed to launch profile '{profile_id}': {e}", severity="error")


class KiloMocoTUI(App):
    """Main TUI application."""

    CSS = """
    Screen {
        layout: vertical;
    }

    Header {
        height: 3;
        background: $primary;
        color: $text;
    }

    Footer {
        height: 3;
        background: $primary;
        color: $text;
    }

    #instance-info {
        height: 4;
        background: $secondary;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }

    Horizontal {
        height: 100%;
    }

    Vertical {
        width: 50%;
        height: 100%;
        padding: 1;
    }

    #profile-list {
        height: 100%;
        border: solid $primary;
    }

    #profile-details {
        height: 100%;
        border: solid $primary;
        padding: 1;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:hover {
        background: $accent;
    }

    ListItem:selected {
        background: $primary;
        color: $text;
    }
    """

    def on_mount(self) -> None:
        """Check prerequisites on startup."""
        if not check_vscode_available():
            self.exit("VS Code CLI ('code') not found in PATH. Please ensure VS Code is installed.")
            return

        # Check if kilo extension is available (look in common locations)
        kilo_found = False
        common_ext_dirs = [
            Path.home() / ".vscode" / "extensions",
            Path.home() / ".vscode-server" / "extensions",
        ]
        for ext_dir in common_ext_dirs:
            if (ext_dir / "kilocode.kilo-code").exists():
                kilo_found = True
                break

        if not kilo_found:
            self.notify(
                "Warning: kilo extension not found in common locations. "
                "Make sure it's installed for full functionality.",
                severity="warning"
            )

    def compose(self) -> ComposeResult:
        yield MainScreen()


def launch_tui() -> None:
    """Launch the TUI application."""
    app = KiloMocoTUI()
    app.run()