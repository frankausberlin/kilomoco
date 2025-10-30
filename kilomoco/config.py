"""Configuration model and simple persistence helpers for kilomoco."""
from dataclasses import dataclass, asdict
from typing import Dict, Optional
import json
from pathlib import Path

@dataclass
class ModeProfile:
    name: str
    model: Optional[str] = None
    prompt: Optional[str] = None
    settings: Dict = None

def default_profiles() -> Dict[str, ModeProfile]:
    names = ["Default", "Ask", "Code", "Debug", "Architect", "Orchestrator", "Administrator"]
    return {n: ModeProfile(name=n, settings={}) for n in names}

def load_profiles_from_file(path: str) -> Dict[str, ModeProfile]:
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    return {k: ModeProfile(**v) for k, v in data.items()}

def save_profiles_to_file(profiles: Dict[str, ModeProfile], path: str) -> None:
    p = Path(path)
    p.write_text(json.dumps({k: asdict(v) for k, v in profiles.items()}, indent=2), encoding="utf-8")