from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from getpass import getpass
from pathlib import Path
from typing import Any

from polaris_core.llm.registry import default_model_for, normalize_provider


API_KEY_ENV_VARS = {
    "google": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


@dataclass(frozen=True)
class PolarisConfig:
    provider: str = "google"
    model: str = "gemini/gemini-2.5-flash"
    api_keys: dict[str, str] = field(default_factory=dict)

    def api_key_for(self, provider: str | None = None) -> str | None:
        provider_name = normalize_provider(provider or self.provider)
        env_name = API_KEY_ENV_VARS.get(provider_name)
        if env_name and os.getenv(env_name):
            return os.getenv(env_name)
        return self.api_keys.get(provider_name)


class ConfigStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else default_config_path()

    def load(self) -> PolarisConfig:
        if not self.path.exists():
            return PolarisConfig()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        provider = normalize_provider(data.get("provider", "google"))
        return PolarisConfig(
            provider=provider,
            model=data.get("model") or default_model_for(provider),
            api_keys=dict(data.get("api_keys", {})),
        )

    def save(self, config: PolarisConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(config)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def update(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ) -> PolarisConfig:
        current = self.load()
        provider_name = normalize_provider(provider or current.provider)
        selected_model = model or current.model or default_model_for(provider_name)
        api_keys = dict(current.api_keys)
        if api_key:
            api_keys[provider_name] = api_key
        config = PolarisConfig(
            provider=provider_name,
            model=selected_model,
            api_keys=api_keys,
        )
        self.save(config)
        return config


def default_config_path() -> Path:
    if os.name == "nt":
        root = Path(os.getenv("APPDATA") or Path.home() / "AppData" / "Roaming")
        return root / "PolarisCore" / "config.json"
    root = Path(os.getenv("XDG_CONFIG_HOME") or Path.home() / ".config")
    return root / "polaris-core" / "config.json"


def user_docs_dir() -> Path:
    if os.name == "nt":
        root = Path(os.getenv("APPDATA") or Path.home() / "AppData" / "Roaming")
        return root / "PolarisCore" / "docs"
    root = Path(os.getenv("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return root / "polaris-core" / "docs"


def configure_interactively(
    provider: str = "google",
    model: str | None = None,
    store: ConfigStore | None = None,
) -> PolarisConfig:
    selected_provider = normalize_provider(provider)
    selected_model = model or default_model_for(selected_provider)
    env_name = API_KEY_ENV_VARS.get(selected_provider, "API_KEY")
    api_key = getpass(f"{selected_provider} API key ({env_name}): ").strip()
    return (store or ConfigStore()).update(
        provider=selected_provider,
        model=selected_model,
        api_key=api_key,
    )


def config_summary(config: PolarisConfig) -> dict[str, Any]:
    provider = normalize_provider(config.provider)
    env_name = API_KEY_ENV_VARS.get(provider)
    has_env_key = bool(env_name and os.getenv(env_name))
    has_stored_key = bool(config.api_keys.get(provider))
    return {
        "provider": config.provider,
        "model": config.model,
        "config_path": str(default_config_path()),
        "api_key_env_var": env_name,
        "has_api_key": has_env_key or has_stored_key,
        "api_key_source": "environment" if has_env_key else "config" if has_stored_key else "missing",
    }
