"""Configuration management for the UE5 AI Assistant backend."""
import json
from pathlib import Path
from typing import Any, Dict

CONFIG_FILE = Path("app/data/config.json")

# Response style presets with intelligent filtering and output control
RESPONSE_STYLES = {
    "descriptive": {
        "name": "Descriptive (Default)",
        "prompt_modifier": "Provide clear, descriptive technical prose that explains what you see in the viewport. Be factual and specific.",
        "max_tokens": 400,
        "data_filter": "standard",
        "focus": "balanced_overview"
    },
    "technical": {
        "name": "Technical/Precise",
        "prompt_modifier": "Use precise technical terminology with exact coordinates, transforms, and specifications. Structure as technical documentation with subsections.",
        "max_tokens": 500,
        "data_filter": "technical",
        "focus": "precision_and_specs"
    },
    "natural": {
        "name": "Natural/Conversational",
        "prompt_modifier": "Respond conversationally as if describing the scene to a colleague. Focus on what's interesting or notable. Skip mundane details.",
        "max_tokens": 300,
        "data_filter": "highlights",
        "focus": "notable_elements"
    },
    "balanced": {
        "name": "Balanced",
        "prompt_modifier": "Balance technical accuracy with readability. Mention key actors and layout, skip repetitive details.",
        "max_tokens": 350,
        "data_filter": "balanced",
        "focus": "key_elements_summary"
    },
    "concise": {
        "name": "Concise/Brief",
        "prompt_modifier": "Be extremely brief. One short paragraph maximum. Only essential information: camera position, selected objects, major scene elements.",
        "max_tokens": 150,
        "data_filter": "minimal",
        "focus": "essentials_only"
    },
    "detailed": {
        "name": "Detailed/Verbose",
        "prompt_modifier": "Provide comprehensive, exhaustive analysis of all viewport elements. Include all actors, lighting setup, environment config, and spatial relationships.",
        "max_tokens": 800,
        "data_filter": "complete",
        "focus": "comprehensive_analysis"
    },
    "creative": {
        "name": "Creative/Imaginative",
        "prompt_modifier": "Paint a vivid picture using creative language and imagery. Help visualize the scene with descriptive metaphors, sensory details, and spatial storytelling. Structure as flowing narrative paragraphs that bring the viewport to life.",
        "max_tokens": 450,
        "temperature_override": 0.9,
        "data_filter": "standard",
        "focus": "visual_narrative"
    }
}

DEFAULT_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_context_turns": 6,
    "timeout": 25,
    "max_retries": 3,
    "retry_delay": 2.5,
    "verbose": False,
    "response_style": "descriptive"
}


def load_config() -> Dict[str, Any]:
    """Load configuration from file or use defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return {**DEFAULT_CONFIG, **config}
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")
