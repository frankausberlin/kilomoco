import pathlib
from kilomoco.config import default_profiles

def test_default_profiles_contains_required_profiles():
    profiles = default_profiles()
    expected_ids = ["lopr", "copr", "hiq", "bas", "res", "ags", "refo", "buco"]
    for profile_id in expected_ids:
        assert profile_id in profiles
        profile = profiles[profile_id]
        assert hasattr(profile, 'id')
        assert hasattr(profile, 'name')
        assert hasattr(profile, 'description')
        assert hasattr(profile, 'modes')
        assert isinstance(profile.modes, dict)
        # Check that all required modes are present
        required_modes = ["default", "orchestrator", "architect", "code", "debug", "ask", "administrator"]
        for mode in required_modes:
            assert mode in profile.modes
            assert isinstance(profile.modes[mode], str)

def test_default_profiles_have_correct_structure():
    profiles = default_profiles()
    for profile_id, profile in profiles.items():
        assert profile.id == profile_id
        assert len(profile.name) > 0
        assert len(profile.description) > 0
        assert len(profile.modes) == 7  # All 7 modes should be defined