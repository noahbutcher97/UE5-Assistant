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

    DEFAULT_CONFIG = {
        "api_base_url": (
            "https://ue5-assistant-noahbutcher97.replit.app"),
        "model": "gpt-4o-mini",
        "max_retries": 3,
        "retry_delay": 2.5,
        "timeout": 25,
        "enable_context_caching": True,
        "cache_duration": 30,
        "verbose_logging": False,
        "enable_confirmations": True,
        "max_context_turns": 6,
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
