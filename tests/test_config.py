import pathlib
from kilomoco.config import default_profiles

def test_default_profiles_contains_required_modes():
    profiles = default_profiles()
    for mode in ["Default", "Ask", "Code", "Debug", "Architect", "Orchestrator", "Administrator"]:
        assert mode in profiles