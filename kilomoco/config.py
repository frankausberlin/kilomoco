"""Configuration model and simple persistence helpers for kilomoco."""
from dataclasses import dataclass, asdict
from typing import Dict, Optional
import json
from pathlib import Path

@dataclass
class ModeCombinationProfile:
    id: str
    name: str
    description: str
    modes: Dict[str, str]  # mode_name -> model_name

def default_profiles() -> Dict[str, ModeCombinationProfile]:
    """Return the default mode combination profiles from infos.txt."""
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