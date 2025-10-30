"""Minimal CLI scaffolding for kilomoco.

This file must provide a stable `main(argv=None)` entrypoint suitable for testing
and for use as the console script specified in pyproject.toml.
"""
import argparse
import sys
from .config import default_profiles

def build_parser():
    parser = argparse.ArgumentParser(prog="kilomoco", description="Kilomoco - manage kilo VS Code extension mode configurations")
    parser.add_argument("--list", action="store_true", help="List available profiles")
    parser.add_argument("--profile", type=str, help="Name of profile to apply (placeholder)")
    parser.add_argument("--workspace", type=str, help="Path to workspace (optional; placeholder for future use)")
    return parser

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list:
        profiles = default_profiles()
        for profile_id in sorted(profiles.keys()):
            profile = profiles[profile_id]
            print(f"{profile_id}: {profile.name} - {profile.description}")
        return 0
    elif args.profile:
        # Launch with specified profile
        from .launcher import prepare_and_launch
        try:
            return prepare_and_launch(args.profile, workspace=args.workspace)
        except (ValueError, RuntimeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    # Placeholder for interactive TUI
    print("kilomoco: interactive TUI not yet implemented. Use --list to see profiles or --profile <id> to launch with a specific profile.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())