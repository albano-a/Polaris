from __future__ import annotations

from pathlib import Path

from polaris_core.config import ConfigStore, PolarisConfig
from polaris_core.context import ContextProvider, StaticContextProvider, geophysics_profile
from polaris_core.model_registry import ModelInfo, fetch_live_models, list_models
from polaris_core.models import AssistantProfile
from polaris_core.providers import LLMProvider, LiteLLMProvider
from polaris_core.retrieval import LocalRetriever
from polaris_core.service import PolarisService


def create_model(
    model: str,
    api_key: str | None = None,
    temperature: float = 0.2,
) -> LiteLLMProvider:
    """Create a LiteLLM-backed provider from an explicit model and optional API key."""
    return LiteLLMProvider(model=model, api_key=api_key, temperature=temperature)


def create_gemini_model(
    api_key: str | None = None,
    model: str = "gemini/gemini-2.5-flash",
    temperature: float = 0.2,
) -> LiteLLMProvider:
    """Create a Gemini provider using LiteLLM model naming."""
    return create_model(model=model, api_key=api_key, temperature=temperature)


def create_model_from_config(config: PolarisConfig | None = None) -> LiteLLMProvider:
    """Create a provider using saved config and environment variable overrides."""
    return LiteLLMProvider.from_config(config)


def save_model_config(
    model: str,
    api_key: str,
    provider: str = "gemini",
    config_path: str | Path | None = None,
) -> PolarisConfig:
    """Persist provider, model, and API key for later CLI or library use."""
    return ConfigStore(config_path).update(
        provider=provider,
        model=model,
        api_key=api_key,
    )


def create_service(
    model: str | None = None,
    api_key: str | None = None,
    provider: LLMProvider | None = None,
    profile: AssistantProfile | None = None,
    context_provider: ContextProvider | None = None,
    docs_path: str | Path | None = None,
    temperature: float = 0.2,
) -> PolarisService:
    """Create a ready-to-use PolarisService with explicit args or saved config."""
    selected_provider = provider
    if selected_provider is None:
        selected_provider = (
            create_model(model=model, api_key=api_key, temperature=temperature)
            if model
            else create_model_from_config()
        )
    retriever = LocalRetriever.from_directory(docs_path) if docs_path else None
    return PolarisService(
        provider=selected_provider,
        profile=profile or geophysics_profile(),
        context_provider=context_provider or StaticContextProvider(),
        retriever=retriever,
    )


def list_available_models(provider: str | None = "gemini") -> tuple[ModelInfo, ...]:
    """List PolarisCore's built-in model suggestions."""
    return list_models(provider)


def list_live_models(provider: str, api_key: str) -> tuple[ModelInfo, ...]:
    """List provider models from the provider API when supported."""
    return fetch_live_models(provider, api_key)
