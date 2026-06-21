from __future__ import annotations

from pathlib import Path

from polaris_core.chat.context import ContextProvider, StaticContextProvider
from polaris_core.chat.profiles import geophysics_profile
from polaris_core.chat.service import PolarisService
from polaris_core.config import ConfigStore, PolarisConfig
from polaris_core.llm.providers import LLMProvider, LiteLLMProvider
from polaris_core.llm.registry import ModelInfo, default_model_for, fetch_live_models, list_models
from polaris_core.models import AssistantProfile
from polaris_core.retrieval import LocalRetriever


def create_model(
    model: str | None = None,
    api_key: str | None = None,
    provider: str = "google",
    temperature: float = 0.2,
) -> LiteLLMProvider:
    """Create a LiteLLM-backed provider from an explicit model and optional API key."""
    return LiteLLMProvider(
        model=model or default_model_for(provider),
        api_key=api_key,
        temperature=temperature,
    )


def create_google_model(
    api_key: str | None = None,
    model: str = "gemini/gemini-2.5-flash",
    temperature: float = 0.2,
) -> LiteLLMProvider:
    """Create a Google Gemini provider using LiteLLM model naming."""
    return create_model(model=model, api_key=api_key, provider="google", temperature=temperature)


def create_gemini_model(
    api_key: str | None = None,
    model: str = "gemini/gemini-2.5-flash",
    temperature: float = 0.2,
) -> LiteLLMProvider:
    """Alias for create_google_model."""
    return create_google_model(api_key=api_key, model=model, temperature=temperature)


def create_openai_model(
    api_key: str | None = None,
    model: str = "openai/gpt-4o-mini",
    temperature: float = 0.2,
) -> LiteLLMProvider:
    """Create an OpenAI provider using LiteLLM model naming."""
    return create_model(model=model, api_key=api_key, provider="openai", temperature=temperature)


def create_anthropic_model(
    api_key: str | None = None,
    model: str = "anthropic/claude-sonnet-4-5",
    temperature: float = 0.2,
) -> LiteLLMProvider:
    """Create an Anthropic provider using LiteLLM model naming."""
    return create_model(model=model, api_key=api_key, provider="anthropic", temperature=temperature)


def create_deepseek_model(
    api_key: str | None = None,
    model: str = "deepseek/deepseek-chat",
    temperature: float = 0.2,
) -> LiteLLMProvider:
    """Create a DeepSeek provider using LiteLLM model naming."""
    return create_model(model=model, api_key=api_key, provider="deepseek", temperature=temperature)


def create_model_from_config(config: PolarisConfig | None = None) -> LiteLLMProvider:
    """Create a provider using saved config and environment variable overrides."""
    return LiteLLMProvider.from_config(config)


def save_model_config(
    model: str,
    api_key: str,
    provider: str = "google",
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
    model_provider: str = "google",
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
            create_model(
                model=model,
                api_key=api_key,
                provider=model_provider,
                temperature=temperature,
            )
            if model or api_key
            else create_model_from_config()
        )
    retriever = LocalRetriever.from_path(docs_path) if docs_path else None
    return PolarisService(
        provider=selected_provider,
        profile=profile or geophysics_profile(),
        context_provider=context_provider or StaticContextProvider(),
        retriever=retriever,
    )


def list_available_models(provider: str | None = None) -> tuple[ModelInfo, ...]:
    """List PolarisCore's built-in model suggestions."""
    return list_models(provider)


def list_live_models(provider: str, api_key: str) -> tuple[ModelInfo, ...]:
    """List provider models from the provider API when supported."""
    return fetch_live_models(provider, api_key)
