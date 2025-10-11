"""
Configuration management for UE5 AI Assistant.
Handles settings, API endpoints, and user preferences.
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import unreal  # type: ignore
    HAS_UNREAL = True
except ImportError:
    HAS_UNREAL = False
    unreal = None  # type: ignore  # Only available in UE environment


class Config:
    """Manages configuration settings with file persistence."""

    # Response style presets (synced with backend v3.0)
    RESPONSE_STYLES = {
        "descriptive": {
            "name": "Descriptive (Default)",
            "description": "Clear, factual technical prose with balanced detail",
            "max_tokens": 400,
            "data_filter": "standard",
            "focus": "balanced_overview"
        },
        "technical": {
            "name": "Technical/Precise",
            "description": "Precise specs with exact coordinates and technical documentation format",
            "max_tokens": 500,
            "data_filter": "technical",
            "focus": "precision_and_specs"
        },
        "natural": {
            "name": "Natural/Conversational",
            "description": "Conversational tone, focuses on notable elements only",
            "max_tokens": 300,
            "data_filter": "highlights",
            "focus": "notable_elements"
        },
        "balanced": {
            "name": "Balanced",
            "description": "Technical accuracy with readability, skips repetitive details",
            "max_tokens": 350,
            "data_filter": "balanced",
            "focus": "key_elements_summary"
        },
        "concise": {
            "name": "Concise/Brief",
            "description": "Extremely brief, one short paragraph with essentials only",
            "max_tokens": 150,
            "data_filter": "minimal",
            "focus": "essentials_only"
        },
        "detailed": {
            "name": "Detailed/Verbose",
            "description": "Comprehensive exhaustive analysis of all elements",
            "max_tokens": 800,
            "data_filter": "complete",
            "focus": "comprehensive_analysis"
        },
        "creative": {
            "name": "Creative/Imaginative",
            "description": "Vivid imagery and narrative storytelling to visualize the scene",
            "max_tokens": 450,
            "temperature_override": 0.9,
            "data_filter": "standard",
            "focus": "visual_narrative"
        }
    }

    DEFAULT_CONFIG = {
        "api_base_url": (
            "https://ue5-assistant-noahbutcher97.replit.app"),
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "response_style": "descriptive",
        "max_retries": 3,
        "retry_delay": 2.5,
        "timeout": 25,
        "enable_context_caching": True,
        "cache_duration": 30,
        "verbose_logging": False,
        "enable_confirmations": True,
        "max_context_turns": 6,
        "collect_project_metadata": True,  # NEW: Enable project context collection
    }

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config, loading from file if it exists."""
        if config_path is None and HAS_UNREAL and unreal is not None:
            # unreal is available here (UE environment only)
            saved_dir = Path(
                unreal.Paths.project_saved_dir()  # type: ignore[union-attr]
            )
            config_path = saved_dir / "AIConsole" / "config.json"

        self.config_path = config_path
        self.settings: Dict[str, Any] = self.DEFAULT_CONFIG.copy()

        if config_path and config_path.exists():
            self.load()
        elif config_path:
            self.save()

    def load(self) -> None:
        """Load configuration from JSON file."""
        try:
            if self.config_path and self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
        except Exception as e:
            print(f"[Config] Failed to load config: {e}")

    def save(self) -> None:
        """Save current configuration to JSON file."""
        try:
            if self.config_path:
                self.config_path.parent.mkdir(
                    parents=True, exist_ok=True)
                with open(
                    self.config_path, "w", encoding="utf-8"
                ) as f:
                    json.dump(
                        self.settings, f, indent=2, ensure_ascii=False
                    )
        except Exception as e:
            print(f"[Config] Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save."""
        self.settings[key] = value
        self.save()

    @property
    def api_url(self) -> str:
        """Get the API base URL."""
        return self.get("api_base_url", "")

    @property
    def execute_endpoint(self) -> str:
        """Get the execute command endpoint."""
        return f"{self.api_url}/execute_command"

    @property
    def describe_endpoint(self) -> str:
        """Get the describe viewport endpoint."""
        return f"{self.api_url}/describe_viewport"

    @property
    def verbose(self) -> bool:
        """Check if verbose logging is enabled."""
        return self.get("verbose_logging", False)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
